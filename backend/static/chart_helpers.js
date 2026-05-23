let cpuChart = null;
let ramChart = null;
let netChart = null;

function initCharts(cpuCanvasId, ramCanvasId, netCanvasId) {
  const cpuCtx = document.getElementById(cpuCanvasId).getContext('2d');
  const ramCtx = document.getElementById(ramCanvasId).getContext('2d');
  const netCtx = document.getElementById(netCanvasId).getContext('2d');

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    scales: {
      x: { ticks: { color: '#94a3b8', maxTicksLimit: 6 }, grid: { color: '#2d3147' } },
      y: { min: 0, max: 100, ticks: { color: '#94a3b8', callback: v => v + '%' }, grid: { color: '#2d3147' } },
    },
    plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ctx.parsed.y.toFixed(1) + '%' } } },
  };

  cpuChart = new Chart(cpuCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'CPU %', data: [], borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.1)', fill: true, tension: 0.3, pointRadius: 2 }] },
    options: JSON.parse(JSON.stringify(commonOptions)),
  });

  ramChart = new Chart(ramCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'RAM %', data: [], borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.1)', fill: true, tension: 0.3, pointRadius: 2 }] },
    options: JSON.parse(JSON.stringify(commonOptions)),
  });

  const netOptions = JSON.parse(JSON.stringify(commonOptions));
  delete netOptions.scales.y.max; 
  netOptions.scales.y.ticks.callback = v => v + ' KB/s';
  netOptions.plugins.tooltip.callbacks.label = ctx => ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + ' KB/s';
  netOptions.plugins.legend.display = true;

  netChart = new Chart(netCtx, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Sent', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', fill: true, tension: 0.3, pointRadius: 2 },
      { label: 'Recv', data: [], borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.1)', fill: true, tension: 0.3, pointRadius: 2 }
    ]},
    options: netOptions,
  });
}

function updateCharts(metricsData) {
  if (!cpuChart || !ramChart || !netChart) return;
  const sorted = [...metricsData].sort((a, b) => new Date(a.collected_at) - new Date(b.collected_at));
  const labels = sorted.map(m => new Date(m.collected_at).toLocaleTimeString());
  
  const cpuData = sorted.map(m => m.cpu_percent);
  const ramData = sorted.map(m => m.ram_percent);
  
  const sentData = [];
  const recvData = [];
  for (let i = 0; i < sorted.length; i++) {
    if (i === 0) {
      sentData.push(0); recvData.push(0);
    } else {
      const prev = sorted[i-1];
      const curr = sorted[i];
      const timeDiffSec = (new Date(curr.collected_at) - new Date(prev.collected_at)) / 1000;
      
      if (timeDiffSec > 0 && curr.uptime_seconds >= prev.uptime_seconds) {
        sentData.push(Math.max(0, (curr.net_bytes_sent - prev.net_bytes_sent) / 1024 / timeDiffSec));
        recvData.push(Math.max(0, (curr.net_bytes_recv - prev.net_bytes_recv) / 1024 / timeDiffSec));
      } else {
        sentData.push(0); recvData.push(0); 
      }
    }
  }

  cpuChart.data.labels = labels; cpuChart.data.datasets[0].data = cpuData; cpuChart.update();
  ramChart.data.labels = labels; ramChart.data.datasets[0].data = ramData; ramChart.update();
  netChart.data.labels = labels; netChart.data.datasets[0].data = sentData; netChart.data.datasets[1].data = recvData; netChart.update();
}

function destroyCharts() {
  if (cpuChart) { cpuChart.destroy(); cpuChart = null; }
  if (ramChart) { ramChart.destroy(); ramChart = null; }
  if (netChart) { netChart.destroy(); netChart = null; }
}
