#!/usr/bin/env python
"""生成可订阅到 Apple 日历的 .ics 文件（中外节日）。

呈现口径：
  - 中国：农历节日 + 二十四节气 + 法定放假安排（🏖️ 休 / 💼 班 调休）
  - 外国：只显示节日本体（不含补休/振替），多日连休合并为一条

用法:
    python generate.py                        # 默认 2020-2040，输出到 docs/
    python generate.py --from-year 1900 --to-year 2099 --cn-only
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from calgen import china, world
from calgen.ical import Event, write_calendar

ROOT = Path(__file__).resolve().parent

BASE_TARGETS: dict[str, tuple[str, str, str]] = {
    "all.ics": (
        "中外节日 · 全部",
        "中国节日与法定放假安排 + 美国、英国、加拿大、澳大利亚、新加坡节日",
        "#FF9500",
    ),
    "cn.ics": (
        "中外节日 · 中国",
        "农历节日、二十四节气、法定放假与调休",
        "#FF3B30",
    ),
    "intl.ics": (
        "中外节日 · 国际",
        "美国、英国、加拿大、澳大利亚、新加坡",
        "#5AA9FF",
    ),
}

COUNTRY_COLORS = ["#5AA9FF", "#7B8CF5", "#4FB3BF", "#3FBF8F", "#C9A227"]


def load_overrides(path: Path | None) -> list[Event]:
    """读取中国法定放假安排（含调休），由 sync_holidays.py 自动维护。

    格式: {"2026-02-17": {"type": "休", "name": "春节"}, "2026-02-14": {"type": "班", "name": "春节"}}
    """
    if not path or not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[warn] 忽略无法解析的节假日文件 {path}: {exc}", file=sys.stderr)
        return []

    events: list[Event] = []
    for key, val in raw.items():
        if key.startswith("_"):
            continue  # 注释字段
        try:
            d = date.fromisoformat(key)
        except ValueError:
            print(f"[warn] 跳过非法日期 {key}", file=sys.stderr)
            continue
        if not isinstance(val, dict):
            val = {"type": str(val)}
        kind = str(val.get("type", "休"))
        name = str(val.get("name", "法定节假日"))
        rest = kind != "班"
        events.append(
            Event(
                day=d,
                key=f"stat-{kind}",
                summary=f"{'🏖️' if rest else '💼'} {kind} · {name}",
                category="🇨🇳 中国放假安排",
                description=f"国务院节假日安排：{key} {'放假' if rest else '调休上班'}（{name}）",
            )
        )
    return events


def dedupe(events: list[Event]) -> list[Event]:
    seen: dict[tuple[date, str], Event] = {}
    for ev in events:
        seen.setdefault((ev.day, ev.key), ev)
    return list(seen.values())


def main() -> int:
    ap = argparse.ArgumentParser(description="生成中外节日万年历 .ics")
    ap.add_argument("--from-year", type=int, default=2020)
    ap.add_argument("--to-year", type=int, default=2040)
    ap.add_argument("--out", default="docs")
    ap.add_argument("--site", default="https://caddaric9527.github.io/perpetual-calendar",
                    help="页面基址，用于 SOURCE 属性")
    ap.add_argument("--overrides", default=str(ROOT / "data" / "holidays_cn.json"),
                    help="中国法定放假安排 JSON")
    ap.add_argument("--no-terms", action="store_true", help="不包含二十四节气")
    ap.add_argument("--cn-only", action="store_true", help="只生成中国日历（可用 1900-2099）")
    args = ap.parse_args()

    if args.from_year > args.to_year:
        print("[error] 起始年份不能大于结束年份", file=sys.stderr)
        return 2
    if args.cn_only and not (1900 <= args.from_year <= 2099 and 1900 <= args.to_year <= 2099):
        print("[error] 中国日历年份需在 1900-2099 之间（农历数据范围）", file=sys.stderr)
        return 2

    out = Path(args.out)
    site = args.site.rstrip("/")
    fy, ty = args.from_year, args.to_year

    cn_events = china.build(fy, ty, include_terms=not args.no_terms)
    # 放假数据源可能覆盖更早年份，按生成范围裁剪
    stat_events = [
        ev for ev in load_overrides(Path(args.overrides)) if fy <= ev.day.year <= ty
    ]
    cn_all = dedupe(cn_events + stat_events)

    targets: dict[str, list[Event]] = {"cn.ics": cn_all}
    if args.cn_only:
        targets["all.ics"] = cn_all
    else:
        world_events = world.build_all(fy, ty)
        targets["all.ics"] = dedupe(cn_all + world_events)
        targets["intl.ics"] = dedupe(world_events)
        for country in world.COUNTRIES:
            targets[f"{country.cc}.ics"] = dedupe(world.build(country.cc, fy, ty))

    for filename, events in targets.items():
        if filename in BASE_TARGETS:
            calname, caldesc, color = BASE_TARGETS[filename]
        else:
            country = world.BY_CC[filename[:-4]]
            calname = f"中外节日 · {country.name}"
            caldesc = f"{country.name}公共节日（仅节日，不含补休）"
            color = COUNTRY_COLORS[world.COUNTRIES.index(country) % len(COUNTRY_COLORS)]

        count = write_calendar(
            events,
            out / filename,
            calname=calname,
            caldesc=caldesc,
            uid_domain="perpetual-calendar",
            color=color,
            source_url=f"{site}/{filename}",
        )
        size = (out / filename).stat().st_size / 1024
        print(f"✅ {filename:<9} {count:>5} 条  {size:>7.1f} KB  {calname}")

    span = f"{fy}-{ty}（{ty - fy + 1} 年）"
    print(f"📅 覆盖范围: {span}　输出目录: {out.resolve()}")
    if not args.cn_only:
        for country in world.COUNTRIES:
            cov = world.coverage(country.cc)
            if cov:
                print(f"   {country.flag} {country.name}: 数据 {cov[0]}-{cov[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
