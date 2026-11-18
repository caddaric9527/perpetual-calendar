#!/usr/bin/env python
"""自检：校验关键节日日期与呈现口径。CI 每次构建前运行。"""

from __future__ import annotations

import re
import sys
from datetime import date

from calgen import china, i18n, world

fails: list[str] = []


def check(label: str, actual, expected) -> None:
    ok = actual == expected
    if not ok:
        fails.append(f"{label}: 期望 {expected}, 实际 {actual}")
    print(f"{'✅' if ok else '❌'} {label}: {actual}")


# ---------- 中国：农历 / 节气 ----------
cny = [
    (2020, date(2020, 1, 25)),
    (2024, date(2024, 2, 10)),
    (2025, date(2025, 1, 29)),
    (2026, date(2026, 2, 17)),
    (2033, date(2033, 1, 31)),  # 著名的 2033 闰十一月问题年
    (2050, date(2050, 1, 23)),
]
for y, expected in cny:
    check(f"{y} 春节", china.lunar_to_solar(y, 1, 1), expected)

check("2026 中秋", china.lunar_to_solar(2026, 8, 15), date(2026, 9, 25))
check("2026 端午", china.lunar_to_solar(2026, 5, 5), date(2026, 6, 19))
check("2026 清明", china.qingming_day(2026), date(2026, 4, 5))
check("2024 清明", china.qingming_day(2024), date(2024, 4, 4))
check("2026 节气数", len(china.solar_terms(2026)), 24)

cn = china.build(2026, 2026)
check("2026 中国条目数 > 40", len(cn) > 40, True)


# ---------- 外国：只呈现节日 ----------
def first(cc: str, year: int, kw: str):
    evs = [e for e in world.build(cc, year, year) if kw in e.summary]
    return evs[0] if evs else None


def exact(cc: str, year: int, name: str):
    """按节日全名精确匹配（避免 Independence Day 命中 Juneteenth National Independence Day）。"""
    flag = world.BY_CC[cc].flag
    evs = [e for e in world.build(cc, year, year) if e.summary == f"{flag} {name}"]
    return evs[0] if evs else None


us = world.build("us", 2026, 2026)
check("美国 2026 条目数在 8-13", 8 <= len(us) <= 13, True)
tg = first("us", 2026, "感恩节")
check("2026 美国感恩节", tg.day if tg else None, date(2026, 11, 26))
check("2026 美国独立日（还原名义日 7/4）", exact("us", 2026, "独立日").day, date(2026, 7, 4))

gb = world.build("gb", 2026, 2026)
check("2026 英国条目数在 6-10", 6 <= len(gb) <= 10, True)
check("2026 英国节礼日（名义日 12/26）", first("gb", 2026, "节礼日").day, date(2026, 12, 26))
check("2026 英国春季银行假日", first("gb", 2026, "春季银行假日").day, date(2026, 5, 25))

ca = world.build("ca", 2026, 2026)
check("2026 加拿大条目数在 6-10", 6 <= len(ca) <= 10, True)
check("2026 加拿大国庆日", first("ca", 2026, "加拿大国庆日").day, date(2026, 7, 1))
check("2026 加拿大维多利亚日", first("ca", 2026, "维多利亚日").day, date(2026, 5, 18))

au = world.build("au", 2026, 2026)
check("2026 澳大利亚条目数在 7-13", 7 <= len(au) <= 13, True)
check("2026 澳新军团日", first("au", 2026, "澳新军团日").day, date(2026, 4, 25))
check("2026 澳大利亚节礼日（名义日 12/26）", first("au", 2026, "节礼日").day, date(2026, 12, 26))

sg = world.build("sg", 2026, 2026)
check("2026 新加坡条目数 >= 9", len(sg) >= 9, True)
check("2026 新加坡农历新年", first("sg", 2026, "农历新年").day, date(2026, 2, 17))
check("2026 新加坡开斋节（官方公布，非规则推算）", first("sg", 2026, "开斋节").day, date(2026, 3, 21))

# ---------- 中文译名 ----------
title = lambda ev: ev.summary.split(" ", 1)[1]  # 去掉国旗
check("外国事件摘要全部为中文",
      all(i18n.has_cjk(title(e)) for e in world.build_all(2026, 2026)), True)
check("中文摘要不含英文残句",
      any(re.search(r"[A-Za-z]{3,}", title(e)) for e in world.build_all(2026, 2026)), False)

# 全时段译名覆盖：缺译只告警（新节日出现不应阻断发布），但会打印清单提示补表
missing: set[str] = set()
for country in world.COUNTRIES:
    for d in world.load(country.cc):
        raw = [d.get("local") or "", d.get("name") or ""]
        if not i18n.zh_name(*raw):
            missing.add(f"{country.cc}:{raw[1] or raw[0]}")
if missing:
    print(f"⚠️ 以下 {len(missing)} 个节日名暂无中文译名（日历中保留英文）：")
    for m in sorted(missing):
        print("   -", m)
else:
    print("✅ 全部节日名均有中文译名")

# ---------- 呈现口径 ----------
check("英语五国数量", len(world.COUNTRIES), 5)
allw = world.build_all(2026, 2026)
check("外国日历不含休/班标记",
      any(e.summary.startswith(("🏖️", "💼")) for e in allw), False)
check("外国事件 UID 唯一", len({(e.day, e.key) for e in allw}) == len(allw), True)

if fails:
    print("\n❌ 自检失败:")
    for f in fails:
        print("  -", f)
    sys.exit(1)

print(f"\n🎉 全部自检通过（中国 {len(cn)} 条 / 外国 {len(allw)} 条）")
