"""Runs the install.sh smoke test (tests/test_install.sh) via pytest so the
whole suite stays the single test entry point. Requires bash (Git Bash on
Windows; standard on Linux/macOS CI)."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
def test_install_sh_smoke():
    proc = subprocess.run(
        ["bash", str(ROOT / "tests" / "test_install.sh")],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=120,
    )
    assert proc.returncode == 0, f"{proc.stdout}\n{proc.stderr}"
    assert "install.sh smoke test OK" in proc.stdout
