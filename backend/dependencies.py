from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(_api_key_header)) -> None:
    """Validate X-API-Key header. Auth is skipped when API_KEY is not configured (dev mode)."""
    if not settings.API_KEY:
        return  # Auth disabled — API_KEY not set
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
