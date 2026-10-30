"""Runs the install.ps1 smoke test via pytest (Windows / PowerShell)."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("powershell") is None, reason="powershell not available")
def test_install_ps1_smoke():
    proc = subprocess.run(
        [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ROOT / "tests" / "test_install.ps1"),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=180,
    )
    assert proc.returncode == 0, f"{proc.stdout}\n{proc.stderr}"
    assert "install.ps1 smoke test OK" in proc.stdout
