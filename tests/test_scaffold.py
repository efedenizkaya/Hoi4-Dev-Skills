from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scaffold_files_exist():
    for p in [
        "LICENSE",
        "README.md",
        "metadata.json",
        ".gitignore",
        "requirements-dev.txt",
        "tools/__init__.py",
        "tests/__init__.py",
    ]:
        assert (ROOT / p).is_file(), p


def test_metadata_fields():
    import json

    m = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    assert m["name"] == "hoi4-dev-skills"
    assert m["license"] == "MIT"
    assert "gameVersion" in m


def test_gitignore_covers_generated_and_private():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in ["extracted/", "__pycache__/", ".superpowers/", ".pytest_cache/"]:
        assert entry in gi, entry
