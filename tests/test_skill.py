"""Structural lint for the hoi4-modding skill: spec compliance, link
integrity, claims-register coverage, kit completeness."""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "hoi4-modding"
SKILL_MD = SKILL_DIR / "SKILL.md"
DOCS = Path(__file__).resolve().parents[1] / "docs"

def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must open with YAML frontmatter"
    block = m.group(1)
    meta = {}
    for line in block.splitlines():
        if line.startswith("  ") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta


def test_every_reference_is_routed():
    """Each references/*.md must appear in the SKILL.md routing table."""
    routing = SKILL_MD.read_text(encoding="utf-8")
    for ref in (SKILL_DIR / "references").glob("*.md"):
        assert f"references/{ref.name}" in routing, ref.name


def test_frontmatter_spec_compliant():
    text = SKILL_MD.read_text(encoding="utf-8")
    meta = _frontmatter(text)
    assert meta["name"] == "hoi4-modding"
    assert meta["name"] == SKILL_DIR.name
    assert 0 < len(meta["description"]) <= 1024
    assert meta["license"] == "MIT"


def test_body_under_500_lines():
    text = SKILL_MD.read_text(encoding="utf-8")
    body = text.split("---\n", 2)[2]
    assert body.count("\n") < 500


def test_references_exist_and_are_focused():
    refs = sorted((SKILL_DIR / "references").glob("*.md"))
    assert len(refs) >= 4
    for ref in refs:
        assert ref.read_text(encoding="utf-8").count("\n") < 400, ref.name


def test_relative_links_resolve():
    for md in [SKILL_MD, *(SKILL_DIR / "references").glob("*.md")]:
        text = md.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(((?:references|assets|docs)/[^)#]+)\)", text):
            # links in SKILL.md and references are relative to the skill dir
            resolved = SKILL_DIR / target
            assert resolved.exists(), f"{md.name}: broken link {target}"


def test_claims_marked_in_references_are_registered():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for ref in (SKILL_DIR / "references").glob("*.md"):
        text += ref.read_text(encoding="utf-8")
    claimed = set(re.findall(r"CLAIM\(([\w-]+)\)", text))
    assert claimed, "references must carry CLAIM markers"
    register = (DOCS / "claims-register.md").read_text(encoding="utf-8")
    registered = set(re.findall(r"^\|\s*([\w-]+)\s*\|", register, re.M))
    assert claimed <= registered, claimed - registered


def test_kits_complete_per_manifest():
    kits = sorted((SKILL_DIR / "assets" / "kits").glob("*"))
    assert len(kits) >= 2
    for kit in kits:
        manifest = kit / "MANIFEST"
        assert manifest.is_file(), kit.name
        for rel in manifest.read_text(encoding="utf-8").split():
            assert (kit / rel).is_file(), f"{kit.name}/{rel}"
        for rel in manifest.read_text(encoding="utf-8").split():
            assert not rel.startswith("/"), f"{kit.name}: manifest paths must be relative"
