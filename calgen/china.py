"""中国节日：农历传统节日、公历纪念日、二十四节气。

数据来源：cnlunar（农历/干支/节气表，1900-2099）、zhdate（农历转公历）。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import cnlunar
from zhdate import ZhDate

from .ical import Event

CAT_CN = "🇨🇳 中国节日"
CAT_TERM = "🌿 二十四节气"

MONTH_CN = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
ZODIAC = "鼠牛虎兔龙蛇马羊猴鸡狗猪"

SOLAR_TERMS = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑",
    "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
]
TERM_SLUGS = [
    "xiaohan", "dahan", "lichun", "yushui", "jingzhe", "chunfen", "qingming", "guyu",
    "lixia", "xiaoman", "mangzhong", "xiazhi", "xiaoshu", "dashu", "liqiu", "chushu",
    "bailu", "qiufen", "hanlu", "shuangjiang", "lidong", "xiaoxue", "daxue", "dongzhi",
]

# (农历月, 农历日, key, 名称, emoji, 说明)
LUNAR_FESTIVALS = [
    (1, 1, "chunjie", "春节", "🧧", "农历新年，正月初一，全年最重要的节日"),
    (1, 15, "yuanxiao", "元宵节", "🏮", "正月十五上元节，赏花灯、吃汤圆"),
    (2, 2, "longtaitou", "龙抬头", "🐉", "二月初二，春耕之始，剃头理发"),
    (5, 5, "duanwu", "端午节", "🐲", "五月初五，赛龙舟、吃粽子、挂艾草"),
    (7, 7, "qixi", "七夕节", "💞", "七月初七，中国情人节"),
    (7, 15, "zhongyuan", "中元节", "🕯️", "七月十五，祭祖追思"),
    (8, 15, "zhongqiu", "中秋节", "🌕", "八月十五，赏月、吃月饼、团圆"),
    (9, 9, "chongyang", "重阳节", "🍁", "九月初九，登高敬老、赏菊"),
    (12, 8, "laba", "腊八节", "🥣", "腊月初八，喝腊八粥"),
    (12, 23, "xiaonian", "小年", "🧨", "腊月廿三祭灶（南方部分地区为廿四）"),
]

# (月, 日, key, 名称, emoji, 说明)
SOLAR_FESTIVALS = [
    (1, 1, "new-year", "元旦", "🎉", "公历新年"),
    (2, 14, "valentine", "情人节", "💝", "Valentine's Day"),
    (3, 8, "women-day", "妇女节", "🌸", "国际劳动妇女节"),
    (3, 12, "tree-day", "植树节", "🌳", "中国植树节"),
    (5, 1, "labour-day", "劳动节", "🛠️", "国际劳动节"),
    (5, 4, "youth-day", "青年节", "✊", "五四青年节"),
    (6, 1, "children-day", "儿童节", "🎈", "国际儿童节"),
    (7, 1, "cpc-day", "建党节", "🚩", "中国共产党成立纪念日"),
    (8, 1, "army-day", "建军节", "🎖️", "中国人民解放军建军节"),
    (9, 10, "teachers-day", "教师节", "📚", "中国教师节"),
    (10, 1, "national-day", "国庆节", "🇨🇳", "中华人民共和国国庆节"),
]


def day_cn(n: int) -> str:
    """农历日 → 中文（初一、十五、廿三、三十）。"""
    if n <= 10:
        return "初" + "一二三四五六七八九十"[n - 1]
    if n < 20:
        return "十" + "一二三四五六七八九"[n - 11]
    if n == 20:
        return "二十"
    if n < 30:
        return "廿" + "一二三四五六七八九"[n - 21]
    return "三十"


def ganzhi(lunar_year: int) -> str:
    return GAN[(lunar_year - 4) % 10] + ZHI[(lunar_year - 4) % 12]


def zodiac(lunar_year: int) -> str:
    return ZODIAC[(lunar_year - 4) % 12]


def lunar_to_solar(year: int, month: int, day: int) -> date | None:
    try:
        return ZhDate(year, month, day).to_datetime().date()
    except Exception:
        return None


def solar_terms(year: int) -> list[tuple[str, date]]:
    """返回该公历年的 24 节气（含春节所在岁首顺序，自小寒起）。"""
    try:
        raw = cnlunar.Lunar(datetime(year, 6, 15)).thisYearSolarTermsDateList
    except Exception:
        return []
    out: list[tuple[str, date]] = []
    for idx, (m, d) in enumerate(raw[:24]):
        out.append((SOLAR_TERMS[idx], date(year, m, d)))
    return out


def qingming_day(year: int) -> date | None:
    """清明（既是节气也是法定节日）。"""
    for name, d in solar_terms(year):
        if name == "清明":
            return d
    return None


def lunar_year_note(ly: int) -> str:
    return f"农历{ganzhi(ly)}年（{zodiac(ly)}年）"


def build(year_from: int, year_to: int, *, include_terms: bool = True) -> list[Event]:
    events: list[Event] = []

    # 农历节日：腊月节日会跨到下一公历年，故多算前后各一年
    for ly in range(year_from - 1, year_to + 2):
        for lm, ld, key, name, emoji, note in LUNAR_FESTIVALS:
            d = lunar_to_solar(ly, lm, ld)
            if not d or not (year_from <= d.year <= year_to):
                continue
            events.append(
                Event(
                    day=d,
                    key=key,
                    summary=f"{emoji} {name}",
                    category=CAT_CN,
                    description=(
                        f"农历{MONTH_CN[lm - 1]}月{day_cn(ld)} · {lunar_year_note(ly)}\n{note}"
                    ),
                )
            )

        # 除夕 = 腊月最后一天
        start = lunar_to_solar(ly, 12, 1)
        next_cny = lunar_to_solar(ly + 1, 1, 1)
        if start and next_cny:
            eve = next_cny - timedelta(days=1)
            if year_from <= eve.year <= year_to:
                length = (next_cny - start).days
                events.append(
                    Event(
                        day=eve,
                        key="chuxi",
                        summary="🧧 除夕",
                        category=CAT_CN,
                        description=(
                            f"农历腊月{day_cn(length)} · {lunar_year_note(ly) + ' 除夕'}\n"
                            "守岁、年夜饭、贴春联"
                        ),
                    )
                )

    # 公历节日
    for y in range(year_from, year_to + 1):
        for m, dd, key, name, emoji, note in SOLAR_FESTIVALS:
            d = date(y, m, dd)
            events.append(
                Event(
                    day=d,
                    key=key,
                    summary=f"{emoji} {name}",
                    category=CAT_CN,
                    description=note,
                )
            )

        # 清明
        qm = qingming_day(y)
        if qm:
            events.append(
                Event(
                    day=qm,
                    key="qingming",
                    summary="🌱 清明节",
                    category=CAT_CN,
                    description="二十四节气之清明，扫墓祭祖、踏青（公历 4 月 4-6 日）",
                )
            )

        # 二十四节气
        if include_terms:
            for idx, (name, d) in enumerate(solar_terms(y)):
                if name == "清明":
                    continue
                events.append(
                    Event(
                        day=d,
                        key=f"term-{TERM_SLUGS[idx]}",
                        summary=f"🌿 {name}",
                        category=CAT_TERM,
                        description=f"二十四节气 · {name}",
                    )
                )

    return events
