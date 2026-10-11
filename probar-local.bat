@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if not errorlevel 1 (
        py -3 bot.py --dry-run
        set "EXIT_CODE=%ERRORLEVEL%"
        goto :finished
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if not errorlevel 1 (
        python bot.py --dry-run
        set "EXIT_CODE=%ERRORLEVEL%"
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

