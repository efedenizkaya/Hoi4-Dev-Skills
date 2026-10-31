"""Static validator for HOI4 mods: fast, dependency-free checks.

This is layer one of the verification loop — instant, agent-callable
syntax/consistency checks. It does not replace the game's own judgment
(launch with ``-debug`` and diff ``error.log``) or deep tooling such as
CWTools; it catches the mechanical mistakes first so the expensive checks
run less often.

Usage:
    python tools/validate.py <mod_dir> [--data <extracted_data_dir>]
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Paradox script files the rules below apply to, relative to the mod root.
SCRIPT_GLOBS = ["**/*.txt"]
LOC_GLOBS = ["localisation/**/*.yml", "localisation/**/*.yaml"]

_EVENT_HEADER_RE = re.compile(
    r"\b(country_event|news_event|state_event|unit_leader_event)\s*=\s*\{"
)
_EVENT_BODY_ID_RE = re.compile(r"\bid\s*=\s*([\w.\-]+)")


def _event_ids_in(masked: str, header_match: re.Match) -> list[tuple[str, int]]:
    """`id = X` entries that are direct children of the event block — `id`
    may legally follow nested blocks (immediate etc.), so search the balanced
    body at depth 0, but NOT ids inside nested blocks (those belong to
    firing effects like `country_event = { id = x days = 3 }` in options)."""
    start = header_match.end()
    end = _extract_block(masked, header_match.end() - 1)
    body = masked[start:end]
    out = []
    for m in _EVENT_BODY_ID_RE.finditer(body):
        if body.count("{", 0, m.start()) != body.count("}", 0, m.start()):
            continue
        out.append((m.group(1), masked.count("\n", 0, start + m.start()) + 1))
    return out
# Loc refs used by events: title/desc/name = <namespace>.<n>[.<letter>]
_LOC_REF_RE = re.compile(
    r"^\s*(?:title|desc|name)\s*=\s*([A-Za-z][\w]*\.\d+(?:\.[A-Za-z0-9_]+)?)\s*(?:#.*)?$",
    re.M,
)
_LOC_KEY_RE = re.compile(r"^\s*([A-Za-z][\w.\-]*):\d*\s*\"", re.M)


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    rule: str
    file: str
    line: int | None
    message: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def mask_comments_and_strings(text: str) -> str:
    """Return text of equal length with comments and string *contents* blanked.

    Both quote characters of a string are KEPT, so counting quotes in the
    masked text counts unclosed strings: a paired string contributes 2, an
    unclosed one 1 (everything it swallowed was blanked). ``#`` outside a
    string starts a comment (to end of line); inside a string it is literal.
    Blanking instead of deleting preserves line/column data.
    """
    out = list(text)
    in_string = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_string:
            if ch == "\\" and i + 1 < n and text[i + 1] == '"':
                # escaped quote: string continues; blank both chars
                out[i] = " "
                out[i + 1] = " "
                i += 2
                continue
            if ch == '"':
                in_string = False
            elif ch != "\n":
                out[i] = " "
        else:
            if ch == '"':
                in_string = True
            elif ch == "#":
                while i < n and text[i] != "\n":
                    out[i] = " "
                    i += 1
                continue
        i += 1
    return "".join(out)


def _check_balance(rel: str, text: str, findings: list[Finding]) -> None:
    masked = mask_comments_and_strings(text)
    braces = masked.count("{") - masked.count("}")
    if braces != 0:
        findings.append(
            Finding(
                severity="error",
                rule="unbalanced-braces",
                file=rel,
                line=None,
                message=f"{braces:+d} unmatched brace(s)",
            )
        )
    quotes = masked.count('"')
    if quotes % 2 != 0:
        findings.append(
            Finding(
                severity="error",
                rule="unbalanced-quotes",
                file=rel,
                line=None,
                message=f"{quotes} quote char(s) — odd count",
            )
        )


def _brace_depth_at(text: str, pos: int) -> int:
    depth = 0
    for ch in text[:pos]:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
    return depth


def _check_duplicate_event_ids(
    mod_dir: Path, findings: list[Finding], game_event_ids: set[str] | None = None
) -> None:
    seen: dict[str, list[tuple[str, int]]] = {}
    for path in sorted(mod_dir.glob("events/**/*.txt")):
        text = _read(path)
        masked = mask_comments_and_strings(text)
        # incremental brace depth — _brace_depth_at per header would be O(n^2)
        # on thousands-of-events files
        depth = 0
        last = 0
        for m in _EVENT_HEADER_RE.finditer(masked):
            depth += masked.count("{", last, m.start()) - masked.count("}", last, m.start())
            last = m.start()
            if depth > 0:
                # inside another block: this is the `country_event` FIRING
                # effect (e.g. within an option), not an event definition.
                continue
            for event_id, line in _event_ids_in(masked, m):
                seen.setdefault(event_id, []).append((str(path.relative_to(mod_dir)), line))
    for event_id, spots in sorted(seen.items()):
        if len(spots) == 1 and game_event_ids and event_id in game_event_ids:
            # Redefining a base-game event once is the standard way to
            # override it — intentional, so only a warning.
            findings.append(
                Finding(
                    severity="warning",
                    rule="vanilla-event-override",
                    file=spots[0][0],
                    line=spots[0][1],
                    message=f"{event_id}: overrides a base-game event (intentional?)",
                )
            )
        elif len(spots) > 1:
            files = ", ".join(f"{f}:{ln}" for f, ln in spots)
            findings.append(
                Finding(
                    severity="error",
                    rule="duplicate-event-id",
                    file=spots[0][0],
                    line=spots[0][1],
                    message=f"{event_id}: defined {len(spots)} times ({files})",
                )
            )


def _load_event_ids_from(events_dir: Path) -> set[str]:
    ids: set[str] = set()
    if not events_dir.is_dir():
        return ids
    for path in sorted(events_dir.glob("**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        for m in _EVENT_HEADER_RE.finditer(masked):
            ids.update(event_id for event_id, _ in _event_ids_in(masked, m))
    return ids


def _load_loc_keys(
    mod_dir: Path, findings: list[Finding], game_dir: Path | None = None
) -> set[str]:
    keys: set[str] = set()
    for pattern in LOC_GLOBS:
        for path in mod_dir.glob(pattern):
            raw = path.read_bytes()
            if not raw.startswith(b"\xef\xbb\xbf"):
                findings.append(
                    Finding(
                        severity="warning",
                        rule="loc-file-encoding",
                        file=str(path.relative_to(mod_dir)),
                        line=None,
                        message="localisation file has no UTF-8 BOM (game requires it)",
                    )
                )
            text = raw.decode("utf-8-sig", errors="replace")
            keys.update(_LOC_KEY_RE.findall(text))
    if game_dir is not None:
        # Base-game keys count as defined: mods may reference them when they
        # copy or extend vanilla events. Game files are never BOM-checked.
        # Key sets are identical across language folders, so reading one is
        # enough — `english` when present, everything otherwise.
        game_loc = game_dir / "localisation"
        roots = [game_loc / "english"] if (game_loc / "english").is_dir() else [game_loc]
        for root in roots:
            for path in root.glob("**/*.yml"):
                text = path.read_text(encoding="utf-8-sig", errors="replace")
                keys.update(_LOC_KEY_RE.findall(text))
    return keys


_DESC_BLOCK_RE = re.compile(r"\bdesc\s*=\s*\{")


def _check_loc_refs(mod_dir: Path, keys: set[str], findings: list[Finding]) -> None:
    for path in sorted(mod_dir.glob("events/**/*.txt")):
        text = _read(path)
        masked = mask_comments_and_strings(text)
        rel = str(path.relative_to(mod_dir))
        for m in _LOC_REF_RE.finditer(masked):
            key = m.group(1)
            if key not in keys:
                line = masked.count("\n", 0, m.start()) + 1
                findings.append(
                    Finding(
                        severity="error",
                        rule="missing-loc-key",
                        file=rel,
                        line=line,
                        message=f"{key}: not found in any localisation file",
                    )
                )
        # conditional descriptions: desc = { text = key trigger = {...} }
        # (512 uses in vanilla events)
        for m in _DESC_BLOCK_RE.finditer(masked):
            end = _extract_block(masked, m.end() - 1)
            body = masked[m.end():end]
            for tm in re.finditer(r"(?m)^\s*text\s*=\s*([\w.\-]+)", body):
                key = tm.group(1)
                if key not in keys:
                    line = masked.count("\n", 0, m.end() + tm.start()) + 1
                    findings.append(
                        Finding(
                            severity="error",
                            rule="missing-loc-key",
                            file=rel,
                            line=line,
                            message=f"{key}: not found in any localisation file",
                        )
                    )


_FOCUS_DEF_RE = re.compile(r"\b(?:focus|shared_focus|joint_focus)\s*=\s*\{")
_FOCUS_ID_RE = re.compile(r"\bid\s*=\s*([\w.\-]+)")
_FOCUS_ME_RE = re.compile(r"mutually_exclusive\s*=\s*\{([^{}]*)\}")
_FOCUS_PREREQ_RE = re.compile(r"prerequisite\s*=\s*\{([^{}]*)\}")
_FOCUS_POS_RE = re.compile(r"\b([xy])\s*=\s*(-?\d+)")
_FOCUS_TARGET_RE = re.compile(r"\bfocus\s*=\s*([\w.\-]+)")


def _extract_block(text: str, open_brace: int) -> int:
    """Return the index of the closing brace matching the one at open_brace."""
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text)


def _collect_focuses(
    mod_dir: Path, findings: list[Finding] | None = None
) -> dict[str, dict]:
    """Scan common/national_focus/**/*.txt for focus definitions.

    Returns id -> {x, y, relative: bool, me, prereq, file, line}.
    Duplicate ids produce a `duplicate-focus-id` error when `findings` is
    given (the game silently keeps one, so this is easy to miss).
    """
    focuses: dict[str, dict] = {}
    for path in sorted(mod_dir.glob("common/national_focus/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _FOCUS_DEF_RE.finditer(masked):
            end = _extract_block(masked, m.end() - 1)
            body = masked[m.end():end]
            id_m = _FOCUS_ID_RE.search(body)
            if not id_m:
                continue
            fid = id_m.group(1)
            # grid x/y must come from the focus's own top level — an
            # `offset = { x y trigger }` block is a conditional pixel nudge
            # and its values must NOT overwrite the grid position
            depth = 0
            pos: dict[str, str] = {}
            for km in re.finditer(r"([{}])|(?m:^[ \t]*)([xy])\s*=\s*(-?\d+)", body):
                if km.group(1):
                    depth += 1 if km.group(1) == "{" else -1
                    continue
                if depth == 0:
                    pos[km.group(2)] = km.group(3)
            entry = {
                "x": pos.get("x"),
                "y": pos.get("y"),
                "relative": "relative_position_id" in body,
                "me": set(_FOCUS_TARGET_RE.findall(
                    " ".join(_FOCUS_ME_RE.findall(body)))),
                "prereq": set(_FOCUS_TARGET_RE.findall(
                    " ".join(_FOCUS_PREREQ_RE.findall(body)))),
                "file": rel,
                "line": masked.count("\n", 0, m.end() + id_m.start()) + 1,
            }
            if fid in focuses and findings is not None:
                findings.append(
                    Finding(
                        severity="error",
                        rule="duplicate-focus-id",
                        file=rel,
                        line=entry["line"],
                        message=(
                            f"{fid}: focus id already defined at "
                            f"{focuses[fid]['file']}:{focuses[fid]['line']}"
                        ),
                    )
                )
            focuses[fid] = entry
    return focuses


def _check_focus_tree(
    mod_dir: Path, findings: list[Finding], game_dir: Path | None = None
) -> None:
    focuses = _collect_focuses(mod_dir, findings)
    if not focuses:
        return
    # vanilla focuses are legitimate prerequisite/exclusivity targets
    known = set(focuses)
    if game_dir is not None:
        known |= set(_collect_focuses(game_dir))
    for fid, f in focuses.items():
        for target in sorted(f["prereq"]):
            if target not in known:
                findings.append(
                    Finding(
                        severity="error",
                        rule="missing-focus-prerequisite",
                        file=f["file"],
                        line=f["line"],
                        message=f"{fid}: prerequisite target '{target}' is not defined",
                    )
                )
        for target in sorted(f["me"]):
            if target in known and fid not in focuses.get(target, {}).get("me", set()):
                findings.append(
                    Finding(
                        severity="warning",
                        rule="unidirectional-mutual-exclusive",
                        file=f["file"],
                        line=f["line"],
                        message=(
                            f"{fid}: mutually exclusive with '{target}', "
                            f"but '{target}' does not declare it back "
                            "(vanilla declares both sides)"
                        ),
                    )
                )
    seen_pos: dict[tuple[str, str], list[str]] = {}
    for fid, f in focuses.items():
        # focuses positioned relative to another focus share no absolute grid
        # cell with a same-offset sibling under a different anchor
        if f["x"] is not None and f["y"] is not None and not f["relative"]:
            seen_pos.setdefault((f["x"], f["y"]), []).append(fid)
    for (x, y), ids in sorted(seen_pos.items()):
        if len(ids) > 1:
            first = focuses[sorted(ids)[0]]
            findings.append(
                Finding(
                    severity="warning",
                    rule="focus-position-overlap",
                    file=first["file"],
                    line=first["line"],
                    message=f"focuses share grid position x={x} y={y}: {', '.join(sorted(ids))}",
                )
            )


# Script block types whose statements are EFFECTS (scripted-GUI and
# on_action effect bodies use the same grammar).
_EFFECT_CONTEXT_RE = re.compile(
    r"\b(?:option|immediate|completion_reward|complete_effect|remove_effect"
    r"|timeout_effect|on_add|on_remove|on_research_complete|doctrine_effects"
    r"|hidden_effect|effect)\s*=\s*\{"
)
_STATEMENT_RE = re.compile(r"(?m)^\s*([a-z0-9_]+)\s*=")
# Fields that are structural inside effect contexts, not effect names.
_EFFECT_CONTEXT_FIELDS = {
    "name", "trigger", "ai_chance", "limit", "custom_tooltip", "tooltip",
    "else", "else_if", "text_icon", "id",
}
_SCRIPT_GLOB_EFFECT_CONTEXT = [
    "events/**/*.txt",
    "common/scripted_effects/**/*.txt",
    "common/decisions/**/*.txt",
    "common/on_actions/**/*.txt",
    "common/national_focus/**/*.txt",
    "common/ideas/**/*.txt",
]
_HAS_COMPLETED_FOCUS_RE = re.compile(r"\bhas_completed_focus\s*=\s*([\w.\-]+)")


_TOP_LEVEL_STMT_RE = re.compile(r"([{}])|^\s*([a-z0-9_]+)\s*=", re.M)


def _top_level_names(path: Path) -> set[str]:
    """Names defined at the top level of a script file (scripted
    effects/triggers, decision blocks)."""
    masked = mask_comments_and_strings(_read(path))
    names: set[str] = set()
    depth = 0
    for m in _TOP_LEVEL_STMT_RE.finditer(masked):
        if m.group(1) == "{":
            depth += 1
        elif m.group(1) == "}":
            depth -= 1
        elif m.group(2) and depth == 0:
            names.add(m.group(2))
    return names


def _load_scripted_names(mod_dir: Path) -> set[str]:
    names: set[str] = set()
    for pattern in ["common/scripted_effects/**/*.txt",
                    "common/scripted_triggers/**/*.txt"]:
        for path in mod_dir.glob(pattern):
            names |= _top_level_names(path)
    return names


def _check_statement_names(
    mod_dir: Path, findings: list[Finding],
    known: set[str], scripted: set[str],
) -> None:
    """Warn on lowercase statement names in effect contexts that are in
    neither the version's effect list nor the mod's scripted effects.
    Warnings-only: block fields, scope tags (UPPERCASE), aliases (@) and
    trigger sub-blocks are skipped."""
    if not known:
        return
    for pattern in _SCRIPT_GLOB_EFFECT_CONTEXT:
        for path in sorted(mod_dir.glob(pattern)):
            masked = mask_comments_and_strings(_read(path))
            rel = str(path.relative_to(mod_dir))
            for block in _EFFECT_CONTEXT_RE.finditer(masked):
                end = _extract_block(masked, block.end() - 1)
                body = masked[block.end():end]
                # cut out trigger/ai_chance sub-blocks (trigger grammar there)
                cleaned = []
                pos = 0
                for sub in re.finditer(r"\b(?:trigger|ai_chance)\s*=\s*\{", body):
                    sub_end = _extract_block(body, sub.end() - 1)
                    cleaned.append(body[pos:sub.start()])
                    # _extract_block returns the index OF the closing brace;
                    # skip past it or the stray brace corrupts depth counting
                    pos = max(pos, sub_end + 1)
                cleaned.append(body[pos:])
                body = "".join(cleaned)
                # depth 1 only: nested blocks (e.g. the argument schema of
                # add_building_construction) have their own field grammars.
                # One pass with a running depth instead of O(body^2) counts.
                depth = 0
                for m in re.finditer(r"([{}])|(?m:^)(\s*)([a-z0-9_]+)(?=\s*=)", body):
                    if m.group(1):
                        depth += 1 if m.group(1) == "{" else -1
                        continue
                    if depth > 0:
                        continue
                    name = m.group(3)
                    if (
                        name in known
                        or name in scripted
                        or name in _EFFECT_CONTEXT_FIELDS
                        or name.upper() == name
                        or name.startswith("@")
                    ):
                        continue
                    findings.append(
                        Finding(
                            severity="warning",
                            rule="unknown-statement-name",
                            file=rel,
                            line=masked.count("\n", 0, block.end() + m.start()) + 1,
                            message=(
                                f"{name}: not an effect in the extracted data "
                                "for this game version"
                            ),
                        )
                    )


def _load_known_names(data_dir: Path | None) -> set[str]:
    if data_dir is None:
        return set()
    known: set[str] = set()
    for json_name in ("effects.json", "triggers.json"):
        p = data_dir / json_name
        if p.is_file():
            known |= {e["name"] for e in json.loads(p.read_text(encoding="utf-8"))}
    return known


def _check_focus_references(
    mod_dir: Path, findings: list[Finding], game_dir: Path
) -> None:
    """has_completed_focus targets must exist in mod or vanilla trees.
    Requires the game dir (vanilla ids are legitimate targets)."""
    known = set(_collect_focuses(mod_dir)) | set(_collect_focuses(game_dir))
    for path in sorted(mod_dir.glob("**/*.txt")):
        if not path.is_file():
            continue
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _HAS_COMPLETED_FOCUS_RE.finditer(masked):
            token = m.group(1)
            if token not in known:
                findings.append(
                    Finding(
                        severity="warning",
                        rule="unknown-focus-reference",
                        file=rel,
                        line=masked.count("\n", 0, m.start()) + 1,
                        message=f"{token}: focus id not defined in mod or vanilla trees",
                    )
                )


def _check_event_namespaces(mod_dir: Path, findings: list[Finding]) -> None:
    """Every event file should declare its namespace(s) via add_namespace —
    all 128 vanilla event files do (short or block form)."""
    for path in sorted(mod_dir.glob("events/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        if "add_namespace" not in masked:
            findings.append(
                Finding(
                    severity="warning",
                    rule="missing-add-namespace",
                    file=str(path.relative_to(mod_dir)),
                    line=1,
                    message="no add_namespace declared (vanilla declares it in every event file)",
                )
            )


# ---- silent-failure rules: things the game ignores WITHOUT an error ----

_STRUCTURAL_MODIFIER_FIELDS = {
    "custom_modifier_tooltip", "add", "tag", "hidden_modifier", "has_variable",
}
_WEIGHT_CONTEXT_RE = re.compile(
    r"\b(?:ai_will_do|ai_chance|mean_time_to_happen)\s*=\s*\{"
)
_MODIFIER_BLOCK_RE = re.compile(r"\bmodifier\s*=\s*\{")
_MODIFIER_CONTEXT_GLOBS = [
    "common/ideas/**/*.txt",
    "common/dynamic_modifiers/**/*.txt",
    "common/military_industrial_organization/**/*.txt",
    "common/decisions/**/*.txt",
]
_SPRITE_DEF_RE = re.compile(r'name\s*=\s*"(GFX_[\w.\-]+)"')
_SPRITE_REF_RE = re.compile(r"\b(?:icon|picture|background)\s*=\s*(GFX_[\w.\-]+)")
_ON_ACTIONS_RE = re.compile(r"\bon_actions\s*=\s*\{")
_HOOK_NAME_RE = re.compile(r"([{}])|(?m:^)\s*([a-z0-9_]+)\s*=")


def _load_modifier_db(data_dir: Path) -> set[str]:
    if data_dir is None:
        return set()
    p = data_dir / "modifiers.json"
    if not p.is_file():
        return set()
    db = json.loads(p.read_text(encoding="utf-8"))
    known: set[str] = set()
    for names in db.values():
        known.update(names)
    return known


def _modifier_matches(name: str, known: set[str]) -> bool:
    if name in known:
        return True
    # templated names: <Building>_output matches arms_factory_output
    for k in known:
        if "<" in k:
            rx = re.sub(r"<[A-Za-z]+>", "[a-z0-9_]+", re.escape(k))
            if re.fullmatch(rx, name):
                return True
    return False


def _check_modifier_names(
    mod_dir: Path, findings: list[Finding], data_dir: Path | None
) -> None:
    """Modifier keys inside idea/dynamic-modifier/MIO blocks against the
    extracted modifiers database. The game silently ignores unknown names.
    Weight-grammar blocks (ai_will_do, tree country factors) are excluded."""
    known = _load_modifier_db(data_dir)
    if not known:
        return
    for pattern in _MODIFIER_CONTEXT_GLOBS:
        for path in sorted(mod_dir.glob(pattern)):
            masked = mask_comments_and_strings(_read(path))
            rel = str(path.relative_to(mod_dir))
            excluded = [
                (w.start(), _extract_block(masked, w.end() - 1))
                for w in _WEIGHT_CONTEXT_RE.finditer(masked)
            ]
            for m in _MODIFIER_BLOCK_RE.finditer(masked):
                if any(a <= m.start() < b for a, b in excluded):
                    continue
                end = _extract_block(masked, m.end() - 1)
                body = masked[m.end():end]
                depth = 0
                keys: list[str] = []
                for km in re.finditer(r"([{}])|(?m:^)\s*([a-z0-9_]+)\s*=", body):
                    if km.group(1):
                        depth += 1 if km.group(1) == "{" else -1
                        continue
                    if depth == 0:
                        keys.append(km.group(2))
                if keys and keys[0] in ("factor", "add"):
                    continue  # weight-style body
                for key in keys:
                    if key in _STRUCTURAL_MODIFIER_FIELDS:
                        continue
                    if _modifier_matches(key, known):
                        continue
                    findings.append(
                        Finding(
                            severity="warning",
                            rule="unknown-modifier-name",
                            file=rel,
                            line=masked.count("\n", 0, m.start()) + 1,
                            message=(
                                f"{key}: not a modifier name in the extracted "
                                "data — the game ignores it silently"
                            ),
                        )
                    )


def _load_sprite_names(mod_dir: Path, game_dir: Path) -> set[str]:
    names: set[str] = set()
    roots = [mod_dir / "interface", game_dir / "interface", game_dir / "dlc"]
    for root in roots:
        if root.is_dir():
            for path in root.glob("**/*.gfx"):
                names.update(_SPRITE_DEF_RE.findall(_read(path)))
    return names


def _check_sprite_references(
    mod_dir: Path, findings: list[Finding], game_dir: Path
) -> None:
    """icon/picture/background GFX references must be declared in some
    interface/*.gfx. A missing SPRITE NAME renders a placeholder with no
    error; only a missing texture file logs."""
    known = _load_sprite_names(mod_dir, game_dir)
    for path in sorted(mod_dir.glob("**/*.txt")):
        if not path.is_file():
            continue
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _SPRITE_REF_RE.finditer(masked):
            if m.group(1) not in known:
                findings.append(
                    Finding(
                        severity="warning",
                        rule="unknown-sprite",
                        file=rel,
                        line=masked.count("\n", 0, m.start()) + 1,
                        message=(
                            f"{m.group(1)}: sprite not declared in any mod or "
                            "vanilla .gfx — renders as placeholder, silently"
                        ),
                    )
                )


def _load_on_action_names(game_dir: Path) -> set[str]:
    names: set[str] = set()
    root = game_dir / "common" / "on_actions"
    if not root.is_dir():
        return names
    for path in root.glob("**/*.txt"):
        masked = mask_comments_and_strings(_read(path))
        m = _ON_ACTIONS_RE.search(masked)
        if not m:
            continue
        end = _extract_block(masked, m.end() - 1)
        body = masked[m.end():end]
        depth = 0
        for sm in _HOOK_NAME_RE.finditer(body):
            if sm.group(1):
                depth += 1 if sm.group(1) == "{" else -1
                continue
            if depth == 0:
                names.add(sm.group(2))
    return names


def _check_on_actions(
    mod_dir: Path, findings: list[Finding], game_dir: Path
) -> None:
    """Mod on_action hook names must exist in the vanilla hook list — a
    misspelled hook never fires and never logs."""
    known = _load_on_action_names(game_dir)
    if not known:
        return
    for path in sorted(mod_dir.glob("common/on_actions/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _ON_ACTIONS_RE.finditer(masked):
            end = _extract_block(masked, m.end() - 1)
            body = masked[m.end():end]
            depth = 0
            for sm in _HOOK_NAME_RE.finditer(body):
                if sm.group(1):
                    depth += 1 if sm.group(1) == "{" else -1
                    continue
                if depth != 0:
                    continue
                hook = sm.group(2)
                if hook not in known:
                    findings.append(
                        Finding(
                            severity="warning",
                            rule="unknown-on-action",
                            file=rel,
                            line=masked.count("\n", 0, m.start()) + 1,
                            message=(
                                f"{hook}: not a vanilla on_action hook — it "
                                "would never fire, silently"
                            ),
                        )
                    )


_LOC_HEADER_RE = re.compile(r"(?m)^\s*l_([a-z_]+)\s*:")


def _check_loc_hygiene(mod_dir: Path, findings: list[Finding]) -> None:
    """Per-file localisation hygiene: the `l_<lang>:` header must match the
    FIRST folder under localisation/ (subfolders beneath it like
    `english/events/` are normal), and duplicate keys within one file are
    almost always an overwrite bug. Files directly inside localisation/
    have no language folder and are exempt."""
    for path in sorted(mod_dir.glob("localisation/**/*.yml")):
        rel = str(path.relative_to(mod_dir))
        parts = path.relative_to(mod_dir / "localisation").parts
        if len(parts) < 2:
            continue  # directly in localisation/ — no language folder
        folder_lang = parts[0]
        if folder_lang == "replace":
            continue  # replace/ overrides every language by design
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        headers = _LOC_HEADER_RE.findall(text)
        if headers and headers[0] != folder_lang:
            findings.append(
                Finding(
                    severity="warning",
                    rule="loc-language-mismatch",
                    file=rel,
                    line=None,
                    message=f"header l_{headers[0]}: but file lives in localisation/{folder_lang}",
                )
            )
        seen: set[str] = set()
        for km in _LOC_KEY_RE.finditer(text):
            key = km.group(1)
            if key in seen:
                findings.append(
                    Finding(
                        severity="warning",
                        rule="duplicate-loc-key",
                        file=rel,
                        line=text.count("\n", 0, km.start()) + 1,
                        message=f"{key}: defined more than once in this file",
                    )
                )
            seen.add(key)


# ---- audit lints (roadmap item 8) ----

_REPLACE_PATH_RE = re.compile(r'replace_path\s*=\s*"([^"]+)"')
_EVENT_REF_RE = re.compile(
    r"\b(?:country_event|news_event|state_event|unit_leader_event)"
    r"\s*=\s*\{[^{}]*?\bid\s*=\s*([\w.\-]+)", re.S)
_IDEA_REF_RE = re.compile(
    r"\b(?:add_ideas|remove_ideas|has_idea)\s*=\s*([\w.\-]+)")
_EVENT_LOC_KEY_RE = re.compile(r"^[a-z0-9_]+\.\d+(\.[a-z0-9_]+)?$")


def _check_descriptor(mod_dir: Path, findings: list[Finding]) -> None:
    """replace_path skips vanilla content entirely — a destructive
    compatibility decision the user must confirm."""
    for path in sorted(mod_dir.glob("*.mod")):
        text = _read(path)
        for m in _REPLACE_PATH_RE.finditer(text):
            findings.append(
                Finding(
                    severity="warning",
                    rule="replace-path-used",
                    file=str(path.relative_to(mod_dir)),
                    line=text.count("\n", 0, m.start()) + 1,
                    message=f"replace_path '{m.group(1)}': skips vanilla "
                            "content entirely — compatibility risk",
                )
            )


def _idea_tokens(root: Path) -> set[str]:
    """Idea tokens: identifiers at depth 2 inside common/ideas files
    (category wrapper -> idea). Both wrapper and wrapper-less layouts
    exist (vanilla uses wrappers, many mods do not), so depth 1 and 2 are
    both collected."""
    toks: set[str] = set()
    for path in root.glob("common/ideas/**/*.txt"):
        masked = mask_comments_and_strings(_read(path))
        depth = 0
        for m in re.finditer(r"([{}])|(?m:^[ \t]*)([A-Za-z_][\w.]*)\s*=", masked):
            if m.group(1):
                depth += 1 if m.group(1) == "{" else -1
                continue
            if depth in (1, 2):
                toks.add(m.group(2))
    return toks


def _check_reference_targets(
    mod_dir: Path, findings: list[Finding], game_dir: Path,
    mod_event_ids: set[str],
) -> None:
    """Fired events and idea references must resolve to definitions in the
    mod or vanilla (needs the game dir — vanilla ids are legitimate)."""
    known_events = set(_load_event_ids_from(game_dir / "events")) | mod_event_ids
    known_ideas = _idea_tokens(game_dir) | _idea_tokens(mod_dir)

    for path in sorted(mod_dir.glob("events/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _EVENT_HEADER_RE.finditer(masked):
            if _brace_depth_at(masked, m.start()) == 0:
                continue  # a definition, not a firing reference
            for ref_id, _line in _event_ids_in(masked, m):
                if ref_id not in known_events:
                    findings.append(
                        Finding(
                            severity="warning",
                            rule="unknown-event-reference",
                            file=rel,
                            line=masked.count("\n", 0, m.start()) + 1,
                            message=f"{ref_id}: fired event is not defined "
                                    "in mod or vanilla",
                        )
                    )

    for path in sorted(mod_dir.glob("**/*.txt")):
        if not path.is_file():
            continue
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        for m in _IDEA_REF_RE.finditer(masked):
            token = m.group(1)
            if token not in known_ideas:
                findings.append(
                    Finding(
                        severity="warning",
                        rule="unknown-idea-reference",
                        file=rel,
                        line=masked.count("\n", 0, m.start()) + 1,
                        message=f"{token}: idea token not defined in mod or "
                                "vanilla",
                    )
                )


def _check_unused_event_loc(mod_dir: Path, findings: list[Finding]) -> None:
    """Event-pattern loc keys (ns.N[.letter]) referenced nowhere in the
    mod's events are leftovers. Dynamic-key construction makes general
    unused-loc detection unreliable, so this stays scoped to event keys."""
    script = "\n".join(
        _read(p) for p in sorted(mod_dir.glob("events/**/*.txt")) if p.is_file()
    )
    for path in sorted(mod_dir.glob("localisation/**/*.yml")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        rel = str(path.relative_to(mod_dir))
        for m in _LOC_KEY_RE.finditer(text):
            key = m.group(1)
            if _EVENT_LOC_KEY_RE.match(key) and key not in script:
                findings.append(
                    Finding(
                        severity="warning",
                        rule="unused-loc-key",
                        file=rel,
                        line=text.count("\n", 0, m.start()) + 1,
                        message=f"{key}: event-pattern key referenced by no "
                                "event file",
                    )
                )


def _check_periodic_hooks(mod_dir: Path, findings: list[Finding]) -> None:
    for path in sorted(mod_dir.glob("common/on_actions/**/*.txt")):
        masked = mask_comments_and_strings(_read(path))
        rel = str(path.relative_to(mod_dir))
        depth = 0
        for hm in re.finditer(r"([{}])|(?m:^)(\s*)([a-z0-9_]+)(?=\s*=)", masked):
            if hm.group(1):
                depth += 1 if hm.group(1) == "{" else -1
                continue
            if depth != 1:
                continue
            hook = hm.group(3)
            if hook in ("on_daily", "on_hourly"):
                findings.append(
                    Finding(
                        severity="warning",
                        rule="periodic-effect-performance",
                        file=rel,
                        line=masked.count("\n", 0, hm.start()) + 1,
                        message="(heuristic) " + hook + ": runs every game "
                                "hour/day per country — heavy effects here "
                                "hurt late-game performance",
                    )
                )


def validate_mod(
    mod_dir: Path, data_dir: Path | None = None, game_dir: Path | None = None
) -> list[Finding]:
    """Run all v1 rules over a mod directory and return the findings.

    ``data_dir`` (from tools/extract.py) is reserved for engine-derived rule
    data (e.g. known effect/trigger names); unused in v1. ``game_dir`` (the
    HOI4 install) enables base-game awareness: vanilla loc keys are accepted
    and single re-definitions of vanilla event IDs downgrade to warnings.
    """
    findings: list[Finding] = []
    for pattern in SCRIPT_GLOBS:
        for path in sorted(mod_dir.glob(pattern)):
            if not path.is_file():
                continue
            rel = str(path.relative_to(mod_dir))
            _check_balance(rel, _read(path), findings)

    game_event_ids = _load_event_ids_from(game_dir / "events") if game_dir else None
    _check_duplicate_event_ids(mod_dir, findings, game_event_ids)
    keys = _load_loc_keys(mod_dir, findings, game_dir)
    _check_loc_refs(mod_dir, keys, findings)
    _check_focus_tree(mod_dir, findings, game_dir)
    _check_event_namespaces(mod_dir, findings)
    _check_loc_hygiene(mod_dir, findings)
    _check_descriptor(mod_dir, findings)
    _check_periodic_hooks(mod_dir, findings)
    _check_unused_event_loc(mod_dir, findings)
    if data_dir is not None:
        known = _load_known_names(data_dir)
        scripted = _load_scripted_names(mod_dir)
        if game_dir is not None:
            scripted |= _load_scripted_names(game_dir)
        _check_statement_names(mod_dir, findings, known, scripted)
        _check_modifier_names(mod_dir, findings, data_dir)
    if game_dir is not None:
        _check_focus_references(mod_dir, findings, game_dir)
        _check_sprite_references(mod_dir, findings, game_dir)
        _check_on_actions(mod_dir, findings, game_dir)
        mod_event_ids = {
            eid
            for _p in sorted(mod_dir.glob('events/**/*.txt'))
            if _p.is_file()
            for _h in _EVENT_HEADER_RE.finditer(mask_comments_and_strings(_read(_p)))
            if _brace_depth_at(mask_comments_and_strings(_read(_p)), _h.start()) == 0
            for eid, _ in _event_ids_in(mask_comments_and_strings(_read(_p)), _h)
        }
        _check_reference_targets(mod_dir, findings, game_dir, mod_event_ids)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Static HOI4 mod validator")
    parser.add_argument("mod_dir", type=Path)
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=None,
        help="HOI4 install root (auto-detected when omitted)",
    )
    parser.add_argument(
        "--no-game", action="store_true", help="skip base-game awareness"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print findings as a JSON list (for agents/CI)",
    )
    args = parser.parse_args(argv)

    if not args.mod_dir.is_dir():
        print(f"error: {args.mod_dir} is not a mod directory", file=sys.stderr)
        return 2

    game_dir: Path | None = args.game_dir
    if not args.no_game and game_dir is None:
        try:
            from .extract import find_game_dir
        except ImportError:
            from extract import find_game_dir
        game_dir = find_game_dir()
    if args.game_dir is not None and not (args.game_dir / "launcher-settings.json").is_file():
        print(
            f"warning: --game-dir {args.game_dir} is not a HOI4 install "
            "(no launcher-settings.json) — vanilla-aware checks are disabled",
            file=sys.stderr,
        )
        game_dir = None
    if args.data is not None and not (args.data / "effects.json").is_file():
        print(
            f"error: --data {args.data} contains no effects.json — run "
            "tools/extract.py first or fix the path",
            file=sys.stderr,
        )
        return 2

    findings = validate_mod(args.mod_dir, args.data, game_dir)
    if args.json:
        print(json.dumps([
            {
                "severity": f.severity,
                "rule": f.rule,
                "file": f.file,
                "line": f.line,
                "message": f.message,
            }
            for f in findings
        ], ensure_ascii=False, indent=1))
    else:
        for f in findings:
            loc = f"{f.file}:{f.line}" if f.line is not None else f.file
            print(f"[{f.severity.upper()}] {f.rule} {loc}: {f.message}")
        errors = sum(1 for f in findings if f.severity == "error")
        warnings = len(findings) - errors
        print(f"\n{errors} error(s), {warnings} warning(s)")
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
