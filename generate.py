#!/usr/bin/env python
"""生成可订阅到 Apple 日历的 .ics 文件。

用法:
    python generate.py                      # 默认 2020-2060，输出到 docs/
    python generate.py --from-year 1900 --to-year 2099
    python generate.py --out public --site https://example.github.io/repo
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from calgen import china, usa
from calgen.ical import Event, write_calendar

ROOT = Path(__file__).resolve().parent

TARGETS = {
    "all.ics": ("万年历 · 中美节日", "中国农历节日 + 二十四节气 + 美国法定/民间节日", "#FF9500"),
    "cn.ics": ("万年历 · 中国节日", "农历传统节日、公历纪念日、二十四节气", "#FF3B30"),
    "us.ics": ("万年历 · 美国节日", "美国联邦法定假日与常见民间节日", "#007AFF"),
}


def load_overrides(path: Path | None) -> list[Event]:
    """读取人工维护的法定节假日安排（含调休）。

    格式: {"2026-02-17": {"type": "休", "name": "春节假期"}, "2026-02-14": {"type": "班", "name": "调休上班"}}
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
                category="🇨🇳 中国法定节假日",
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
    ap = argparse.ArgumentParser(description="生成中美节日万年历 .ics")
    ap.add_argument("--from-year", type=int, default=2020)
    ap.add_argument("--to-year", type=int, default=2060)
    ap.add_argument("--out", default="docs")
    ap.add_argument("--site", default="https://caddaric9527.github.io/perpetual-calendar",
                    help="页面基址，用于 SOURCE 属性")
    ap.add_argument("--overrides", default=str(ROOT / "data" / "holidays_cn.json"),
                    help="中国法定节假日安排 JSON（可缺省）")
    ap.add_argument("--no-terms", action="store_true", help="不包含二十四节气")
    args = ap.parse_args()

    if not (1900 <= args.from_year <= 2099 and 1900 <= args.to_year <= 2099):
        print("[error] 年份需在 1900-2099 之间（农历数据范围）", file=sys.stderr)
        return 2
    if args.from_year > args.to_year:
        print("[error] 起始年份不能大于结束年份", file=sys.stderr)
        return 2

    out = Path(args.out)
    site = args.site.rstrip("/")

    cn_events = china.build(args.from_year, args.to_year, include_terms=not args.no_terms)
    us_events = usa.build(args.from_year, args.to_year)
    stat_events = load_overrides(Path(args.overrides))

    calendars = {
        "all.ics": dedupe(cn_events + us_events + stat_events),
        "cn.ics": dedupe(cn_events + stat_events),
        "us.ics": dedupe(us_events),
    }

    for filename, events in calendars.items():
        calname, caldesc, color = TARGETS[filename]
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
        print(f"✅ {filename:<9} {count:>5} 条事件  {size:>7.1f} KB  {calname}")

    span = f"{args.from_year}-{args.to_year}（{args.to_year - args.from_year + 1} 年）"
    print(f"📅 覆盖范围: {span}　输出目录: {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
