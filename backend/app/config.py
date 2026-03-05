import os

OSRM_BASE_URL: str = os.getenv("OSRM_BASE_URL", "http://localhost:5000")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "10.0"))
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://routing:routing123@localhost:5432/routing",
)

_origins_env: str = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS: list[str] = ["*"] if _origins_env == "*" else [o.strip() for o in _origins_env.split(",")]
