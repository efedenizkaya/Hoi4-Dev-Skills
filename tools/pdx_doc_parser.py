"""Parser for the official documentation markdown files shipped inside the
Hearts of Iron IV install (``documentation/*.md``).

The game regenerates these files at runtime, so anything parsed from them is
accurate for the installed patch. Nothing parsed here is ever committed to
the repository — see the design spec for the licensing rationale.

Confirmed file shapes (game 1.19.4.1):

- effects/triggers: ``## <name>`` entries with ``* Supported Scopes: A, B``
  and ``* Supported Targets: X, Y`` bullets, followed by one fenced code
  block holding the description and example.
- modifiers: ``## Modifiers for scope <scope>`` sections whose content is a
  ``* [name](#anchor)`` list; templated entries look like
  ``<Building>_max_level_terrain_limit``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Doc file stem -> entry kind parsed from it.
GAME_DOC_FILES: dict[str, str] = {
    "effects_documentation": "effect",
    "triggers_documentation": "trigger",
}

# `## <header>` lines that mark sections, not parseable entries.
_SECTION_HEADER = re.compile(r"^(Table of Content|\w+ for scope .+)$")

_BULLET_SCOPES = re.compile(r"\*\s*Supported Scopes:\s*(.+)")
_BULLET_TARGETS = re.compile(r"\*\s*Supported Targets:\s*(.+)")
_MODIFIER_ITEM = re.compile(r"\*\s*\[(.+?)\]\(")


@dataclass
class DocEntry:
    name: str
    kind: str  # "effect" | "trigger"
    scopes: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    description: str = ""


def _read_text(path: Path) -> str:
    # utf-8-sig strips the BOM the game writes on Windows; universal newlines
    # fold CRLF into LF.
    return path.read_text(encoding="utf-8-sig")


def _split_entries(text: str) -> list[tuple[str, list[str]]]:
    """Split into (header, body_lines) pairs.

    A line starting with ``## `` only opens a new entry when it is *outside*
    a fenced code block — descriptions may contain markdown-looking lines.
    """
    blocks: list[tuple[str, list[str]]] = []
    in_fence = False
    current_header: str | None = None
    current_body: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if current_header is not None:
                blocks.append((current_header, current_body))
            current_header = line[3:].strip()
            current_body = []
        elif current_header is not None:
            current_body.append(line)
    if current_header is not None:
        blocks.append((current_header, current_body))
    return blocks


def _first_fenced_block(body_lines: list[str]) -> str:
    lines: list[str] = []
    in_fence = False
    for line in body_lines:
        if line.strip().startswith("```"):
            if in_fence:
                break
            in_fence = True
            continue
        if in_fence:
            lines.append(line)
    return "\n".join(lines).strip()


def _split_csv(value: str) -> list[str]:
    if value.strip().lower() == "none":
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_effects_or_triggers(path: Path, kind: str) -> list[DocEntry]:
    """Parse an effects/triggers documentation file into entries."""
    entries: list[DocEntry] = []
    for header, body in _split_entries(_read_text(path)):
        if _SECTION_HEADER.match(header):
            continue
        scopes: list[str] = []
        targets: list[str] = []
        for line in body:
            m = _BULLET_SCOPES.match(line.strip())
            if m:
                scopes = _split_csv(m.group(1))
                continue
            m = _BULLET_TARGETS.match(line.strip())
            if m:
                targets = _split_csv(m.group(1))
        entries.append(
            DocEntry(
                name=header,
                kind=kind,
                scopes=scopes,
                targets=targets,
                description=_first_fenced_block(body),
            )
        )
    return entries


def parse_modifiers(path: Path) -> dict[str, list[str]]:
    """Parse a modifiers documentation file into scope -> sorted names."""
    result: dict[str, list[str]] = {}
    scope: str | None = None
    for line in _read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            header = stripped[3:].strip()
            m = re.match(r"^Modifiers for scope (.+)$", header)
            scope = m.group(1).strip() if m else None
            if scope and scope not in result:
                result[scope] = []
        elif scope is not None and stripped.startswith("* ["):
            m = _MODIFIER_ITEM.match(stripped)
            if m:
                name = m.group(1).strip()
                if name not in result[scope]:
                    result[scope].append(name)
    for names in result.values():
        names.sort()
    return result
