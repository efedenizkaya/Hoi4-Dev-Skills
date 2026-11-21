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
    [string]$HomeDir = $env:USERPROFILE,
    [ValidateSet("install", "dry-run", "update", "uninstall", "list")]
    [string]$Mode = "install",
    [switch]$Force
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

$MANIFEST_NAME = ".hoi4-installer.json"

function Test-InstallerOwned {
    param([string]$Target)
    Test-Path (Join-Path $Target $MANIFEST_NAME)
}

function Install-To {
    param([string]$TargetDir)
    $target = Join-Path $TargetDir $skillName
    if ((Test-Path $target) -and -not (Test-InstallerOwned $target)) {
        if ($Force) {
            Write-Output "force: replacing foreign dir $target"
        } else {
            Write-Output "skip: $target exists and is NOT installer-managed (use -Force to replace)"
            return
        }
    }
    if ($Mode -eq "dry-run") {
        if (Test-Path $target) { Write-Output "would update: $target" }
        else { Write-Output "would install: $target" }
        return
    }
    if ($Mode -eq "update" -and -not (Test-Path $target)) { return }
    if (Test-Path $target) {
        Write-Output "already installed: $target (updating)"
        Remove-Item -Recurse -Force $target
    }
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Copy-Item -Recurse -Force $skillSrc $target
    Set-Content -Path (Join-Path $target $MANIFEST_NAME) `
        -Value ('{"tool": "hoi4-dev-skills installer", "installed_at": "' + [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ") + '"}')
    Write-Output "installed: $target"
}

function List-Agents {
    param([string]$Base)
    foreach ($entry in $agents.GetEnumerator()) {
        $state = if (Test-Path (Join-Path $Base "$($entry.Value)\$skillName")) { "installed" } else { "not installed" }
        Write-Output ("{0,-10} {1,-30} {2}" -f $entry.Key, (Join-Path $Base $entry.Value), $state)
    }
}

function Uninstall-All {
    param([string]$Base)
    $removed = 0
    foreach ($entry in $agents.GetEnumerator()) {
        if ($Agent -ne "" -and $entry.Key -ne $Agent) { continue }
        $target = Join-Path $Base "$($entry.Value)\$skillName"
        if (Test-Path $target) {
            if (Test-InstallerOwned $target) {
                Remove-Item -Recurse -Force $target
                Write-Output "removed: $target"
                $removed = 1
            } elseif ($Force) {
                Remove-Item -Recurse -Force $target
                Write-Output "force-removed foreign dir: $target"
                $removed = 1
            } else {
                Write-Output "skip: $target is not installer-managed (use -Force to remove)"
            }
        }
    }
    if ($removed -eq 0) { Write-Output "nothing to uninstall under $Base" }
}

if ($Mode -eq "list") {
    List-Agents $HomeDir
    exit 0
}
if ($Mode -eq "uninstall") {
    Uninstall-All $HomeDir
    exit 0
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
