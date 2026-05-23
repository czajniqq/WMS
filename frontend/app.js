const API_BASE = '';

let agentsData = [];

async function fetchAgents() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/agents/`);
    if (!res.ok) return;
    agentsData = await res.json();
    renderAgentsTable(agentsData);
    populateAgentSelect(agentsData);
  } catch (e) {
    console.error('fetchAgents error:', e);
  }
}

function renderAgentsTable(agents) {
  const tbody = document.getElementById('agents-tbody');
  if (!agents.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">No agents registered</td></tr>';
    return;
  }
  tbody.innerHTML = agents.map(a => `
    <tr onclick="selectAgent(${a.id}, '${escHtml(a.hostname)}')">
      <td>${escHtml(a.hostname)}</td>
      <td>${escHtml(a.ip_address)}</td>
      <td>${escHtml(a.agent_version)}</td>
      <td>${formatDateTime(a.last_seen)}</td>
      <td><span class="status-${a.status.toLowerCase()}">${a.status}</span></td>
    </tr>
  `).join('');
}

function populateAgentSelect(agents) {
  const sel = document.getElementById('log-agent-select');
  const current = sel.value;
  sel.innerHTML = '<option value="">All Agents</option>' +
    agents.map(a => `<option value="${a.id}">${escHtml(a.hostname)}</option>`).join('');
  if (current) sel.value = current;
}

async function fetchMetrics(agentId, fromIso, toIso) {
  let url = `${API_BASE}/api/v1/agents/${agentId}/metrics?limit=100`;
  if (fromIso) url += `&from_time=${encodeURIComponent(fromIso)}`;
  if (toIso) url += `&to_time=${encodeURIComponent(toIso)}`;
  try {
    const res = await fetch(url);
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    console.error('fetchMetrics error:', e);
    return [];
  }
}

async function fetchActiveAlerts() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/alerts/active`);
    if (!res.ok) return;
    const alerts = await res.json();
    renderAlertsTable(alerts);
    document.getElementById('alerts-badge').textContent = alerts.length;
  } catch (e) {
    console.error('fetchActiveAlerts error:', e);
  }
}

function renderAlertsTable(alerts) {
  const tbody = document.getElementById('alerts-tbody');
  if (!alerts.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">No active alerts</td></tr>';
    return;
  }
  tbody.innerHTML = alerts.map(a => `
    <tr>
      <td>${a.agent_id}</td>
      <td>${escHtml(a.rule)}</td>
      <td>${a.threshold}%</td>
      <td>${a.actual_value.toFixed(1)}%</td>
      <td>${formatDateTime(a.triggered_at)}</td>
      <td><button class="btn btn-sm btn-danger" onclick="resolveAlert(${a.id})">Resolve</button></td>
    </tr>
  `).join('');
}

async function fetchLogs(agentId, level, fromIso, toIso) {
  if (!agentId) {
    if (!agentsData.length) {
      document.getElementById('logs-tbody').innerHTML =
        '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">Select an agent to view logs</td></tr>';
      return;
    }
    agentId = agentsData[0]?.id;
    if (!agentId) return;
  }
  let url = `${API_BASE}/api/v1/agents/${agentId}/logs?limit=100`;
  if (level) url += `&level=${encodeURIComponent(level)}`;
  if (fromIso) url += `&from_time=${encodeURIComponent(fromIso)}`;
  if (toIso) url += `&to_time=${encodeURIComponent(toIso)}`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      document.getElementById('logs-tbody').innerHTML = '';
      return;
    }
    const logs = await res.json();
    renderLogsTable(logs);
  } catch (e) {
    console.error('fetchLogs error:', e);
  }
}

function renderLogsTable(logs) {
  const tbody = document.getElementById('logs-tbody');
  if (!logs.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">No logs found</td></tr>';
    return;
  }
  tbody.innerHTML = logs.map(l => `
    <tr>
      <td>${formatDateTime(l.event_time)}</td>
      <td class="level-${(l.level||'').toLowerCase()}">${escHtml(l.level)}</td>
      <td>${escHtml(l.source)}</td>
      <td>${l.event_id}</td>
      <td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escHtml(l.message)}">${escHtml(l.message)}</td>
    </tr>
  `).join('');
}

async function resolveAlert(alertId) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/alerts/${alertId}/resolve`, { method: 'PUT' });
    if (res.ok) {
      await fetchActiveAlerts();
    }
  } catch (e) {
    console.error('resolveAlert error:', e);
  }
}

async function selectAgent(agentId, hostname) {
  document.getElementById('agent-detail').style.display = '';
  document.getElementById('detail-hostname').textContent = hostname;
  const now = new Date();
  const fromIso = new Date(now - 3600 * 1000).toISOString();
  const metrics = await fetchMetrics(agentId, fromIso, now.toISOString());
  
  destroyCharts();
  
  // TUTAJ JEST ZMIANA: Dodano 'net-chart' do inicjalizacji wykresów
  initCharts('cpu-chart', 'ram-chart', 'net-chart'); 
  
  updateCharts(metrics);
  document.getElementById('log-agent-select').value = agentId;
  fetchLogs(agentId, '', null, null);
}

function startAutoRefresh(intervalSeconds = 30) {
  setInterval(() => {
    fetchAgents();
    fetchActiveAlerts();
  }, intervalSeconds * 1000);
}

function formatDateTime(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString();
  } catch { return iso; }
}

function escHtml(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', () => {
  fetchAgents();
  fetchActiveAlerts();
  fetchLogs(null, '', null, null);
  startAutoRefresh(30);

  document.getElementById('log-apply-btn').addEventListener('click', () => {
    const agentId = document.getElementById('log-agent-select').value;
    const level = document.getElementById('log-level-select').value;
    const fromVal = document.getElementById('log-from').value;
    const toVal = document.getElementById('log-to').value;
    const fromIso = fromVal ? new Date(fromVal).toISOString() : null;
    const toIso = toVal ? new Date(toVal).toISOString() : null;
    fetchLogs(agentId || null, level, fromIso, toIso);
  });
});
