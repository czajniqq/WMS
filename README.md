# System Monitorowania Sieci LAN dla Windows

Kompleksowy system monitorowania urządzeń w sieci lokalnej (LAN) oparty na architekturze agent–backend–frontend.

## Architektura

```text
┌─────────────────┐        HTTP/JSON        ┌──────────────────────┐
│  Agent Windows  │ ──────────────────────► │  Backend (FastAPI)   │
│  (psutil +      │                         │  SQLite / SQLAlchemy │
│   win32evtlog)  │                         │  Alembic migrations  │
└─────────────────┘                         └──────────┬───────────┘
                                                       │
                                            ┌──────────▼───────────┐
                                            │  Frontend Dashboard  │
                                            │  (Chart.js, dark UI) │
                                            └──────────────────────┘
```

## Funkcjonalności

- **Rejestracja agentów** – automatyczna rejestracja maszyn Windows w backendzie
- **Metryki systemowe** – CPU, RAM, sieć, uptime (co 60 s)
- **Logi zdarzeń Windows** – odczyt z `System` i `Application` Event Log (co 5 min)
- **Heartbeat** – wykrywanie offline agentów (timeout 300 s)
- **Alerty** – automatyczne generowanie alertów przy przekroczeniu progów CPU/RAM (domyślnie 90%)
- **Dashboard** – ciemny interfejs z wykresami w czasie rzeczywistym, tabelą agentów, logami i alertami

## Struktura projektu

```text
agent/          # Agent Python uruchamiany na maszynach Windows
backend/        # API FastAPI + baza danych SQLite
frontend/       # Interfejs webowy (HTML/CSS/JS)
tests/          # Testy jednostkowe i integracyjne (pytest)
docs/           # Dokumentacja API i wdrożenia agenta
```

---

# Wymagania wstępne

Na każdym komputerze (zarówno serwerze, jak i klientach) musi być zainstalowany:

- **Python 3.11+**
- Podczas instalacji należy zaznaczyć opcję:

```text
Add Python to PATH
```

---

# Instalacja i uruchomienie serwera (Backend)

Backend odpowiada za:

- rejestrację agentów,
- odbieranie heartbeatów,
- przechowywanie logów i metryk,
- obsługę alertów,
- udostępnienie panelu webowego.

Serwer instalujemy wyłącznie na jednym głównym komputerze.

## Ręczna instalacja w CMD

```powershell
:: Przejście do głównego folderu projektu
cd /d F:\WMS-main\WMS-main

:: Utworzenie środowiska wirtualnego
python -m venv venv

:: Aktywacja środowiska
call venv\Scripts\activate

:: Instalacja zależności backendu
cd backend
pip install -r requirements.txt
cd ..

:: Uruchomienie backendu
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Dokumentacja API

Po uruchomieniu backendu dokumentacja Swagger będzie dostępna pod adresem:

```text
http://127.0.0.1:8000/docs
```

lub:

```text
http://localhost:8000/docs
```

---

# Konfiguracja Zapory Windows (KRYTYCZNE)

Aby inne komputery mogły komunikować się z serwerem, należy odblokować port `8000`.

## Instrukcja

1. Uruchom PowerShell jako Administrator.
2. Wklej poniższą komendę:

```powershell
New-NetFirewallRule -DisplayName "WMS Serwer Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

# Konfiguracja Agentów (Klienci)

Agent działa jako usługa Windows uruchamiana w tle.

## Konfiguracja `agent/config.ini`

### Główny komputer (Serwer)

Plik pozostaje bez zmian:

```ini
url = http://127.0.0.1:8000
```

### Komputery klienckie

1. Na serwerze otwórz CMD.
2. Wpisz:

```powershell
ipconfig
```

3. Odszukaj adres IPv4 serwera, np.:

```text
192.168.0.138
```

4. Na komputerze klienckim otwórz plik:

```text
agent/config.ini
```

5. Ustaw adres serwera:

```ini
url = http://192.168.0.138:8000
```

---

# Instalacja Agenta jako usługi Windows

Po poprawnej konfiguracji `config.ini`:

1. Wejdź do głównego folderu projektu.
2. Kliknij prawym przyciskiem myszy na:

```text
ZAINSTALUJ_AGENTA.bat
```

3. Wybierz:

```text
Uruchom jako administrator
```

Skrypt:

- zainstaluje wymagane biblioteki,
- uruchomi agenta jako usługę Windows,
- skonfiguruje automatyczny start wraz z systemem.

---

# Diagnostyka i rozwiązywanie problemów

Jeżeli agent nie pojawia się w panelu lub ma status `OFFLINE`, należy uruchomić go w trybie jawnym.

## Tworzenie pliku diagnostycznego

Na komputerze klienckim utwórz plik:

```text
TEST_AGENTA.bat
```

Wklej do niego poniższy kod:

```bat
@echo off
title Agent Monitoringu - Tryb Jawny (Diagnostyka)
chcp 65001 >nul
cd /d "%~dp0\agent"

echo [INFO] Sprawdzanie i instalowanie ewentualnych brakow...
python -m pip install -r requirements.txt --quiet

echo [INFO] Uruchamianie Agenta widocznego w konsoli...
python main.py

pause
```

## Interpretacja działania

### Jeśli pojawi się błąd

Najczęstsze problemy:

- błędny adres IP w `config.ini`,
- zablokowany port `8000`,
- brakujące biblioteki Python.

Przykładowy komunikat:

```text
Connection refused
```

oznacza najczęściej problem z połączeniem do serwera.

### Jeśli okno pozostanie aktywne

Może pojawić się ostrzeżenie:

```text
DeprecationWarning
```

Można je zignorować.

Jeżeli terminal pozostaje aktywny bez błędów, agent działa poprawnie i komputer powinien pojawić się w panelu.

Po zakończeniu testów należy ponownie uruchomić:

```text
ZAINSTALUJ_AGENTA.bat
```

jako administrator.

---

# Uruchamianie testów

```bash
pip install -r backend/requirements.txt
python -m pytest tests/ -v
```

---

# Konfiguracja środowiska

Zmienne środowiskowe (lub plik `.env` w katalogu `backend/`):

| Zmienna | Domyślna wartość | Opis |
|---------|-----------------|------|
| `DATABASE_URL` | `sqlite:///./monitoring.db` | URL bazy danych |
| `CPU_ALERT_THRESHOLD` | `90.0` | Próg alertu CPU (%) |
| `RAM_ALERT_THRESHOLD` | `90.0` | Próg alertu RAM (%) |
| `AGENT_OFFLINE_TIMEOUT_SECONDS` | `300` | Timeout offline agenta |
| `LIVENESS_CHECK_INTERVAL_SECONDS` | `60` | Interwał sprawdzania heartbeat |

---

# Technologie

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, SQLite
- **Agent:** Python 3.11+, psutil, pywin32, requests, schedule
- **Frontend:** Vanilla JS, Chart.js, CSS Grid/Flexbox
- **Testy:** pytest, httpx, FastAPI TestClient

---

# Dokumentacja

- `docs/api.md` – dokumentacja API
- `docs/agent-deploy.md` – wdrożenie agenta

