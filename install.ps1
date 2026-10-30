# Install the hoi4-modding skill into AI agent skill directories (Windows).
# One stored copy (this repo) is copied out to each agent; re-run to update.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1              # all detected agents
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Agent claude
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Dest C:\some\dir
[CmdletBinding()]
param(
    [string]$Agent = "",
    [string]$Dest = "",
    [string]$HomeDir = $env:USERPROFILE
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSrc = Join-Path $root "skills\hoi4-modding"
$skillName = "hoi4-modding"

$agents = @{
    claude    = ".claude\skills"
    zcode     = ".agents\skills"
    codex     = ".codex\skills"
    cursor    = ".cursor\skills"
    gemini    = ".gemini\skills"
    opencode  = ".config\opencode\skills"
    copilot   = ".copilot\skills"
}

function Install-To {
    param([string]$TargetDir)
    $target = Join-Path $TargetDir $skillName
    if (Test-Path $target) {
        Write-Output "already installed: $target (updating)"
        Remove-Item -Recurse -Force $target
    }
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Copy-Item -Recurse -Force $skillSrc $target
    Write-Output "installed: $target"
}

if ($Dest -ne "") {
    Install-To $Dest
    exit 0
}

$found = 0
foreach ($entry in $agents.GetEnumerator()) {
    if ($Agent -ne "" -and $entry.Key -ne $Agent) { continue }
    $topDir = $entry.Value.Split("\")[0]
    $base = Join-Path $HomeDir $topDir
    if ((Test-Path $base) -or ($Agent -eq $entry.Key)) {
        Install-To (Join-Path $HomeDir $entry.Value)
        $found = 1
    }
}

if ($found -eq 0) {
    Write-Output "no supported agent directories found under $HomeDir."
    Write-Output "install manually with -Dest, or name an agent: $($agents.Keys -join ', ')"
    exit 1
}
