import threading
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import init_db, SessionLocal
from .config import settings
from .services.liveness import check_liveness
from .routers import agents, metrics, logs, alerts

def _liveness_loop():
    while True:
        time.sleep(settings.LIVENESS_CHECK_INTERVAL_SECONDS)
        db = SessionLocal()
        try:
            check_liveness(db)
        except Exception:
            pass
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    t = threading.Thread(target=_liveness_loop, daemon=True)
    t.start()
    yield

app = FastAPI(title="LAN Monitoring API", version="1.0.0", lifespan=lifespan)

try:
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception:
    pass

app.include_router(agents.router)
app.include_router(metrics.router)
app.include_router(logs.router)
app.include_router(alerts.router)

@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "LAN Monitoring API", "docs": "/docs"}
