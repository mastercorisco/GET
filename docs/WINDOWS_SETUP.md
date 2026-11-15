# GET no Windows — sem credenciais `origin.cursor.com`

O repositório do agente Cloud vive no **Origin** (`origin.cursor.com`). Fora do Cursor, o Git pede um **token Cursor**, não a password do GitHub. Para evitar isso, use um destes métodos.

## Método 1 — Abrar no Cursor Desktop (mais simples)

1. Abra o agente [Gerador especificações técnicas](https://cursor.com/agents/bc-ea5e56fa-c110-42ce-be59-3529b8ee18a0).
2. Abra o projeto no Cursor Desktop a partir do agente (checkout local / pasta do agente).
3. Copie ou sincronize a pasta para `C:\PROGRAMACAO\GET` se quiser um caminho fixo.
4. Na pasta do projeto:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
```

Ou execute `scripts\run_local.bat`.

## Método 2 — ZIP do código (sem `git clone` do Origin)

1. Descarregue `GET-src.zip` (artefactos deste agente ou ficheiro `releases/GET-src.zip` no repositório).
2. No PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path C:\PROGRAMACAO\GET | Out-Null
Expand-Archive -Path "$env:USERPROFILE\Downloads\GET-src.zip" -DestinationPath C:\PROGRAMACAO\GET -Force
cd C:\PROGRAMACAO\GET
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
```

## Método 3 — Git bundle (histórico git completo)

1. Descarregue `GET-main.bundle`.
2. Precisa de [Git for Windows](https://git-scm.com/download/win).

```powershell
powershell -ExecutionPolicy Bypass -File install_get_windows.ps1 -BundlePath "$env:USERPROFILE\Downloads\GET-main.bundle"
```

(Execute a partir da pasta `scripts` do ZIP, ou copie o script para a pasta dos downloads.)

## Método 4 — GitHub (quando `main` estiver preenchido)

Quando o código estiver em [github.com/mastercorisco/GET](https://github.com/mastercorisco/GET):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_get_windows.ps1 -FromGitHub
```

Autenticação normal do GitHub (`gh auth login` ou browser no Git Credential Manager).

## O que **não** fazer no CMD à mão

```text
git clone https://origin.cursor.com/git/jo-o-pedro-cabral/tmp-d400637815729183.git
```

Fora do Cursor isso pede credenciais Origin. Só use se tiver token Git do Cursor nas definições da conta.

## Arranque

- API: `http://127.0.0.1:4810/api/health`
- UI: `http://127.0.0.1:4811/`
- Atalho: `scripts\run_local.bat`

Requisitos: **Python 3.12+** e **Node.js LTS** no PATH.