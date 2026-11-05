from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.catalog import router as catalog_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="API e-commerce de SHY BOUTIQUE",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Admin-API-Key"],
)

app.include_router(catalog_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "shy-boutique-api"}


@app.get("/api/v1", tags=["meta"])
def api_root() -> dict[str, str]:
    return {"name": settings.app_name, "version": "0.2.0"}
