#!/usr/bin/env python3
"""Carve a visitor's name into rooms/wall.md.

Reads the issue title from $RAW_TITLE and the author from $VISITOR.
Everything is sanitized hard: the title is untrusted input from the internet.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WALL = ROOT / "rooms" / "wall.md"

START, END = "<!-- CARVE:START -->", "<!-- CARVE:END -->"
MAX_ENTRIES = 60
MAX_LEN = 24

# letters, digits, spaces and a couple of harmless marks. nothing else survives.
ALLOWED = re.compile(r"[^A-Za-z0-9 ._\-]")


def clean_name(raw: str) -> str:
    name = raw.split(":", 1)[1] if ":" in raw else raw
    name = ALLOWED.sub("", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:MAX_LEN]


def clean_login(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9\-]", "", raw)[:39]


def main() -> int:
    name = clean_name(os.environ.get("RAW_TITLE", ""))
    login = clean_login(os.environ.get("VISITOR", ""))

    if not name:
        print("nothing carvable in that title")
        return 0

    text = WALL.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("wall markers missing", file=sys.stderr)
        return 1

    head, rest = text.split(START, 1)
    body, tail = rest.split(END, 1)

    existing = [
        ln for ln in body.splitlines()
        if ln.strip().startswith("\u259a")
    ]

    entry = f"  \u259a {name:<25}@{login}" if login else f"  \u259a {name}"
    if entry in existing:
        print("already on the wall")
        return 0

    entries = ([entry] + existing)[:MAX_ENTRIES]
    block = "\n```text\n" + "\n".join(entries) + "\n```\n"

    WALL.write_text(head + START + block + END + tail, encoding="utf-8")
    print(f"carved: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
