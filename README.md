# System Monitorowania Sieci LAN dla Windows

Kompleksowy system monitorowania urządzeń w sieci lokalnej (LAN) oparty na architekturze **agent – backend – frontend**. Pozwala na śledzenie stanu maszyn Windows w czasie rzeczywistym: CPU, RAM, logi systemowe, alerty progowe i wykrywanie offline agentów.

---

## Spis treści

1. [Architektura](#architektura)
2. [Wymagania technologiczne](#wymagania-technologiczne)
3. [Struktura projektu](#struktura-projektu)
4. [Szybki start – Backend](#szybki-start--backend)
5. [Szybki start – Agent](#szybki-start--agent-windows)
6. [Szybki start – Dashboard (frontend)](#szybki-start--dashboard-frontend)
7. [Dokumentacja API](#dokumentacja-api)
8. [Konfiguracja](#konfiguracja)
9. [Uruchomienie testów](#uruchomienie-testów)
10. [Scenariusz demonstracji](#scenariusz-demonstracji)
11. [Ograniczenia MVP](#ograniczenia-mvp)
12. [Dalsza dokumentacja](#dalsza-dokumentacja)

---

## Architektura

System składa się z trzech warstw:

| Warstwa | Rola | Technologia |
|---------|------|-------------|
| **Agent** | Zbiera metryki i logi z maszyn Windows, wysyła do backendu | Python, psutil, pywin32 |
| **Backend** | REST API, persystencja danych, logika alertów i liveness | FastAPI, SQLAlchemy, SQLite |
| **Frontend** | Interaktywny dashboard do wizualizacji danych | Vanilla JS, Chart.js |

```
┌─────────────────┐        HTTP/JSON         ┌──────────────────────┐
│  Agent Windows  │ ───────────────────────► │  Backend (FastAPI)   │
│  psutil +       │   POST /metrics          │  SQLite / SQLAlchemy │
│  win32evtlog    │   POST /logs             │  Alembic migrations  │
│  schedule       │   POST /heartbeat        └──────────┬───────────┘
└─────────────────┘                                     │  GET /agents
                                                        │  GET /metrics
                                              ┌─────────▼────────────┐
                                              │  Frontend Dashboard  │
                                              │  Chart.js, dark UI   │
                                              │  auto-refresh 30 s   │
                                              └──────────────────────┘
```

**Przepływ danych:**

1. Agent rejestruje się w backendzie (`POST /agents/register`)
2. Co 60 s wysyła metryki CPU/RAM/sieć (`POST /metrics`)
3. Co 5 min wysyła logi Windows Event Log (`POST /logs`)
4. Co 120 s wysyła heartbeat (`POST /agents/{id}/heartbeat`)
5. Backend sprawdza liveness i generuje alerty przy przekroczeniu progów
6. Dashboard odpytuje API i wyświetla dane w czasie rzeczywistym

---

## Wymagania technologiczne

| Komponent | Wymagania |
|-----------|-----------|
| **Backend** | Python 3.11+, pip |
| **Agent** | Python 3.11+, Windows 10/11 lub Windows Server 2016+ |
| **Frontend** | Dowolna nowoczesna przeglądarka (Chrome, Firefox, Edge) |
| **System** | Sieć LAN z dostępem do portu 8000 na maszynie z backendem |

---

## Struktura projektu

```
WMS/
├── agent/              # Agent zbierający dane z maszyn Windows
│   ├── main.py         # Punkt wejścia agenta
│   ├── collector.py    # Zbieranie metryk (CPU, RAM, sieć)
│   ├── event_log_reader.py  # Odczyt Windows Event Log
│   ├── reporter.py     # Komunikacja z backendem
│   ├── config.ini      # Konfiguracja agenta
│   ├── installer.ps1   # Instalator usługi Windows
│   └── requirements.txt
├── backend/            # API FastAPI + baza danych
│   ├── main.py         # Aplikacja FastAPI + lifespan
│   ├── config.py       # Ustawienia (zmienne środowiskowe)
│   ├── database.py     # Połączenie SQLAlchemy
│   ├── models.py       # Modele ORM
│   ├── schemas.py      # Schematy Pydantic
│   ├── routers/        # Endpointy API
│   ├── services/       # Logika biznesowa (alerty, liveness)
│   ├── alembic/        # Migracje bazy danych
│   ├── static/         # Pliki frontendowe (serwowane przez FastAPI)
│   └── requirements.txt
├── frontend/           # Źródła dashboardu (kopiowane do backend/static)
│   ├── index.html
│   ├── app.js
│   ├── chart_helpers.js
│   └── style.css
├── tests/              # Testy pytest
├── docs/               # Dokumentacja szczegółowa
└── README.md
```

---

## Szybki start – Backend

### 1. Instalacja zależności

**Windows (PowerShell):**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> 💡 Jeśli PowerShell blokuje aktywację:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

**Linux / macOS:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Uruchomienie backendu

Uruchom z **katalogu głównego projektu** (nie z `backend/`):

```bash
# Z aktywnym venv
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend wystartuje na `http://localhost:8000`.

### 3. Weryfikacja

Otwórz przeglądarkę:

- **Dashboard:** http://localhost:8000/
- **Swagger UI (docs API):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Szybki start – Agent (Windows)

### 1. Przygotowanie środowiska

Na docelowej maszynie Windows:

```powershell
cd agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Konfiguracja

Edytuj `agent/config.ini` — ustaw adres serwera backendowego:

```ini
[server]
url = http://<IP_MASZYNY_Z_BACKENDEM>:8000

[intervals]
metrics_seconds = 60
logs_seconds = 300
heartbeat_seconds = 120
```

### 3. Uruchomienie ręczne (dev/test)

```powershell
cd agent
python main.py
```

### 4. Instalacja jako usługa Windows (produkcja)

```powershell
# PowerShell jako Administrator
cd agent
.\installer.ps1
```

Agent zarejestruje się automatycznie w backendzie i zacznie wysyłać dane.

---

## Szybki start – Dashboard (frontend)

Frontend jest serwowany automatycznie przez backend z katalogu `backend/static/`. Po uruchomieniu backendu dashboard jest dostępny pod:

```
http://localhost:8000/
```

Jeśli chcesz pracować nad frontendem niezależnie (np. z live-server):

```bash
cd frontend
# Użyj dowolnego serwera plików statycznych, np.:
python -m http.server 3000
```

Następnie otwórz `http://localhost:3000/index.html`.

> ⚠️ W trybie standalone frontend musi mieć dostęp do backendu pod `http://localhost:8000` (CORS nie jest tu blokowany w dev).

---

## Dokumentacja API

Interaktywna dokumentacja API jest generowana automatycznie przez FastAPI:

| Narzędzie | URL |
|-----------|-----|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |

Szczegółowa dokumentacja endpointów: [docs/api.md](docs/api.md)

### Główne endpointy

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `POST` | `/agents/register` | Rejestracja nowego agenta |
| `POST` | `/agents/{id}/heartbeat` | Heartbeat agenta |
| `GET` | `/agents` | Lista agentów ze statusem |
| `POST` | `/metrics` | Wysłanie metryk |
| `GET` | `/metrics/{agent_id}` | Pobranie metryk agenta |
| `POST` | `/logs` | Wysłanie logów |
| `GET` | `/logs` | Pobranie logów |
| `GET` | `/alerts` | Lista alertów |

---

## Konfiguracja

### Backend – zmienne środowiskowe

Utwórz plik `.env` w katalogu `backend/` lub ustaw zmienne systemowe:

| Zmienna | Domyślna wartość | Opis |
|---------|-----------------|------|
| `DATABASE_URL` | `sqlite:///./monitoring.db` | URL bazy danych |
| `CPU_ALERT_THRESHOLD` | `90.0` | Próg alertu CPU (%) |
| `RAM_ALERT_THRESHOLD` | `90.0` | Próg alertu RAM (%) |
| `AGENT_OFFLINE_TIMEOUT_SECONDS` | `300` | Czas (s) do oznaczenia agenta jako offline |
| `LIVENESS_CHECK_INTERVAL_SECONDS` | `60` | Częstotliwość sprawdzania liveness (s) |

### Agent – config.ini

| Sekcja | Klucz | Domyślna wartość | Opis |
|--------|-------|-----------------|------|
| `server` | `url` | `http://127.0.0.1:8000` | Adres backendu |
| `intervals` | `metrics_seconds` | `60` | Interwał wysyłania metryk |
| `intervals` | `logs_seconds` | `300` | Interwał wysyłania logów |
| `intervals` | `heartbeat_seconds` | `120` | Interwał heartbeat |
| `thresholds` | `min_log_level` | `WARNING` | Minimalny poziom logów do wysłania |

---

## Uruchomienie testów

```bash
# Z katalogu głównego projektu, z aktywnym venv
pip install -r backend/requirements.txt
python -m pytest tests/ -v
```

Testy korzystają z FastAPI TestClient i httpx — nie wymagają uruchomionego serwera.

---

## Scenariusz demonstracji

Poniższy scenariusz pozwala w ~5 minut zaprezentować działanie systemu end-to-end.

### Przygotowanie (jednorazowo)

```bash
# 1. Sklonuj repo
git clone https://github.com/czajniqq/WMS.git
cd WMS

# 2. Zainstaluj zależności backendu
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### Demo krok po kroku

```bash
# KROK 1: Uruchom backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

1. **Otwórz dashboard** → http://localhost:8000/
   - Pokaż pustą tabelę agentów, brak alertów

2. **Otwórz Swagger UI** → http://localhost:8000/docs
   - Pokaż dostępne endpointy API

```bash
# KROK 2: Uruchom agenta (na tej samej lub innej maszynie Windows)
cd agent
python main.py
```

3. **Odśwież dashboard** (~10 s po starcie agenta)
   - Agent pojawi się w tabeli ze statusem „online"
   - Po 60 s pojawią się metryki CPU/RAM na wykresach

4. **Wygeneruj obciążenie** (opcjonalnie, żeby wymusić alert):
   - Uruchom proces obciążający CPU na monitorowanej maszynie
   - Po przekroczeniu progu 90% pojawi się alert w dashboardzie

5. **Zatrzymaj agenta** (Ctrl+C)
   - Po 5 minutach (timeout 300 s) backend oznaczy agenta jako „offline"
   - Pokaż zmianę statusu w dashboardzie

### Punkty do omówienia podczas demo

- Automatyczna rejestracja agenta (zero konfiguracji po stronie serwera)
- Wykrywanie offline na podstawie heartbeat
- Progi alertów konfigurowalne przez zmienne środowiskowe
- Ciemny interfejs dashboardu z auto-refresh

---

## Ograniczenia MVP

| Ograniczenie | Opis |
|--------------|------|
| **Brak uwierzytelniania** | API nie wymaga tokenów ani logowania — nie nadaje się do sieci publicznych |
| **SQLite** | Jednowątkowa baza danych — brak skalowalności na wiele równoległych zapisów |
| **Tylko Windows** | Agent korzysta z pywin32 / Windows Event Log — nie działa na Linux/macOS |
| **Brak HTTPS** | Komunikacja nieszyfrowana — tylko dla sieci zaufanych (LAN) |
| **Brak retencji danych** | Brak automatycznego czyszczenia starych metryk/logów — baza rośnie bez limitu |
| **Single-instance backend** | Brak load balancingu, brak replikacji — jeden serwer |
| **Brak powiadomień** | Alerty widoczne tylko w dashboardzie — brak e-mail/Slack/webhook |
| **Frontend polling** | Dashboard odpytuje API co 30 s — brak WebSocket/SSE dla real-time |

---

## Technologie

| Kategoria | Stack |
|-----------|-------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, SQLite |
| **Agent** | Python 3.11+, psutil, pywin32, requests, schedule |
| **Frontend** | Vanilla JS (ES6+), Chart.js, CSS Grid/Flexbox |
| **Testy** | pytest, httpx, FastAPI TestClient |

---

## Dalsza dokumentacja

- 📘 [Dokumentacja API (szczegółowa)](docs/api.md)
- 🚀 [Wdrożenie agenta jako usługi Windows](docs/agent-deploy.md)
