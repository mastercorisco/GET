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

where npm >nul 2>&1
if errorlevel 1 (
  echo [ERRO] npm nao encontrado no PATH. Instale Node.js LTS e tente de novo.
  pause
  exit /b 1
)

echo [1/3] A preparar backend...
cd /d "%ROOT%\backend"
python -m pip install -e ".[dev]" -q
if errorlevel 1 (
  echo [ERRO] Falha ao instalar dependencias Python.
  pause
  exit /b 1
)

echo [2/3] A preparar frontend...
cd /d "%ROOT%\frontend"
if not exist "node_modules\" (
  call npm install
  if errorlevel 1 (
    echo [ERRO] Falha no npm install.
    pause
    exit /b 1
  )
)

echo [3/3] A iniciar servidores...
start "GET API" cmd /k "cd /d %ROOT%\backend & python -m uvicorn app.main:app --host 127.0.0.1 --port 4810"
timeout /t 2 /nobreak >nul
start "GET Web" cmd /k "cd /d %ROOT%\frontend & npm run dev"

echo.
echo  API:  http://127.0.0.1:4810/api/health
echo  App:  http://127.0.0.1:4811/
echo.
echo  Feche as janelas "GET API" e "GET Web" para parar.
echo.
pause
endlocal