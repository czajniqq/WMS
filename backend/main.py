import logging
import threading
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import os

from .database import init_db, SessionLocal
from .config import settings
from .services.liveness import check_liveness
from .routers import agents, metrics, logs, alerts
from .dependencies import verify_api_key

logger = logging.getLogger("wms")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
       "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com;"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter (single-process only)."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self._calls = calls
        self._period = period
        self._buckets: dict = defaultdict(list)
        self._request_count = 0
        self._cleanup_interval = 1000  # prune stale keys every N requests

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - self._period
        self._buckets[client] = [t for t in self._buckets[client] if t > cutoff]
        if len(self._buckets[client]) >= self._calls:
            return JSONResponse({"detail": "Too many requests"}, status_code=429)
        self._buckets[client].append(now)
        self._request_count += 1
        if self._request_count >= self._cleanup_interval:
            self._request_count = 0
            stale = [ip for ip, ts in self._buckets.items() if not any(t > cutoff for t in ts)]
            for ip in stale:
                del self._buckets[ip]
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        logger.info(
            "method=%s path=%s status=%d duration=%.3fs client=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration,
            request.client.host if request.client else "unknown",
        )
        return response


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

app = FastAPI(
    title="LAN Monitoring API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.API_KEY else "/docs",
    redoc_url=None if settings.API_KEY else "/redoc",
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    calls=settings.RATE_LIMIT_CALLS,
    period=settings.RATE_LIMIT_PERIOD_SECONDS,
)
app.add_middleware(RequestLoggingMiddleware)

try:
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception:
    pass

_auth = [Depends(verify_api_key)]
app.include_router(agents.router, dependencies=_auth)
app.include_router(metrics.router, dependencies=_auth)
app.include_router(logs.router, dependencies=_auth)
app.include_router(alerts.router, dependencies=_auth)

@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "LAN Monitoring API", "docs": "/docs"}

