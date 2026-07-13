#!/usr/bin/env python3
"Regenerate contrib-heatmap.svg from the public GitHub contribution calendar."
from __future__ import annotations

import calendar
import html
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path

USERNAME = "jankibananki"
YEAR = date.today().year
OUT = Path(__file__).resolve().parents[1] / "contrib-heatmap.svg"

BG = "#0d1117"
BORDER = "#30363d"
WHITE = "#f0f6fc"
MUTED = "#8b949e"
PURPLE = "#c084fc"
PINK = "#f472b6"
CYAN = "#22d3ee"
COLORS = ["#161b22", "#312e81", "#6d28d9", "#c026d3", "#22d3ee"]


def fetch_contributions() -> dict[str, int]:
    start = date(YEAR, 1, 1).isoformat()
    end = date(YEAR, 12, 31).isoformat()
    url = f"https://github.com/users/{USERNAME}/contributions?from={start}&to={end}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 GitHub-profile-readme"})
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")

    # GitHub has used both <td> and <rect> cells. Parse either, independent of attribute order.
    cells = re.findall(r"<(?:td|rect)\b[^>]*(?:data-date=\"\d{4}-\d{2}-\d{2}\")[^>]*>", body, flags=re.I)
    result: dict[str, int] = {}
    for cell in cells:
        date_match = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', cell)
        count_match = re.search(r'data-count="(\d+)"', cell)
        level_match = re.search(r'data-level="(\d+)"', cell)
        if not date_match:
            continue
        # data-count is exact when present. data-level is used only as a last-resort approximation.
        count = int(count_match.group(1)) if count_match else int(level_match.group(1)) if level_match else 0
        result[date_match.group(1)] = count

    # Accessible tooltip text exposes exact values; use it to override data-level approximations.
    month_names = "|".join(calendar.month_name[1:])
    for count, month, day in re.findall(rf"(\d+) contributions? on ({month_names}) (\d+)(?:st|nd|rd|th)", body):
        d = date(YEAR, list(calendar.month_name).index(month), int(day))
        result[d.isoformat()] = int(count)
    if not result:
        raise RuntimeError("Could not parse GitHub contribution calendar; GitHub markup may have changed.")
    return result


def level(count: int) -> int:
    if count <= 0: return 0
    if count <= 2: return 1
    if count <= 5: return 2
    if count <= 9: return 3
    return 4


def text(x, y, content, size=12, fill=WHITE, weight="400", anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="mono" font-size="{size}" font-weight="{weight}" fill="{fill}"{a}>{html.escape(str(content))}</text>'


def render(contribs: dict[str, int]) -> str:
    start = date(YEAR, 1, 1)
    start_grid = start - timedelta(days=(start.weekday() + 1) % 7)
    end = date(YEAR, 12, 31)
    end_grid = end + timedelta(days=(5 - end.weekday()) % 7)
    weeks = ((end_grid - start_grid).days // 7) + 1
    total = sum(v for k, v in contribs.items() if k.startswith(f"{YEAR}-"))

    left, top, cell, gap = 67, 78, 17, 5
    rects = []
    for week in range(weeks):
        for dow in range(7):
            d = start_grid + timedelta(days=week * 7 + dow)
            count = contribs.get(d.isoformat(), 0) if d.year == YEAR else 0
            x = left + week * (cell + gap)
            y = top + dow * (cell + gap)
            opacity = "0.22" if d.year != YEAR else "1"
            rects.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{COLORS[level(count)]}" opacity="{opacity}"><title>{d.isoformat()}: {count} contributions</title></rect>')

    months = []
    for month in range(1, 13):
        d = date(YEAR, month, 1)
        week = (d - start_grid).days // 7
        months.append(text(left + week * (cell + gap), 62, calendar.month_abbr[month], fill=MUTED))
    weekdays = [text(18, top + dow * (cell + gap) + 13, label, 11, MUTED) for dow, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]]

    legend = [text(967, 232, "Less", 11, MUTED)]
    for i, color in enumerate(COLORS):
        legend.append(f'<rect x="1005" y="219" width="16" height="16" rx="4" fill="{color}" transform="translate({i*25},0)"/>')
    legend.append(text(1134, 232, "More", 11, MUTED))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="260" viewBox="0 0 1240 260" role="img" aria-labelledby="title desc">
<title id="title">Jana's GitHub contribution graph</title>
<desc id="desc">GitHub contributions for {YEAR}, refreshed by a scheduled workflow.</desc>
<defs><linearGradient id="topLine" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{PURPLE}"/><stop offset="0.5" stop-color="{PINK}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient><style>.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}}</style></defs>
<rect width="1240" height="260" rx="22" fill="{BG}"/><rect x="1.5" y="1.5" width="1237" height="257" rx="20.5" fill="none" stroke="{BORDER}" stroke-width="3"/><rect x="2" y="2" width="1236" height="4" rx="2" fill="url(#topLine)"/>
{text(28,37,f"{total} contributions in {YEAR}",18,WHITE,"700")}{text(1210,37,"auto-refreshed daily",12,MUTED,anchor="end")}
{''.join(months)}{''.join(weekdays)}{''.join(rects)}{''.join(legend)}</svg>'''


if __name__ == "__main__":
    OUT.write_text(render(fetch_contributions()), encoding="utf-8")
    print(f"Updated {OUT}")
