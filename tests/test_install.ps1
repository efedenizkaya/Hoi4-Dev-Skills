# Smoke test for install.ps1 — mirrors tests/test_install.sh.
# Invoked by pytest (tests/test_install_ps.py) and the Windows CI leg.
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("hoi4-install-" + [guid]::NewGuid())
try {
    & (Join-Path $repo "install.ps1") -Agent claude -HomeDir $tmp | Out-Null
    if (-not (Test-Path (Join-Path $tmp ".claude\skills\hoi4-modding\SKILL.md"))) { throw "claude install missing SKILL.md" }
    if (-not (Test-Path (Join-Path $tmp ".claude\skills\hoi4-modding\references\events.md"))) { throw "claude install missing reference" }

    & (Join-Path $repo "install.ps1") -Dest (Join-Path $tmp "anywhere") | Out-Null
    if (-not (Test-Path (Join-Path $tmp "anywhere\hoi4-modding\SKILL.md"))) { throw "dest install missing SKILL.md" }

    $out = & (Join-Path $repo "install.ps1") -Agent claude -HomeDir $tmp
    if (-not ($out -match "already installed")) { throw "second run not idempotent" }

    Write-Host "install.ps1 smoke test OK"
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
