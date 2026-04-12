import time
from datetime import datetime
import psutil

def collect_metrics() -> dict:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    net = psutil.net_io_counters()
    boot_time = psutil.boot_time()
    uptime = int(time.time() - boot_time)
    return {
        "collected_at": datetime.utcnow().isoformat(),
        "cpu_percent": cpu,
        "ram_percent": mem.percent,
        "ram_used_mb": mem.used / 1024 / 1024,
        "ram_total_mb": mem.total / 1024 / 1024,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
        "uptime_seconds": uptime,
    }
