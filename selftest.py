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


us = world.build("us", 2026, 2026)
check("美国 2026 条目数在 8-13", 8 <= len(us) <= 13, True)
tg = first("us", 2026, "Thanksgiving")
check("2026 美国感恩节", tg.day if tg else None, date(2026, 11, 26))

jp = world.build("jp", 2026, 2026)
check("2026 日本条目数 >= 14", len(jp) >= 14, True)
check("2026 天皇誕生日", first("jp", 2026, "天皇誕生日").day, date(2026, 2, 23))
check("日本无振替休日", any("振替" in e.summary for e in jp), False)

kr = world.build("kr", 2026, 2026)
seol = first("kr", 2026, "설날")
check("2026 韩国 설날 首日", seol.day if seol else None, date(2026, 2, 16))
check("韩国 설날 连休合并为一条", len([e for e in kr if "설날" in e.summary]), 1)
check("韩国无替代公休日", any("대체" in e.summary for e in kr), False)

sg = world.build("sg", 2026, 2026)
check("2026 新加坡条目数 >= 9", len(sg) >= 9, True)
de = world.build("de", 2026, 2026)
check("2026 德国条目数 >= 8", len(de) >= 8, True)
fr = world.build("fr", 2026, 2026)
check("2026 法国条目数 >= 10", len(fr) >= 10, True)

# ---------- 呈现口径 ----------
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
