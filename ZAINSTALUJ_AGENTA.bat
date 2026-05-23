@echo off
title Instalator Agenta Monitoringu - Autostart
chcp 65001 >nul

:: SEKCJA AUTO-ELEVATION: Skrypt sam sprawdza czy ma uprawnienia admina.
:: Jeśli nie ma, automatycznie wywołuje systemowe okienko z prośbą o zgodę.
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Wymagane uprawnienia administratora. Wywoływanie okna UAC...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs"
    exit /b
)

echo =======================================================================
echo    INSTALACJA AGENTA LAN JAKO USŁUGA SYSTEMOWA (PRACA W TLE)
echo =======================================================================

:: Przejdź do folderu z agentem
cd /d "%~dp0"
cd agent

:: Sprawdzenie obecności interpretera Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BŁĄD] Python nie jest zainstalowany na tym komputerze!
    pause
    exit /b
)

:: Uruchomienie instalatora PowerShell w sposób całkowicie zautomatyzowany
echo [INFO] Trwa instalacja usugi oraz pobieranie bibliotek zasobów...
powershell -NoProfile -ExecutionPolicy Bypass -File .\installer.ps1

echo =======================================================================
echo [SUKCES] Agent został pomyślnie zainstalowany i uruchomiony w tle!
echo Komputer jest już monitorowany. Możesz bezpiecznie zamknąć to okno.
echo =======================================================================
timeout /t 5
exit