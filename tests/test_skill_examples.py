"""Automated audit of reference code blocks against REAL game data.

Every fenced code block in the references is checked:
1. all GFX_* tokens must exist in the real game's sprite inventory
   (interface + dlc) or be declared in the kit fixtures;
2. all effect/trigger-looking statement names in blocks must exist in the
   extracted 1.19.4.1 database (effects.json/triggers.json), skipping
   synthetic namespace tokens (`mymod_*`, `<placeholder>`, structural
   fields).

This replaces the manual "brace-balanced + eyeballed" audit."""

import json
import re
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "hoi4-modding"
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
EXTRACTED = Path(__file__).resolve().parents[1] / "extracted" / "1.19.4.1"

needs_game = pytest.mark.skipif(
    not (GAME / "launcher-settings.json").is_file(), reason="game install not present")


def _fenced_blocks() -> list[tuple[str, int, str]]:
    out = []
    for md in sorted((SKILL / "references").glob("*.md")):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        start = 0
        buf: list[str] = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                if in_fence:
                    out.append((md.name, start, "\n".join(buf)))
                    in_fence = False
                    buf = []
                else:
                    in_fence = True
                    start = i
                    buf = []
            elif in_fence:
                buf.append(line)
    return out


def _known_sprites() -> set[str]:
    names = set()
    for root in [GAME / "interface", GAME / "dlc"]:
        if root.is_dir():
            for p in root.glob("**/*.gfx"):
                names.update(re.findall(r'name\s*=\s*"(GFX_[\w.\-]+)"',
                                        p.read_text(encoding="utf-8-sig", errors="replace")))
    return names


def _known_api() -> set[str]:
    known = set()
    for f in ("effects.json", "triggers.json"):
        p = EXTRACTED / f
        if p.is_file():
            known |= {e["name"] for e in json.loads(p.read_text(encoding="utf-8"))}
    return known


def _synthetic(name: str) -> bool:
    return (
        name.startswith(("mymod", "mymod_", "mod_", "<", "$", "@"))
        or "yourmod" in name
        or name in {"id", "title", "desc", "text", "name", "icon", "picture",
                    "option", "trigger", "limit", "factor", "cost", "x", "y",
                    "type", "value", "tag", "days", "hours"}
    )


# placeholders that are part of the game's own docs or clearly synthetic
# placeholders from the game's own docs, synthetic examples, and base
# names the game suffixes at runtime (GFX_upgrade_frame_* -> _completed...)
_GFX_ALLOWED = re.compile(
    r"(?:mymod|my_leader|my_|GFX_ref|special_project_id|upgrade_frame_)")


@needs_game
def test_reference_gfx_tokens_exist_in_game():
    sprites = _known_sprites()
    bad = []
    for fname, line, block in _fenced_blocks():
        for m in re.finditer(r"GFX_[\w.\-]+", block):
            token = m.group(0)
            if token in sprites or _GFX_ALLOWED.search(token):
                continue
            bad.append(f"{fname}:{line}: {token}")
    assert bad == [], "phantom sprites in reference code blocks:\n" + "\n".join(bad)


# effect-context headers whose depth-1 statements are real effects
_EFFECT_CONTEXT_RE = re.compile(
    r"(?:option|immediate|completion_reward|complete_effect|remove_effect"
    r"|on_add|on_research_complete)\s*=\s*\{")


@needs_game
def test_reference_effect_names_exist_in_extracted_db():
    known = _known_api()
    if not known:
        pytest.skip("no extracted data on this machine")
    bad = []
    for fname, line, block in _fenced_blocks():
        masked = re.sub(r"#.*", "", block)
        for m in _EFFECT_CONTEXT_RE.finditer(masked):
            # brace-match the block (snippets may be incomplete at the tail)
            depth = 0
            end = len(masked)
            for i in range(m.end() - 1, len(masked)):
                if masked[i] == "{":
                    depth += 1
                elif masked[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            body = masked[m.end():end]
            for sm in re.finditer(r"(?m)^\s*([a-z][\w]+)\s*=\s*(?:\{|\d|yes|no|-)", body):
                name = sm.group(1)
                if _synthetic(name) or name in known:
                    continue
                bad.append(f"{fname}:{line}: {name}")
    assert bad == [], "unknown effect/statement names in reference blocks:\n" + "\n".join(bad)
