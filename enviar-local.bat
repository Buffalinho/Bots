@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Se creo .env. Completa el archivo y vuelve a ejecutar enviar-local.bat.
    start "" notepad.exe "%~dp0.env"
    pause
    exit /b 1
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if not errorlevel 1 (
        py -3 bot.py
        set "EXIT_CODE=!ERRORLEVEL!"
        goto :finished
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if not errorlevel 1 (
        python bot.py
        set "EXIT_CODE=!ERRORLEVEL!"
        goto :finished
    )
)

echo No se encontro Python 3.9 o posterior.
echo Instala Python desde https://www.python.org/downloads/windows/
set "EXIT_CODE=1"

:finished
echo.
pause
exit /b %EXIT_CODE%

