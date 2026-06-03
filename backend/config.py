from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # Database — SQLite for dev; use PostgreSQL in production
    DATABASE_URL: str = "sqlite:///./monitoring.db"

    # API authentication — set a strong secret in production; empty = auth disabled (dev mode)
    API_KEY: str = ""

    CPU_ALERT_THRESHOLD: float = 90.0
    RAM_ALERT_THRESHOLD: float = 90.0
    AGENT_OFFLINE_TIMEOUT_SECONDS: int = 300
    LIVENESS_CHECK_INTERVAL_SECONDS: int = 60

    # Rate limiting (requests per IP per period)
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD_SECONDS: int = 60

settings = Settings()
