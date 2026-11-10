import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


class Settings:
    app_name: str = os.getenv("APP_NAME", "SHY BOUTIQUE API")
    api_v1_prefix: str = "/api/v1"
    database_url: str
    admin_api_key: str
    cors_origins: list[str]
    uploads_dir: Path
    public_base_url: str

    def __init__(self) -> None:
        explicit_url = os.getenv("DATABASE_URL")
        if explicit_url:
            self.database_url = explicit_url
        else:
            self.database_url = URL.create(
                drivername="postgresql+psycopg",
                username=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "shy_db"),
            ).render_as_string(hide_password=False)
        self.admin_api_key = os.getenv("ADMIN_API_KEY", "")
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ]
        self.uploads_dir = Path(os.getenv("UPLOADS_DIR") or (BACKEND_DIR / "uploads"))
        self.public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
        self.uploads_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
