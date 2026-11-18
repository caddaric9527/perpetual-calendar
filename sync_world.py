#!/usr/bin/env python
"""同步中国以外国家的公共假日到 data/world/{cc}.json。

数据源：https://date.nager.at/api/v3/PublicHolidays/{year}/{cc}
  免费、无需 key，按国家法定规则计算（含美国的 observed 补休、日本的振替休日），
  未来年份同样可取（已验证 2035 年可用）。

全国性过滤（避免把州/省级假日混进国家日历）：
  - 美国：只保留 counties 为空且类型含 Public/Bank → 11 个联邦法定假日
  - 英国：英格兰+威尔士口径（counties 为空或含 GB-ENG）
  - 澳大利亚：counties 为空，或聚合后覆盖 ≥4 个州/领地（如 Anzac Day、King's Birthday）
  - 其他国家：counties 为空即视为全国性
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from calgen.world import COUNTRIES, data_path

API = "https://date.nager.at/api/v3/PublicHolidays/{year}/{cc}"
VALID_TYPES = {"Public", "Bank"}


def fetch(year: int, cc: str, timeout: int = 25) -> list[dict] | None:
    req = urllib.request.Request(
        API.format(year=year, cc=cc.upper()),
        headers={"User-Agent": "perpetual-calendar/1.2", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        print(f"[warn] {cc.upper()} {year} HTTP {exc.code}", file=sys.stderr)
        return None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"[warn] {cc.upper()} {year} 抓取失败: {exc}", file=sys.stderr)
        return None
    return data if isinstance(data, list) else None


def select(items: list[dict], mode: str) -> list[dict]:
    """按国家策略过滤出全国性假日。"""
    typed = [i for i in items if VALID_TYPES & set(i.get("types") or [])]
    if not typed:
        return []

    if mode == "federal":
        picked = [i for i in typed if not i.get("counties")]
    elif mode == "eng":
        picked = [i for i in typed if not i.get("counties") or "GB-ENG" in (i.get("counties") or [])]
    elif mode == "au":
        # 同名节日按州聚合，覆盖 ≥4 个州/领地视为全国性
        agg: dict[str, int] = defaultdict(int)
        for i in typed:
            agg[i["localName"]] += len(i.get("counties") or []) or 99
        picked = [
            i for i in typed
            if not i.get("counties") or agg[i["localName"]] >= 4
        ]
    else:
        picked = [i for i in typed if not i.get("counties")]

    # 兜底：过滤后为空说明该年结构异常，退回全部 Public/Bank
    return picked or typed


def main() -> int:
    ap = argparse.ArgumentParser(description="同步各国公共假日")
    ap.add_argument("--from-year", type=int, default=2020)
    ap.add_argument("--to-year", type=int, default=2040)
    ap.add_argument("--countries", default="", help="逗号分隔的国家代码，默认全部")
    args = ap.parse_args()

    ccs = [c.strip().lower() for c in args.countries.split(",") if c.strip()] or [c.cc for c in COUNTRIES]
    total_events = 0
    failed: list[str] = []

    for country in COUNTRIES:
        if country.cc not in ccs:
            continue
        path = data_path(country.cc)
        existing: list[dict] = []
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8")).get("days") or []
            except json.JSONDecodeError:
                existing = []

        # 保留范围外年份的旧数据
        kept = [d for d in existing if not (args.from_year <= int(d["date"][:4]) <= args.to_year)]
        collected: list[dict] = []
        years_ok: list[int] = []

        for year in range(args.from_year, args.to_year + 1):
            items = fetch(year, country.cc)
            if not items:
                failed.append(f"{country.cc}{year}")
                continue
            picked = select(items, country.mode)
            if not picked:
                continue
            years_ok.append(year)
            for i in picked:
                collected.append({
                    "date": i["date"],
                    "name": i.get("name") or i.get("localName"),
                    "local": i.get("localName") or i.get("name"),
                })

        if not collected:
            print(f"⚠️ {country.cc.upper()} 无新数据，保留原文件", file=sys.stderr)
            continue

        # 同一天同名去重
        uniq: dict[tuple[str, str], dict] = {}
        for d in kept + collected:
            uniq.setdefault((d["date"], d.get("local") or d.get("name") or ""), d)
        days = [uniq[k] for k in sorted(uniq)]

        payload = {
            "_name": country.name,
            "_source": "https://date.nager.at",
            "_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_years": years_ok,
            "days": days,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total_events += len(collected)
        span = f"{years_ok[0]}-{years_ok[-1]}" if years_ok else "-"
        print(f"✅ {country.flag} {country.name:<4} {len(collected):>4} 条 / {span}")

    print(f"\n共写入 {total_events} 条假日数据"
          + (f"，失败 {len(failed)} 次年：{failed[:6]}" if failed else ""))
    return 0 if total_events else 1


if __name__ == "__main__":
    raise SystemExit(main())
