# API Documentation

## Base URL

```
http://<server>:8000
```

Interactive docs available at `/docs` (Swagger UI) and `/redoc`.

---

## Agents

### POST /api/v1/agents/register

Register a new agent.

**Request body:**
```json
{
  "hostname": "DESKTOP-ABC123",
  "ip_address": "192.168.1.10",
  "agent_version": "1.0.0"
}
```

**Response 201:**
```json
{
  "id": 1,
  "hostname": "DESKTOP-ABC123",
  "ip_address": "192.168.1.10",
  "agent_version": "1.0.0",
  "registered_at": "2024-01-01T10:00:00",
  "last_seen": "2024-01-01T10:00:00",
  "status": "ONLINE"
}
```

**Errors:** `409 Conflict` if hostname already registered.

---

### POST /api/v1/agents/{agent_id}/heartbeat

Update agent last-seen timestamp and set status to ONLINE.

**Response 200:**
```json
{"status": "ok"}
```

**Errors:** `404 Not Found` if agent_id does not exist.

---

### GET /api/v1/agents/

List all registered agents.

**Response 200:** Array of agent objects.

---

## Metrics

### POST /api/v1/agents/{agent_id}/metrics

Submit a metrics snapshot.

**Request body:**
```json
{
  "collected_at": "2024-01-01T10:00:00",
  "cpu_percent": 45.2,
  "ram_percent": 67.8,
  "ram_used_mb": 5532.0,
  "ram_total_mb": 8192.0,
  "net_bytes_sent": 1048576,
  "net_bytes_recv": 2097152,
  "uptime_seconds": 86400
}
```

**Response 201:** Metric object with `id` and `agent_id`.

**Side effect:** Triggers alert evaluation for CPU/RAM thresholds.

**Errors:** `404 Not Found` if agent_id does not exist.

---

### GET /api/v1/agents/{agent_id}/metrics

Query metrics for an agent.

**Query parameters:**
- `from_time` (ISO 8601 datetime, optional)
- `to_time` (ISO 8601 datetime, optional)
- `limit` (integer, default 100)

**Response 200:** Array of metric objects.

---

## Logs

### POST /api/v1/agents/{agent_id}/logs

Submit a batch of Windows Event Log entries.

**Request body:**
```json
{
  "entries": [
    {
      "event_time": "2024-01-01T09:55:00",
      "level": "WARNING",
      "source": "System",
      "event_id": 7036,
      "message": "The service entered the stopped state."
    }
  ]
}
```

**Response 201:**
```json
{"saved": 1}
```

**Errors:** `404 Not Found` if agent_id does not exist.

---

### GET /api/v1/agents/{agent_id}/logs

Query event logs for an agent.

**Query parameters:**
- `level` (string, optional): Filter by level (e.g. `WARNING`, `ERROR`)
- `from_time` (ISO 8601 datetime, optional)
- `to_time` (ISO 8601 datetime, optional)
- `limit` (integer, default 100)

**Response 200:** Array of log objects.

---

## Alerts

### GET /api/v1/alerts/

List all alerts (active and resolved).

**Response 200:** Array of alert objects.

---

### GET /api/v1/alerts/active

List only active alerts.

**Response 200:** Array of alert objects with `status == "ACTIVE"`.

---

### PUT /api/v1/alerts/{alert_id}/resolve

Resolve an active alert.

**Response 200:** Updated alert object with `status == "RESOLVED"`.

**Errors:**
- `404 Not Found` if alert_id does not exist.
- `409 Conflict` if alert is already resolved.

---

## Alert Rules

| Rule       | Triggered When                                      |
|------------|-----------------------------------------------------|
| `CPU_HIGH` | `cpu_percent >= CPU_ALERT_THRESHOLD` (default 90%) |
| `RAM_HIGH` | `ram_percent >= RAM_ALERT_THRESHOLD` (default 90%) |

Thresholds are configurable via environment variables or `.env` file.

---

## Agent Status

Agents are automatically marked **OFFLINE** if `last_seen` is older than `AGENT_OFFLINE_TIMEOUT_SECONDS` (default 300s). The liveness check runs every `LIVENESS_CHECK_INTERVAL_SECONDS` (default 60s).
