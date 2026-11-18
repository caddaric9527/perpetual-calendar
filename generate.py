#!/usr/bin/env python
"""生成可订阅到 Apple 日历的 .ics 文件（中国节假日 + 全球通用节日）。

呈现口径：
  - 中国：农历节日 + 二十四节气 + 法定放假安排（🏖️ 休 / 💼 班 调休）
  - 全球：联合国核心国际日（🌍）+ 全球通行民间节日（🎉），纯规则推算，不依赖外部 API

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

from calgen import china, intl
from calgen.ical import Event, write_calendar

ROOT = Path(__file__).resolve().parent

BASE_TARGETS: dict[str, tuple[str, str, str]] = {
    "all.ics": (
        "万年历 · 中国节假日 + 全球节日",
        "中国节日、法定放假与调休 + 二十四节气 + 联合国国际日与全球民间节日",
        "#FF9500",
    ),
    "cn.ics": (
        "万年历 · 中国",
        "农历节日、二十四节气、法定放假与调休",
        "#FF3B30",
    ),
    "intl.ics": (
        "万年历 · 全球通用节日",
        "联合国核心国际日 + 全球通行民间节日（不含任何国家的休息日）",
        "#5AA9FF",
    ),
}


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


def drop_shadowed(cn_events: list[Event], intl_events: list[Event]) -> list[Event]:
    """合并日历里去掉与中国日历重复的同一节日（如元旦、情人节同日同名）。"""
    def name_of(ev: Event) -> str:
        return ev.summary.split(" ", 1)[-1]

    taken = {(ev.day, name_of(ev)) for ev in cn_events}
    return [ev for ev in intl_events if (ev.day, name_of(ev)) not in taken]


def main() -> int:
    ap = argparse.ArgumentParser(description="生成中国节假日 + 全球通用节日万年历 .ics")
    ap.add_argument("--from-year", type=int, default=2020)
    ap.add_argument("--to-year", type=int, default=2040)
    ap.add_argument("--out", default="docs")
    ap.add_argument("--site", default="https://caddaric9527.github.io/perpetual-calendar",
                    help="页面基址，用于 SOURCE 属性")
    ap.add_argument("--overrides", default=str(ROOT / "data" / "holidays_cn.json"),
                    help="中国法定放假安排 JSON")
    ap.add_argument("--no-terms", action="store_true", help="不包含二十四节气")
    ap.add_argument("--no-intl", action="store_true", help="不包含全球通用节日")
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
    if args.cn_only or args.no_intl:
        targets["all.ics"] = cn_all
    else:
        intl_events = dedupe(intl.build(fy, ty))
        targets["all.ics"] = dedupe(cn_all + drop_shadowed(cn_all, intl_events))
        targets["intl.ics"] = intl_events

    for filename, events in targets.items():
        calname, caldesc, color = BASE_TARGETS[filename]
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
    if not (args.cn_only or args.no_intl):
        catalog = intl.load()
        memorial = sum(1 for d in catalog if d.get("kind") == "memorial")
        print(f"   🌍 全球通用节日：{len(catalog)} 个（国际日 {memorial} + 民间 {len(catalog) - memorial}），纯规则推算")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
