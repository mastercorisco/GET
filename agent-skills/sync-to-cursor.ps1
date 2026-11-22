$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$repoRoot = Split-Path $root -Parent
$destRoot = Join-Path $repoRoot ".cursor\skills"
$manifestPath = Join-Path $root "MANIFEST.json"
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

if (-not (Test-Path $destRoot)) {
    New-Item -ItemType Directory -Path $destRoot -Force | Out-Null
}

foreach ($skill in $manifest.skills) {
    $src = Join-Path $root $skill
  if (-not (Test-Path $src)) {
        throw "Skill em falta: $skill"
    }
    $dest = Join-Path $destRoot $skill
    if (Test-Path $dest) {
        Remove-Item $dest -Recurse -Force
    }
    Copy-Item $src $dest -Recurse -Force
    Write-Host "Synced $skill -> $dest"
}

Write-Host "Done. Commit agent-skills/ and .cursor/skills/ together."