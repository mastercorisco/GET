#Requires -Version 5.1
<#
.SYNOPSIS
  Prepara e arranca o GET em Windows (sem credenciais origin.cursor.com).

.DESCRIPTION
  Instala dependencias Python e chama run_local.bat.
  Executa na raiz do projeto ou a partir de scripts\.
#>
param(
    [switch]$SkipStart
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host ""
Write-Host " GET - setup Windows"
Write-Host " Pasta: $Root"
Write-Host ""

function Require-Command {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "Comando '$Name' nao encontrado. $Hint"
    }
}

Require-Command python "Instale Python 3.12+ e marque 'Add to PATH'."

Write-Host "[1/1] Backend (pip install -e .[dev])..."
Set-Location "$Root\backend"
python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { throw "Falha no pip install." }

Set-Location $Root
Write-Host ""
Write-Host " Setup concluido."

if (-not $SkipStart) {
    Write-Host "A iniciar servidores (run_local.bat)..."
    & "$Root\scripts\run_local.bat"
}