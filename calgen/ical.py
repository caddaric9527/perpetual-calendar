"""极简 iCalendar (RFC 5545) 生成器，针对 Apple 日历订阅优化。

只实现订阅场景需要的部分：全天事件 + VCALENDAR 属性 + UTF-8 折行。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

CRLF = "\r\n"


def escape(text: str) -> str:
    """转义 ICS 文本值中的特殊字符。"""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def fold(line: str, limit: int = 75) -> str:
    """按 UTF-8 字节数折行（不切断多字节字符），续行以空格开头。"""
    parts: list[str] = []
    cur = ""
    size = 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            parts.append(cur)
            cur = " " + ch
            size = 1 + n
        else:
            cur += ch
            size += n
    parts.append(cur)
    return CRLF.join(parts)


@dataclass(frozen=True)
class Event:
    """一条全天事件。day + key 组合保证 UID 稳定（订阅刷新时不会重复/丢失）。"""

    day: date
    key: str
    summary: str
    category: str = ""
    description: str = ""


def write_calendar(
    events: list[Event],
    path: Path,
    *,
    calname: str,
    caldesc: str,
    uid_domain: str,
    color: str = "#FF9500",
    source_url: str | None = None,
    tz: str = "Asia/Shanghai",
) -> int:
    """写出 .ics 文件，返回事件条数。"""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    head = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//caddaric//perpetual-calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape(calname)}",
        f"X-WR-CALDESC:{escape(caldesc)}",
        f"X-WR-TIMEZONE:{tz}",
        "X-APPLE-CALENDAR-COLOR:" + color,
        # Apple 日历按 REFRESH-INTERVAL / X-PUBLISHED-TTL 决定刷新节奏
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
        "X-PUBLISHED-TTL:P1D",
    ]
    if source_url:
        head.append(f"SOURCE;VALUE=URI:{source_url}")
        head.append(f"URL:{source_url}")

    body: list[str] = []
    for ev in sorted(events, key=lambda e: (e.day, e.key)):
        uid = f"{ev.day:%Y%m%d}-{ev.key}@{uid_domain}"
        body += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{ev.day:%Y%m%d}",
            f"DTEND;VALUE=DATE:{date.fromordinal(ev.day.toordinal() + 1):%Y%m%d}",
            f"SUMMARY:{escape(ev.summary)}",
        ]
        if ev.description:
            body.append(f"DESCRIPTION:{escape(ev.description)}")
        if ev.category:
            body.append(f"CATEGORIES:{escape(ev.category)}")
        body += [
            "TRANSP:TRANSPARENT",
            "CLASS:PUBLIC",
            "END:VEVENT",
        ]

    lines = head + body + ["END:VCALENDAR"]
    content = CRLF.join(fold(line) for line in lines) + CRLF
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    return len(events)
