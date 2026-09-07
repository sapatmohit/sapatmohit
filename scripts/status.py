#!/usr/bin/env python3
"""Regenerate assets/status.svg from this repo's git history.

No network, no dependencies. Run it locally or let the Action run it.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "status.svg"

AMBER, DIM, OK, WARN, BG = "#FFB94A", "#8A5F22", "#6FE87A", "#FF4D6D", "#0A0705"


def git(*args: str, fallback: str = "") -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20
        ).stdout.strip() or fallback
    except Exception:
        return fallback


def human_gap(seconds: float) -> str:
    m = int(seconds // 60)
    if m < 60:
        return f"{max(m, 0)}m ago"
    if m < 1440:
        return f"{m // 60}h ago"
    d = m // 1440
    return f"{d}d ago" if d < 365 else f"{d // 365}y {d % 365}d ago"


def bar(filled: int, width: int = 10) -> str:
    filled = max(0, min(width, filled))
    return "\u2588" * filled + "\u2591" * (width - filled)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)

    commits = git("rev-list", "--count", "HEAD", fallback="0")
    first_ts = git("log", "--reverse", "--format=%ct", fallback="")
    first_ts = first_ts.splitlines()[0] if first_ts else ""
    last_ts = git("log", "-1", "--format=%ct", fallback="")
    subject = git("log", "-1", "--format=%s", fallback="\u2500")[:44]

    if last_ts.isdigit():
        gap = (now - dt.datetime.fromtimestamp(int(last_ts), dt.timezone.utc)).total_seconds()
        keystroke = human_gap(gap)
        # cools off after a week of silence
        temp_units = 10 if gap < 86400 else 7 if gap < 259200 else 4 if gap < 604800 else 1
    else:
        keystroke, temp_units, gap = "\u2500", 5, 0.0

    if first_ts.isdigit():
        days = (now - dt.datetime.fromtimestamp(int(first_ts), dt.timezone.utc)).days
        uptime = f"{days // 365}y {days % 365}d" if days >= 365 else f"{days}d"
    else:
        uptime = "\u2500"

    temp_label, temp_color = (
        ("NOMINAL", OK) if temp_units >= 7
        else ("COOLING", AMBER) if temp_units >= 4
        else ("COLD \u2014 nobody has typed in a week", WARN)
    )

    rows = [
        ("LAST KEYSTROKE", keystroke, AMBER),
        ("LAST WORDS", f'"{subject}"', DIM),
        ("TOTAL COMMITS", f"{int(commits):,}" if commits.isdigit() else commits, AMBER),
        ("STATION UPTIME", uptime, AMBER),
        ("CORE TEMPERATURE", f"{bar(temp_units)}  {temp_label}", temp_color),
    ]

    lines = []
    y = 92
    for label, value, color in rows:
        dots = "." * max(2, 30 - len(label))
        lines.append(
            f'    <text class="t" x="40" y="{y}">{esc(label)}</text>'
            f'<text class="t dim" x="{40 + 9.05 * (len(label) + 1):.0f}" y="{y}">{esc(dots)}</text>'
            f'<text class="t" fill="{color}" x="345" y="{y}">{esc(value)}</text>'
        )
        y += 27

    stamp = now.strftime("%Y-%m-%d %H:%M UTC")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 265" width="760" height="265" role="img" aria-label="station vitals">
  <defs>
    <pattern id="s" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#000" opacity="0.28"/>
    </pattern>
    <style>
      .t {{ font-family: "SFMono-Regular","DejaVu Sans Mono",Consolas,"Courier New",monospace;
            font-size: 14px; letter-spacing: 1.1px; fill: {AMBER}; }}
      .dim {{ fill: {DIM}; }}
      .h {{ font-size: 15px; letter-spacing: 3px; fill: #FFD79A; }}
    </style>
  </defs>
  <rect width="760" height="265" rx="12" fill="#120C08"/>
  <rect x="6" y="6" width="748" height="253" rx="9" fill="{BG}" stroke="#3A2612" stroke-width="1.4"/>
  <text class="t h" x="40" y="48">S T A T I O N   V I T A L S</text>
  <text class="t dim" x="40" y="68">self-reported, unattended, refreshed {stamp}</text>
  <line x1="40" y1="78" x2="720" y2="78" stroke="#3A2612" stroke-width="1"/>
{chr(10).join(lines)}
  <text class="t dim" x="40" y="238">nobody asked it to keep doing this.</text>
  <rect x="6" y="6" width="748" height="253" rx="9" fill="url(#s)"/>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} \u2014 {keystroke}, {commits} commits")


if __name__ == "__main__":
    main()
