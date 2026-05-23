# Agent Deployment Guide

## Requirements

- Windows 10/11 or Windows Server 2016+
- Python 3.11 or newer
- Network access to the monitoring backend server
- Administrator privileges (for Windows service installation)

---

## Quick Start

### 1. Copy agent files

Copy the `agent/` directory to the target Windows machine, e.g.:

```
C:\MonitoringAgent\
  main.py
  collector.py
  event_log_reader.py
  reporter.py
  config.ini
  requirements.txt
  installer.ps1
```

### 2. Configure the agent

Edit `config.ini` to point to your backend server:

```ini
[server]
url = http://192.168.1.100:8000

[agent]
version = 1.0.0

[intervals]
metrics_seconds = 60
logs_seconds = 300
heartbeat_seconds = 120

[thresholds]
min_log_level = WARNING

[retry]
max_retries = 3
backoff_seconds = 5
```

### 3. Install as a Windows service

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope Process
C:\MonitoringAgent\installer.ps1
```

The script will:
1. Verify Python is in PATH
2. Install Python dependencies (`pip install -r requirements.txt`)
3. Create a Windows service named `MonitoringAgent`
4. Start the service automatically

> **Tip:** Install [NSSM](https://nssm.cc/) first for better service management (log rotation, restart on failure). The installer detects NSSM automatically.

---

## Manual run (for testing)

```cmd
cd C:\MonitoringAgent
python main.py
```

The agent will register itself with the backend, then begin collecting and submitting metrics every 60 seconds.

---

## Service management

```powershell
# Check status
Get-Service MonitoringAgent

# Stop
Stop-Service MonitoringAgent

# Start
Start-Service MonitoringAgent

# Remove (if NSSM was used)
nssm remove MonitoringAgent confirm

# Remove (if sc.exe was used)
sc.exe delete MonitoringAgent
```

---

## Log files

| File                        | Contents                        |
|-----------------------------|----------------------------------|
| `agent_errors.log`          | Python-level errors from agent   |
| `service_stdout.log`        | Stdout (NSSM only)               |
| `service_stderr.log`        | Stderr (NSSM only)               |

---

## Collected data

| Data point        | Source                          | Interval  |
|-------------------|---------------------------------|-----------|
| CPU %             | `psutil.cpu_percent()`          | 60 s      |
| RAM % / used / total | `psutil.virtual_memory()`    | 60 s      |
| Network bytes sent/recv | `psutil.net_io_counters()` | 60 s   |
| System uptime     | `psutil.boot_time()`            | 60 s      |
| Windows Event Log | `win32evtlog` (System, Application) | 300 s |

---

## Firewall

Ensure the agent machine can reach the backend on TCP port 8000 (or whichever port you configure).

```powershell
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
```

---

## Troubleshooting

| Symptom | Resolution |
|---------|-----------|
| Agent shows OFFLINE in dashboard | Check network connectivity; verify `config.ini` URL |
| No logs collected | Ensure agent runs as Administrator (Event Log access requires elevation) |
| `pywin32` import error | Run `pip install pywin32` then `python Scripts/pywin32_postinstall.py -install` |
| Service won't start | Check `service_stderr.log`; verify Python path in `sc.exe` service config |
