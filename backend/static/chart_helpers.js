let cpuChart = null;
let ramChart = null;

function initCharts(cpuCanvasId, ramCanvasId) {
  const cpuCtx = document.getElementById(cpuCanvasId).getContext('2d');
  const ramCtx = document.getElementById(ramCanvasId).getContext('2d');

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    scales: {
      x: {
        ticks: { color: '#94a3b8', maxTicksLimit: 6, maxRotation: 0 },
        grid: { color: '#2d3147' },
      },
      y: {
        min: 0,
        max: 100,
        ticks: { color: '#94a3b8', callback: v => v + '%' },
        grid: { color: '#2d3147' },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ctx.parsed.y.toFixed(1) + '%' } },
    },
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
}

function updateCharts(metricsData) {
  if (!cpuChart || !ramChart) return;
  const sorted = [...metricsData].sort((a, b) => new Date(a.collected_at) - new Date(b.collected_at));
  const labels = sorted.map(m => new Date(m.collected_at).toLocaleTimeString());
  const cpuData = sorted.map(m => m.cpu_percent);
  const ramData = sorted.map(m => m.ram_percent);

  cpuChart.data.labels = labels;
  cpuChart.data.datasets[0].data = cpuData;
  cpuChart.update();

  ramChart.data.labels = labels;
  ramChart.data.datasets[0].data = ramData;
  ramChart.update();
}

function destroyCharts() {
  if (cpuChart) { cpuChart.destroy(); cpuChart = null; }
  if (ramChart) { ramChart.destroy(); ramChart = null; }
}
