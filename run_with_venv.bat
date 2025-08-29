@echo off
REM Force l'utilisation du bon environnement virtuel pour lancer l'app
setlocal
set VENV_PATH=%~dp0.venv\Scripts
if exist "%VENV_PATH%\activate.bat" (
    call "%VENV_PATH%\activate.bat"
)
python main.py
