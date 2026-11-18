"""全球通用节日：联合国核心国际日 + 全球通行民间节日。

数据在 data/intl_days.json，**纯规则生成，不依赖任何外部 API** —— 按年份算出日期即可，
不会因为第三方接口下线、改结构或限流而失效。

支持三种日期规则：
  - 固定日期：`month` + `day`
  - 第 N 个某星期几：`month` + `rule: nth_sunday|nth_thursday` + `nth`
  - 复活节：`rule: easter`（Anonymous Gregorian computus，1583 年起通用）

与中国日历重叠的节日（元旦、妇女节、劳动节、儿童节）只在中国日历呈现，
data/intl_days.json 里不重复收录，`generate.py` 还会再做一次同名同日去重。
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from .ical import Event

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "intl_days.json"

CAT_MEMORIAL = "🌍 国际纪念日"
CAT_FESTIVAL = "🎉 民间节日"
KIND_CATEGORY = {"memorial": CAT_MEMORIAL, "festival": CAT_FESTIVAL}

# 星期几的编号（Mon=0 ... Sun=6）
_WEEKDAY = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6}


def load() -> list[dict]:
    try:
        raw = json.loads(DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [d for d in (raw.get("days") or []) if isinstance(d, dict) and d.get("name")]


def nth_weekday(year: int, month: int, weekday: int, nth: int) -> date | None:
    """某月第 nth 个星期 weekday（nth 为负表示倒数第几个）。"""
    if nth > 0:
        first = date(year, month, 1)
        delta = (weekday - first.weekday()) % 7
        return first + timedelta(days=delta + 7 * (nth - 1))
    # 倒数：从下个月 1 日往回找
    nxt = date(year + month // 12, month % 12 + 1, 1)
    last = nxt - timedelta(days=1)
    delta = (last.weekday() - weekday) % 7
    return last - timedelta(days=delta + 7 * (-nth - 1))


def easter(year: int) -> date:
    """Anonymous Gregorian algorithm（Meeus/Jones/Butcher）。"""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


def resolve(item: dict, year: int) -> date | None:
    """把一条规则解析成具体日期；2/29 之类不存在的日期返回 None。"""
    rule = item.get("rule")
    if rule == "easter":
        return easter(year)

    month = int(item["month"])
    if rule in ("nth_sunday", "nth_thursday", "nth_monday", "nth_friday", "nth_saturday"):
        weekday = _WEEKDAY[rule.removeprefix("nth_")]
        return nth_weekday(year, month, weekday, int(item.get("nth", 1)))

    day = item.get("day")
    if not day:
        return None
    try:
        return date(year, month, int(day))
    except ValueError:
        return None


def build(year_from: int, year_to: int) -> list[Event]:
    events: list[Event] = []
    for item in load():
        name = str(item["name"]).strip()
        category = KIND_CATEGORY.get(str(item.get("kind")), CAT_MEMORIAL)
        for year in range(year_from, year_to + 1):
            day = resolve(item, year)
            if not day:
                continue
            desc = [str(item.get("desc") or "").strip()]
            if category == CAT_MEMORIAL:
                desc.append("联合国官方国际日")
            else:
                desc.append("全球通行民间节日")
            desc.append("数据源：un.org 国际日 + 人工整理的民间节日规则")
            events.append(
                Event(
                    day=day,
                    key=f"intl-{item.get('key') or name}",
                    summary=f"{category.split()[0]} {name}",
                    category=category,
                    description="\n".join(x for x in desc if x),
                )
            )
    return events


def catalog() -> list[dict]:
    """供落地页/文档展示的规则清单（未展开年份）。"""
    out = []
    for item in load():
        out.append({
            "name": item["name"],
            "kind": item.get("kind", "memorial"),
            "rule": _rule_label(item),
            "desc": item.get("desc", ""),
        })
    return out


def _rule_label(item: dict) -> str:
    rule = item.get("rule")
    if rule == "easter":
        return "春分月圆后首个周日"
    if rule and rule.startswith("nth_"):
        cn = {"sunday": "周日", "thursday": "周四", "monday": "周一",
              "friday": "周五", "saturday": "周六"}[rule.removeprefix("nth_")]
        return f"{int(item['month'])} 月第 {int(item.get('nth', 1))} 个{cn}"
    return f"{int(item['month'])} 月 {int(item.get('day', 1))} 日"
