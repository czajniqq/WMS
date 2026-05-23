@echo off
title Agent Monitoringu - Tryb Jawny
chcp 65001 >nul
cd /d "%~dp0\agent"

echo [INFO] Instalowanie ewentualnych braków...
python -m pip install -r requirements.txt --quiet

echo [INFO] Uruchamianie Agenta...
python main.py

pause