# Smoke test for install.ps1 — mirrors tests/test_install.sh.
# Invoked by pytest (tests/test_install_ps.py) and the Windows CI leg.
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("hoi4-install-" + [guid]::NewGuid())
try {
    & (Join-Path $repo "install.ps1") -Agent claude -HomeDir $tmp | Out-Null
    if (-not (Test-Path (Join-Path $tmp ".claude\skills\hoi4-modding\SKILL.md"))) { throw "claude install missing SKILL.md" }
    if (-not (Test-Path (Join-Path $tmp ".claude\skills\hoi4-modding\references\events.md"))) { throw "claude install missing reference" }

    # manifest written
    if (-not (Test-Path (Join-Path $tmp ".claude\skills\hoi4-modding\.hoi4-installer.json"))) { throw "manifest missing" }

    & (Join-Path $repo "install.ps1") -Dest (Join-Path $tmp "anywhere") | Out-Null
    if (-not (Test-Path (Join-Path $tmp "anywhere\hoi4-modding\SKILL.md"))) { throw "dest install missing SKILL.md" }

    $out = & (Join-Path $repo "install.ps1") -Agent claude -HomeDir $tmp
    if (-not ($out -match "already installed")) { throw "second run not idempotent" }

    # scoped uninstall: gemini survives claude uninstall
    & (Join-Path $repo "install.ps1") -Agent gemini -HomeDir $tmp | Out-Null
    & (Join-Path $repo "install.ps1") -Mode uninstall -Agent claude -HomeDir $tmp | Out-Null
    if (Test-Path (Join-Path $tmp ".claude\skills\hoi4-modding")) { throw "claude not removed" }
    if (-not (Test-Path (Join-Path $tmp ".gemini\skills\hoi4-modding\SKILL.md"))) { throw "gemini wrongly removed" }

    # foreign dir protected
    New-Item -ItemType Directory -Force -Path (Join-Path $tmp ".cursor\skills\hoi4-modding") | Out-Null
    Set-Content -Path (Join-Path $tmp ".cursor\skills\hoi4-modding\user_file.txt") -Value "USER"
    & (Join-Path $repo "install.ps1") -Mode uninstall -Agent cursor -HomeDir $tmp | Out-Null
    if (-not (Test-Path (Join-Path $tmp ".cursor\skills\hoi4-modding\user_file.txt"))) { throw "foreign dir wiped" }

    # dry-run does not install
    & (Join-Path $repo "install.ps1") -Mode dry-run -Agent codex -HomeDir $tmp | Out-Null
    if (Test-Path (Join-Path $tmp ".codex\skills\hoi4-modding")) { throw "dry-run installed" }

    Write-Host "install.ps1 smoke test OK"
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
