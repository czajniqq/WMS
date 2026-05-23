from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    DATABASE_URL: str = "sqlite:///./monitoring.db"
    CPU_ALERT_THRESHOLD: float = 90.0
    RAM_ALERT_THRESHOLD: float = 90.0
    AGENT_OFFLINE_TIMEOUT_SECONDS: int = 300
    LIVENESS_CHECK_INTERVAL_SECONDS: int = 60

settings = Settings()
