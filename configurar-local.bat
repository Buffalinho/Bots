@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Se creo .env a partir de .env.example.
)

echo Edita SMTP_USER, SMTP_PASSWORD y EMAIL_TO en .env.
echo Usa una contrasena de aplicacion del correo, no tu contrasena normal.
start "" notepad.exe "%~dp0.env"

