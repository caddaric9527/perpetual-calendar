#!/usr/bin/env python
"""自检：校验关键节日日期与呈现口径。CI 每次构建前运行。"""

from __future__ import annotations

import sys
from datetime import date

from calgen import china, world

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
tg = first("us", 2026, "Thanksgiving")
check("2026 美国感恩节", tg.day if tg else None, date(2026, 11, 26))
check("2026 美国独立日（还原名义日 7/4）", exact("us", 2026, "Independence Day").day, date(2026, 7, 4))

gb = world.build("gb", 2026, 2026)
check("2026 英国条目数在 6-10", 6 <= len(gb) <= 10, True)
check("2026 英国 Boxing Day（名义日 12/26）", first("gb", 2026, "Boxing Day").day, date(2026, 12, 26))
check("2026 英国春季银行假日", first("gb", 2026, "Spring Bank Holiday").day, date(2026, 5, 25))

ca = world.build("ca", 2026, 2026)
check("2026 加拿大条目数在 6-10", 6 <= len(ca) <= 10, True)
check("2026 加拿大国庆", first("ca", 2026, "Canada Day").day, date(2026, 7, 1))
check("2026 加拿大维多利亚日", first("ca", 2026, "Victoria Day").day, date(2026, 5, 18))

au = world.build("au", 2026, 2026)
check("2026 澳大利亚条目数在 7-13", 7 <= len(au) <= 13, True)
check("2026 澳新军团日", first("au", 2026, "Anzac Day").day, date(2026, 4, 25))
check("2026 澳大利亚 Boxing Day（名义日 12/26）", first("au", 2026, "Boxing Day").day, date(2026, 12, 26))

sg = world.build("sg", 2026, 2026)
check("2026 新加坡条目数 >= 9", len(sg) >= 9, True)
check("2026 新加坡农历新年", first("sg", 2026, "Chinese New Year").day, date(2026, 2, 17))
check("2026 新加坡开斋节（官方公布，非规则推算）", first("sg", 2026, "Hari Raya Puasa").day, date(2026, 3, 21))

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
