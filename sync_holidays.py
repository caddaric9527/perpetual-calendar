#!/usr/bin/env python
"""同步中国法定节假日安排（含调休）到 data/holidays_cn.json。

数据源：https://github.com/NateScarlet/holiday-cn
  该项目在国务院公告发布后自动更新，提供每年一份 JSON：
  {"year":2026,"papers":["https://www.gov.cn/..."],"days":[{"name":"春节","date":"2026-02-17","isOffDay":true}]}

设计要点：
- 远端是权威数据，覆盖同名手工条目；远端未公布的年份保留手工数据
- 全部请求失败时不覆盖本地文件（避免 CI 把日历清空）
- 每年公告一般在 11 月前后发布，未发布年份返回 404 属正常
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{year}.json"

META = {
    "_说明": "中国法定节假日安排（含调休）。由 sync_holidays.py 从国务院公告数据源自动同步，也可手工补充。",
    "_格式": '日期(YYYY-MM-DD) => {"type": "休" 或 "班", "name": "节日名称"}',
    "_数据源": "https://github.com/NateScarlet/holiday-cn",
}


def fetch_year(year: int, timeout: int = 20) -> dict | None:
    req = urllib.request.Request(
        SOURCE.format(year=year), headers={"User-Agent": "perpetual-calendar/1.1"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None  # 该年公告尚未发布
        raise
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"[warn] {year} 抓取失败: {exc}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="同步中国法定节假日安排")
    ap.add_argument("--from-year", type=int, default=2018)
    ap.add_argument("--to-year", type=int, default=2035)
    ap.add_argument("--out", default="data/holidays_cn.json")
    ap.add_argument("--strict", action="store_true", help="一条都没抓到则以非 0 退出")
    args = ap.parse_args()

    out = Path(args.out)
    existing: dict = {}
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"[warn] 本地文件损坏，将被重建: {out}", file=sys.stderr)

    manual = {
        k: v for k, v in existing.items()
        if not k.startswith("_") and isinstance(v, dict)
    }

    collected: dict[str, dict] = {}
    papers: list[str] = []
    years_ok: list[int] = []
    failed_years: list[int] = []

    for year in range(args.from_year, args.to_year + 1):
        try:
            data = fetch_year(year)
        except Exception as exc:  # 网络抖动 / 5xx
            print(f"[warn] {year} 跳过: {exc}", file=sys.stderr)
            failed_years.append(year)
            continue
        if not data:
            continue
        days = data.get("days") or []
        if not days:
            continue
        years_ok.append(year)
        papers += [p for p in (data.get("papers") or []) if p]
        for item in days:
            d = str(item.get("date", ""))
            if len(d) != 10:
                continue
            off = item.get("isOffDay")
            collected[d] = {
                "type": "休" if off else "班",
                "name": str(item.get("name", "法定节假日")),
            }

    if not collected:
        print("⚠️ 未获取到任何节假日数据，保留本地文件不变", file=sys.stderr)
        return 1 if args.strict else 0

    # 远端优先，未覆盖的手工条目保留（例如手工补录的历史年份）
    merged = dict(manual)
    merged.update(collected)

    payload = dict(META)
    payload["_更新时间"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload["_覆盖年份"] = years_ok
    if papers:
        payload["_公告"] = sorted(set(papers))
    payload.update(dict(sorted(merged.items())))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    rest = sum(1 for v in collected.values() if v["type"] == "休")
    work = len(collected) - rest
    span = f"{years_ok[0]}-{years_ok[-1]}" if years_ok else "-"
    print(f"✅ 已同步 {len(collected)} 天（休 {rest} / 班 {work}），覆盖 {span} → {out}")
    if failed_years:
        print(f"⚠️ 失败年份: {failed_years}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
