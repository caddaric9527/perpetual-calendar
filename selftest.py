#!/usr/bin/env python
"""自检：校验关键节日日期与呈现口径。CI 每次构建前运行。"""

from __future__ import annotations

import re
import sys
from datetime import date

from calgen import china, intl

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


# ---------- 全球通用节日：日期规则 ----------
def one(year: int, name: str):
    evs = [e for e in intl.build(year, year) if e.summary.endswith(name)]
    return evs[0] if evs else None


def day_of(year: int, name: str):
    ev = one(year, name)
    return ev.day if ev else None


check("2026 母亲节（5 月第 2 个周日）", day_of(2026, "母亲节"), date(2026, 5, 10))
check("2027 母亲节", day_of(2027, "母亲节"), date(2027, 5, 9))
check("2026 父亲节（6 月第 3 个周日）", day_of(2026, "父亲节"), date(2026, 6, 21))
check("2026 感恩节（11 月第 4 个周四）", day_of(2026, "感恩节"), date(2026, 11, 26))
check("2025 感恩节", day_of(2025, "感恩节"), date(2025, 11, 27))
check("2026 复活节", day_of(2026, "复活节"), date(2026, 4, 5))
check("2025 复活节", day_of(2025, "复活节"), date(2025, 4, 20))
check("2024 复活节", day_of(2024, "复活节"), date(2024, 3, 31))
check("2038 复活节（远期 computus）", day_of(2038, "复活节"), date(2038, 4, 25))
check("2026 世界水日", day_of(2026, "世界水日"), date(2026, 3, 22))
check("2026 联合国日", day_of(2026, "联合国日"), date(2026, 10, 24))
check("2026 世界人权日", day_of(2026, "世界人权日"), date(2026, 12, 10))

# ---------- 呈现口径 ----------
catalog = intl.load()
check("节日清单条数", len(catalog), 28)
check("全球节日不含休息日标记",
      any(e.summary.startswith(("🏖️", "💼")) for e in intl.build(2026, 2026)), False)
check("全球节日摘要全部中文",
      all(any("\u4e00" <= ch <= "\u9fff" for ch in e.summary) for e in intl.build(2026, 2026)), True)
check("全球节日摘要不含英文残句",
      any(re.search(r"[A-Za-z]{3,}", e.summary) for e in intl.build(2026, 2026)), False)
check("全球节日 UID 唯一（2020-2040）",
      len({(e.day, e.key) for e in intl.build(2020, 2040)}) == len(intl.build(2020, 2040)), True)

# 每年条目数应稳定（固定日期 + 浮动规则，不应随年份抖动）
counts = {y: len(intl.build(y, y)) for y in (2024, 2026, 2027, 2031, 2040)}
check("每年全球节日条数稳定", len(set(counts.values())), 1)
print("   每年条数:", counts)

# 合并日历（all.ics）不应出现「同一天同名」的重复条目：intl.ics 独立完整，
# 但 all.ics 里与中国日历重复的情人节/元旦等只保留中国那条
import generate  # noqa: E402  （同目录 CLI，仅用于复用去重逻辑）

merged = generate.dedupe(cn + generate.drop_shadowed(cn, intl.build(2026, 2026)))
names = [(e.day, e.summary.split(" ", 1)[-1]) for e in merged]
check("合并日历无同名同日重复", len(names) - len(set(names)), 0)
check("合并日历仍含中国侧情人节",
      [s for d, s in names if d == date(2026, 2, 14)], ["情人节"])

if fails:
    print("\n❌ 自检失败:")
    for f in fails:
        print("  -", f)
    sys.exit(1)

print(f"\n🎉 全部自检通过（中国 {len(cn)} 条 / 全球 {len(intl.build(2026, 2026))} 条）")
