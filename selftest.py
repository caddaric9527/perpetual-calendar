#!/usr/bin/env python
"""自检：校验关键节日日期是否正确。CI 每次构建前运行。"""

from __future__ import annotations

import sys
from datetime import date

from calgen import china, usa

fails: list[str] = []


def check(label: str, actual, expected) -> None:
    ok = actual == expected
    if not ok:
        fails.append(f"{label}: 期望 {expected}, 实际 {actual}")
    print(f"{'✅' if ok else '❌'} {label}: {actual}")


# --- 农历：春节（正月初一）---
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

# --- 中秋 / 端午 ---
check("2026 中秋", china.lunar_to_solar(2026, 8, 15), date(2026, 9, 25))
check("2026 端午", china.lunar_to_solar(2026, 5, 5), date(2026, 6, 19))

# --- 清明 ---
check("2026 清明", china.qingming_day(2026), date(2026, 4, 5))
check("2024 清明", china.qingming_day(2024), date(2024, 4, 4))
check("2025 清明", china.qingming_day(2025), date(2025, 4, 4))

# --- 节气数量 ---
check("2026 节气数", len(china.solar_terms(2026)), 24)

# --- 美国节日 ---
check("2026 感恩节", usa.nth_weekday(2026, 11, usa.THU, 4), date(2026, 11, 26))
check("2026 阵亡将士纪念日", usa.last_weekday(2026, 5, usa.MON), date(2026, 5, 25))
check("2024 复活节", usa.easter(2024), date(2024, 3, 31))
check("2025 复活节", usa.easter(2025), date(2025, 4, 20))
check("2026 独立日补休", usa.observed(date(2026, 7, 4)), date(2026, 7, 3))
check("2022 圣诞补休", usa.observed(date(2022, 12, 25)), date(2022, 12, 26))

# --- 整体构建 ---
cn = china.build(2026, 2026)
us = usa.build(2026, 2026)
check("2026 中国条目数 > 40", len(cn) > 40, True)
check("2026 美国条目数 > 20", len(us) > 20, True)

# 中美共有的节日（元旦/情人节）共用 key，合并后需去重
from generate import dedupe  # noqa: E402

merged = dedupe(cn + us)
check("合并后 UID 唯一", len({(e.day, e.key) for e in merged}) == len(merged), True)
check("共有节日去重（元旦/情人节）", len(merged) == len(cn) + len(us) - 2, True)

if fails:
    print("\n❌ 自检失败:")
    for f in fails:
        print("  -", f)
    sys.exit(1)

print(f"\n🎉 全部自检通过（中国 {len(cn)} 条 / 美国 {len(us)} 条）")
