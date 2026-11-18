"""外国节日中英译名表。

数据源 date.nager.at 给的是英文名（name）与本国语言名（localName），落地到日历需要中文。
键同时覆盖 name 与 localName 两种写法（如 `Labour Day` / `Labor Day`、
`St. Stephen's Day` / `Boxing Day`），查询时两者都试。

规则：
  - 只做「节日名称」翻译，不做机器翻译 —— 节日名是专有名词，机翻会出「劳动节」→「Labour Day」
    之类的反向错误，也会把 Hari Raya Puasa 直译成「斋戒月后的庆祝」
  - 未收录的名称不硬翻，日历里保留英文原名（宁可英文，也不要错的中文）
  - 新增节日（如未来某位君主的加冕日）只需在此加一行
"""

from __future__ import annotations

# 英文名 → 中文名
ZH_NAMES: dict[str, str] = {
    # ---------- 共同 / 基督教节日 ----------
    "New Year's Day": "元旦",
    "Christmas Day": "圣诞节",
    "Boxing Day": "节礼日",
    "St. Stephen's Day": "节礼日",
    "Good Friday": "耶稣受难日",
    "Holy Saturday": "圣周六",
    "Easter Eve": "圣周六",
    "Easter Sunday": "复活节星期日",
    "Easter Monday": "复活节星期一",
    # ---------- 🇺🇸 美国 ----------
    "Martin Luther King, Jr. Day": "马丁·路德·金纪念日",
    "Presidents Day": "总统日",
    "Washington's Birthday": "总统日",
    "Memorial Day": "阵亡将士纪念日",
    "Juneteenth National Independence Day": "六月节",
    "Independence Day": "独立日",
    "Labor Day": "劳动节",
    "Labour Day": "劳动节",
    "Columbus Day": "哥伦布日",
    "Veterans Day": "退伍军人节",
    "Thanksgiving": "感恩节",
    "Thanksgiving Day": "感恩节",
    # ---------- 🇬🇧 英国 ----------
    "Early May Bank Holiday": "五月初银行假日",
    "Spring Bank Holiday": "春季银行假日",
    "Summer Bank Holiday": "夏季银行假日",
    "Coronation Bank Holiday": "加冕银行假日",
    "Queen’s Platinum Jubilee": "女王登基七十周年",
    "Queen’s State Funeral": "伊丽莎白二世国葬",
    "State Funeral of Queen Elizabeth II": "伊丽莎白二世国葬",
    # ---------- 🇨🇦 加拿大 ----------
    "Canada Day": "加拿大国庆日",
    "Victoria Day": "维多利亚日",
    "National Day for Truth and Reconciliation": "全国真相与和解日",
    # ---------- 🇦🇺 澳大利亚 ----------
    "Australia Day": "澳大利亚国庆日",
    "Anzac Day": "澳新军团日",
    "King's Birthday": "国王诞辰日",
    "Queen's Birthday": "女王诞辰日",
    "National Day of Mourning": "全国哀悼日",
    # ---------- 🇸🇬 新加坡 ----------
    "Chinese New Year": "农历新年",
    "Hari Raya Puasa": "开斋节",
    "Hari Raya Haji": "哈芝节",
    "Vesak Day": "卫塞节",
    "Deepavali": "屠妖节",
    "National Day": "国庆日",
    "Polling Day": "投票日",
}

# 数据源偶发使用弯引号（’），统一后再查表
_QUOTE_MAP = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def normalize(name: str) -> str:
    return (name or "").translate(_QUOTE_MAP).strip()


# 键统一归一化（弯引号→直引号），避免数据源 ’ 与字典 ' 不匹配
_LOOKUP: dict[str, str] = {normalize(k): v for k, v in ZH_NAMES.items()}


def zh_name(*candidates: str) -> str | None:
    """按顺序查找中文译名，命中即返回；全未命中返回 None。"""
    for raw in candidates:
        if not raw:
            continue
        hit = _LOOKUP.get(normalize(raw))
        if hit:
            return hit
    return None


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text or "")
