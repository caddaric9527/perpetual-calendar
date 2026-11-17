"""美国节日：联邦法定假日 + 常见民间节日。

规则化生成（星期规则 + 复活节 computus + 固定日期的联邦补休），可无限延伸年份。
"""

from __future__ import annotations

from datetime import date, timedelta

from .ical import Event

CAT_US = "🇺🇸 美国节日"

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """该月第 n 个星期 weekday（n 从 1 开始）。"""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def easter(year: int) -> date:
    """格里高利历复活节（Anonymous Gregorian algorithm）。"""
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


def observed(d: date) -> date:
    """联邦假日补休：周六提前至周五，周日顺延至周一。"""
    if d.weekday() == SAT:
        return d - timedelta(days=1)
    if d.weekday() == SUN:
        return d + timedelta(days=1)
    return d


def _fixed(events: list[Event], y: int, m: int, dd: int, key: str, name: str, emoji: str,
           note: str, *, federal: bool = True) -> None:
    d = date(y, m, dd)
    events.append(Event(d, key, f"{emoji} {name}", CAT_US, note))
    if federal:
        o = observed(d)
        if o != d:
            events.append(
                Event(o, f"{key}-observed", f"{emoji} {name}（补休）", CAT_US,
                      f"{note} · {d:%Y-%m-%d} 为{'周六' if d.weekday() == SAT else '周日'}，"
                      f"联邦假日顺延至 {o:%Y-%m-%d}")
            )


def build(year_from: int, year_to: int) -> list[Event]:
    events: list[Event] = []

    for y in range(year_from, year_to + 1):
        # ---- 11 个联邦法定假日 ----
        _fixed(events, y, 1, 1, "new-year", "元旦 New Year's Day", "🎊", "联邦法定假日")
        d = nth_weekday(y, 1, MON, 3)
        events.append(Event(d, "mlk-day", "✊ 马丁·路德·金纪念日 MLK Day", CAT_US,
                            "1 月第三个星期一 · 联邦法定假日"))
        d = nth_weekday(y, 2, MON, 3)
        events.append(Event(d, "presidents-day", "🏛️ 总统日 Presidents' Day", CAT_US,
                            "2 月第三个星期一 · 华盛顿诞辰，联邦法定假日"))
        d = last_weekday(y, 5, MON)
        events.append(Event(d, "memorial-day", "🎖️ 阵亡将士纪念日 Memorial Day", CAT_US,
                            "5 月最后一个星期一 · 联邦法定假日，暑期开始"))
        _fixed(events, y, 6, 19, "juneteenth", "✊ 六月节 Juneteenth", "🕊️",
               "6 月 19 日 · 纪念废除奴隶制，联邦法定假日")
        _fixed(events, y, 7, 4, "independence-day", "独立日 Independence Day", "🗽",
               "7 月 4 日 · 美国国庆，联邦法定假日")
        d = nth_weekday(y, 9, MON, 1)
        events.append(Event(d, "labor-day", "🛠️ 劳动节 Labor Day", CAT_US,
                            "9 月第一个星期一 · 联邦法定假日"))
        d = nth_weekday(y, 10, MON, 2)
        events.append(Event(d, "columbus-day", "⛵ 哥伦布日 Columbus Day", CAT_US,
                            "10 月第二个星期一 · 联邦法定假日"))
        _fixed(events, y, 11, 11, "veterans-day", "🎗️ 退伍军人节 Veterans Day", "",
               "11 月 11 日 · 联邦法定假日")
        d = nth_weekday(y, 11, THU, 4)
        events.append(Event(d, "thanksgiving", "🦃 感恩节 Thanksgiving", CAT_US,
                            "11 月第四个星期四 · 火鸡、家庭聚餐、黑五"))
        _fixed(events, y, 12, 25, "christmas", "🎄 圣诞节 Christmas", "",
               "12 月 25 日 · 联邦法定假日")

        # ---- 民间常见节日 ----
        _fixed(events, y, 2, 2, "groundhog-day", "土拨鼠日 Groundhog Day", "🦫",
               "2 月 2 日 · 预测春季是否提前到来", federal=False)
        _fixed(events, y, 2, 14, "valentine", "情人节 Valentine's Day", "💝",
               "2 月 14 日", federal=False)
        _fixed(events, y, 3, 17, "st-patrick", "圣帕特里克节 St. Patrick's Day", "🍀",
               "3 月 17 日 · 爱尔兰裔文化节", federal=False)
        _fixed(events, y, 4, 1, "april-fools", "愚人节 April Fools' Day", "🤡",
               "4 月 1 日", federal=False)
        _fixed(events, y, 4, 22, "earth-day", "地球日 Earth Day", "🌍",
               "4 月 22 日", federal=False)
        e = easter(y)
        events.append(Event(e, "easter", "🐰 复活节 Easter", CAT_US,
                            f"春分月圆后首个星期日 · 彩蛋与兔子\n"
                            f"耶稣受难日 Good Friday: {e - timedelta(days=2):%Y-%m-%d}"))
        d = nth_weekday(y, 5, SUN, 2)
        events.append(Event(d, "mothers-day", "🌷 母亲节 Mother's Day", CAT_US,
                            "5 月第二个星期日"))
        d = nth_weekday(y, 6, SUN, 3)
        events.append(Event(d, "fathers-day", "👔 父亲节 Father's Day", CAT_US,
                            "6 月第三个星期日"))
        _fixed(events, y, 10, 31, "halloween", "🎃 万圣节 Halloween", "",
               "10 月 31 日 · 南瓜灯、trick-or-treat", federal=False)

        # 选举日（偶数年）：11 月第一个星期一之后的星期二
        if y % 2 == 0:
            d = nth_weekday(y, 11, MON, 1) + timedelta(days=1)
            events.append(Event(d, "election-day", "🗳️ 选举日 Election Day", CAT_US,
                                "偶数年 11 月第一个星期一后的星期二 · 中期选举/大选"))

        # 夏令时切换（美国本土）
        d = nth_weekday(y, 3, SUN, 2)
        events.append(Event(d, "dst-start", "⏰ 夏令时开始（拨快 1 小时）", CAT_US,
                            "3 月第二个星期日 02:00 → 03:00（美国本土）"))
        d = nth_weekday(y, 11, SUN, 1)
        events.append(Event(d, "dst-end", "⏰ 夏令时结束（拨慢 1 小时）", CAT_US,
                            "11 月第一个星期日 02:00 → 01:00（美国本土）"))

    return events
