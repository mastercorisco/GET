#Requires -Version 5.1
<#
.SYNOPSIS
  Instala o GET em C:\PROGRAMACAO\GET sem clonar do Origin.

.PARAMETER TargetDir
  Pasta destino (predefinicao: C:\PROGRAMACAO\GET).

.PARAMETER BundlePath
  Caminho para GET-main.bundle (git bundle) ou GET-src.zip.

.PARAMETER FromGitHub
  Clona de https://github.com/mastercorisco/GET (quando o repositorio tiver codigo).
#>
param(
    [string]$TargetDir = "C:\PROGRAMACAO\GET",
    [string]$BundlePath = "",
    [switch]$FromGitHub
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "Comando '$Name' nao encontrado. $Hint"
    }
}

$Parent = Split-Path -Parent $TargetDir
if (-not (Test-Path $Parent)) {
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
}

if ($FromGitHub) {
    Require-Command git "Instale Git for Windows."
    if (Test-Path $TargetDir) {
        Write-Error "A pasta ja existe: $TargetDir. Remova-a ou escolha outro destino."
    }
    Write-Host "A clonar do GitHub..."
    git clone https://github.com/mastercorisco/GET.git $TargetDir
    Set-Location $TargetDir
    & "$TargetDir\scripts\setup_windows.ps1"
    exit 0
}

if ([string]::IsNullOrWhiteSpace($BundlePath)) {
    Write-Host @"

Instalacao GET em Windows (sem Origin)

Escolha uma opcao:

  A) GitHub (quando estiver sincronizado):
     powershell -ExecutionPolicy Bypass -File install_get_windows.ps1 -FromGitHub

  B) Ficheiro git bundle (GET-main.bundle desta conversa / agente Cursor):
     powershell -ExecutionPolicy Bypass -File install_get_windows.ps1 -BundlePath "C:\Users\...\Downloads\GET-main.bundle"

  C) ZIP do codigo (GET-src.zip):
     Expand-Archive -Path "...\GET-src.zip" -DestinationPath "C:\PROGRAMACAO\GET"
     cd C:\PROGRAMACAO\GET
     powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1

  D) Ja tem o codigo (ex.: abriu o projeto no Cursor Desktop):
     cd C:\caminho\para\GET
     powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1

"@
    exit 1
}

if (-not (Test-Path $BundlePath)) {
    Write-Error "Ficheiro nao encontrado: $BundlePath"
}

$ext = [IO.Path]::GetExtension($BundlePath).ToLowerInvariant()

if ($ext -eq ".bundle") {
    Require-Command git "Instale Git for Windows."
    if (Test-Path $TargetDir) {
        Write-Error "A pasta ja existe: $TargetDir"
    }
    Write-Host "A clonar do bundle..."
    git clone $BundlePath $TargetDir
    Set-Location $TargetDir
    & "$TargetDir\scripts\setup_windows.ps1"
    exit 0
}

if ($ext -eq ".zip") {
    if (Test-Path $TargetDir) {
        Write-Error "A pasta ja existe: $TargetDir"
    }
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    Expand-Archive -Path $BundlePath -DestinationPath $TargetDir -Force
    # git archive pode criar uma subpasta; normalizar se so existir uma entrada
    Set-Location $TargetDir
    & "$TargetDir\scripts\setup_windows.ps1"
    exit 0
}

Write-Error "Extensao nao suportada (use .bundle ou .zip): $BundlePath"