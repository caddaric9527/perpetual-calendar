"""中国以外的英语国家节日 —— 只呈现「节日」，不呈现休息日/补休。

覆盖：美国、英国、加拿大、澳大利亚、新加坡（五国）。

为什么用数据而不是规则硬算：新加坡的开斋节（Hari Raya Puasa）、哈芝节、卫塞节、
屠妖节每年由官方公布，英国/加拿大的君主生日、维多利亚日等按公告微调，
规则推算必然出错，必须用日期数据表。

数据同步见 sync_world.py，缓存 data/world/{cc}.json（已在同步阶段过滤为全国性假日）。

呈现口径（与中国不同）：
  - 中国：显示放假安排（🏖️ 休 / 💼 班 调休），来自国务院公告
  - 外国：只显示节日本体，过滤「observed / substitute / in lieu」等补休条目
  - 连续多日的同一节日（如新加坡农历新年两天）合并为一条，注明连休天数
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .ical import Event

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "world"

# 补休 / 替代休日 —— 属「休息日」语义，外国日历不呈现
SUBSTITUTE_PAT = re.compile(
    r"补休|振替|替代休日|代替休日|대체\s*공휴일|observed|substitute|in\s+lieu|make-?up",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Country:
    cc: str        # ISO 3166-1 alpha-2
    flag: str
    name: str      # 中文名
    mode: str      # 全国性判定策略（同步阶段使用）

    @property
    def category(self) -> str:
        return f"{self.flag} {self.name}节日"


# mode 说明：
#   federal — 仅联邦/全国统一假日（美国 11 个联邦法定假日）
#   national — counties 为空即视为全国性（加/新）
#   eng     — 英国：英格兰+威尔士口径（不含苏格兰、北爱独有假日）
#   au      — 澳大利亚：全国性 或 覆盖 ≥4 个州/领地
COUNTRIES: list[Country] = [
    Country("us", "🇺🇸", "美国", "federal"),
    Country("gb", "🇬🇧", "英国", "eng"),
    Country("ca", "🇨🇦", "加拿大", "national"),
    Country("au", "🇦🇺", "澳大利亚", "au"),
    Country("sg", "🇸🇬", "新加坡", "national"),
]

BY_CC = {c.cc: c for c in COUNTRIES}


# 固定日期节日的「节日本体」日期：数据源在节日撞上周末时会给出补休日（如美国独立日 7/3），
# 既然外国日历只呈现节日，这里还原到名义日期。
FIXED_NOMINAL: dict[str, dict[str, tuple[int, int]]] = {
    "us": {
        "New Year's Day": (1, 1),
        "Juneteenth National Independence Day": (6, 19),
        "Independence Day": (7, 4),
        "Veterans Day": (11, 11),
        "Christmas Day": (12, 25),
    },
    "gb": {
        "New Year's Day": (1, 1),
        "Christmas Day": (12, 25),
        "Boxing Day": (12, 26),
    },
    "au": {
        "New Year's Day": (1, 1),
        "Australia Day": (1, 26),
        "Anzac Day": (4, 25),
        "Christmas Day": (12, 25),
        "Boxing Day": (12, 26),
    },
    "ca": {
        "New Year's Day": (1, 1),
        "Canada Day": (7, 1),
        "Christmas Day": (12, 25),
    },
    "sg": {
        "New Year's Day": (1, 1),
        "Labour Day": (5, 1),
        "National Day": (8, 9),
        "Christmas Day": (12, 25),
    },
}


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "holiday"


def data_path(cc: str) -> Path:
    return DATA_DIR / f"{cc}.json"


def load(cc: str) -> list[dict]:
    p = data_path(cc)
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    days = raw.get("days") or []
    return [d for d in days if isinstance(d, dict) and len(str(d.get("date", ""))) == 10]


def build(cc: str, year_from: int, year_to: int) -> list[Event]:
    country = BY_CC.get(cc)
    if not country:
        return []

    # 按 (年, 节日英文名) 归组，便于合并连休、剔除补休、去重
    groups: dict[tuple[int, str], list[dict]] = {}
    for item in load(cc):
        d = date.fromisoformat(item["date"])
        if not (year_from <= d.year <= year_to):
            continue
        name = str(item.get("name") or item.get("local") or "Holiday")
        local = str(item.get("local") or name)
        if SUBSTITUTE_PAT.search(name) or SUBSTITUTE_PAT.search(local):
            continue  # 补休 / 振替休日不呈现
        groups.setdefault((d.year, name), []).append({"date": d, "local": local, "name": name})

    events: list[Event] = []
    for (_, name), items in groups.items():
        items.sort(key=lambda x: x["date"])
        # 切成连续日期段，只保留第一段（同一节日在同年不连续的多个日期视为重复，如补休日）
        runs: list[list[dict]] = []
        for it in items:
            if runs and (it["date"] - runs[-1][-1]["date"]).days == 1:
                runs[-1].append(it)
            else:
                runs.append([it])
        run = runs[0]
        start, end = run[0]["date"], run[-1]["date"]
        local = run[0]["local"]

        fixed = FIXED_NOMINAL.get(cc, {})
        nominal = fixed.get(name) or fixed.get(local)
        if nominal:  # 还原固定日期节日（去掉补休位移）
            start = date(start.year, nominal[0], nominal[1])
            end = start

        desc = []
        if name != local:
            desc.append(name)
        desc.append("公共假日")
        if len(run) > 1:
            desc.append(f"连休 {len(run)} 天（{start:%Y-%m-%d} 至 {end:%Y-%m-%d}）")
        desc.append(f"数据源：date.nager.at（{country.name}官方公布日期）")

        events.append(
            Event(
                day=start,
                key=f"{cc}-{slug(name)}",
                summary=f"{country.flag} {local}",
                category=country.category,
                description="\n".join(desc),
            )
        )
    return events


def build_all(year_from: int, year_to: int, ccs: list[str] | None = None) -> list[Event]:
    out: list[Event] = []
    for cc in ccs or [c.cc for c in COUNTRIES]:
        out += build(cc, year_from, year_to)
    return out


def coverage(cc: str) -> tuple[int, int] | None:
    days = load(cc)
    if not days:
        return None
    years = sorted(int(d["date"][:4]) for d in days)
    return years[0], years[-1]
