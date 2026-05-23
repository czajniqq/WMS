# System Monitorowania Sieci LAN dla Windows

Kompleksowy system monitorowania urządzeń w sieci lokalnej (LAN) oparty na architekturze agent–backend–frontend.

## Architektura

```
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

```
agent/          # Agent Python uruchamiany na maszynach Windows
backend/        # API FastAPI + baza danych SQLite
frontend/       # Interfejs webowy (HTML/CSS/JS)
tests/          # Testy jednostkowe i integracyjne (pytest)
docs/           # Dokumentacja API i wdrożenia agenta
```

## Szybki start – Backend

Backend systemu został przygotowany w FastAPI. Odpowiada za rejestrację agentów, odbieranie heartbeatów, metryk, logów oraz obsługę alertów.

### Instalacja zależności

```powershell
cd C:\repos\WMS
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Jeżeli PowerShell blokuje aktywację środowiska:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Uruchomienie backendu

Backend należy uruchamiać z katalogu głównego projektu:

```powershell
cd C:\repos\WMS
.\backend\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

Dokumentacja API dostępna pod:

```text
http://127.0.0.1:8000/docs
``````

Dokumentacja API dostępna pod: http://localhost:8000/docs

## Szybki start – Agent (Windows)

1. Skopiuj katalog `agent/` na docelową maszynę Windows
2. Skonfiguruj `agent/config.ini` (adres serwera)
3. Uruchom jako usługę Windows:

```powershell
# PowerShell jako Administrator
.\installer.ps1
```

## Uruchomienie testów

```bash
pip install -r backend/requirements.txt
python -m pytest tests/ -v
```

## Konfiguracja

Zmienne środowiskowe (lub plik `.env` w katalogu `backend/`):

| Zmienna | Domyślna wartość | Opis |
|---------|-----------------|------|
| `DATABASE_URL` | `sqlite:///./monitoring.db` | URL bazy danych |
| `CPU_ALERT_THRESHOLD` | `90.0` | Próg alertu CPU (%) |
| `RAM_ALERT_THRESHOLD` | `90.0` | Próg alertu RAM (%) |
| `AGENT_OFFLINE_TIMEOUT_SECONDS` | `300` | Czas do oznaczenia agenta jako offline |
| `LIVENESS_CHECK_INTERVAL_SECONDS` | `60` | Częstotliwość sprawdzania liveness |

## Technologie

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, SQLite
- **Agent:** Python 3.11+, psutil, pywin32, requests, schedule
- **Frontend:** Vanilla JS, Chart.js, CSS Grid/Flexbox
- **Testy:** pytest, httpx, FastAPI TestClient

## Dokumentacja

- [Dokumentacja API](docs/api.md)
- [Wdrożenie agenta](docs/agent-deploy.md)
