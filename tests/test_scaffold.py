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


def test_versions_consistent():
    import json
    import re

    meta = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    # regex parse instead of tomllib: the suite must also run on Python
    # 3.10 (requires-python floor), where tomllib does not exist
    m = re.search(r'^version = "([^"]+)"', pyproject_text, re.M)
    assert m, "pyproject.toml must declare a project version"
    assert m.group(1) == meta["version"]
