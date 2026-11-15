@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
set "ROOT=%CD%"

title GET - arranque
echo.
echo  GET - Gerador de Especificacoes Funcionais
echo  Arranque local (127.0.0.1)
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado no PATH. Instale Python 3.12+ e tente de novo.
  pause
  exit /b 1
)

echo [1/2] A preparar backend Python...
cd /d "%ROOT%\backend"
python -m pip install -e ".[dev]" -q
if errorlevel 1 (
  echo [ERRO] Falha ao instalar dependencias Python.
  pause
  exit /b 1
)

echo [2/2] A iniciar a aplicacao (sem Node.js)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :4810 ^| findstr LISTENING') do (
  echo       A terminar processo antigo na porta 4810 PID %%a...
  taskkill /F /PID %%a >nul 2>&1
)
start "GET" cmd /k "cd /d %ROOT%\backend & python -m uvicorn app.main:app --host 127.0.0.1 --port 4810"
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:4810/

echo.
echo  App:  http://127.0.0.1:4810/
echo  API:  http://127.0.0.1:4810/api/health
echo.
echo  Feche a janela "GET" para parar.
echo.
pause
endlocal