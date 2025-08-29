@echo off
REM Ce script va packager le backend Flask en .exe avec PyInstaller
REM 1. Installe PyInstaller si besoin
pip install pyinstaller
REM 2. Génére le .exe (mode onefile, console visible pour debug)
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" main.py
REM 3. Le .exe sera dans le dossier dist\main.exe
pause
