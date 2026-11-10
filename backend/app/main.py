from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.catalog import router as catalog_router
from app.api.cart import router as cart_router
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.stock import router as stock_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="API e-commerce de SHY BOUTIQUE",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Admin-API-Key", "X-Guest-Token"],
)

app.mount("/uploads", StaticFiles(directory=str(settings.uploads_dir), check_dir=False), name="uploads")

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(catalog_router, prefix=settings.api_v1_prefix)
app.include_router(cart_router, prefix=settings.api_v1_prefix)
app.include_router(orders_router, prefix=settings.api_v1_prefix)
app.include_router(payments_router, prefix=settings.api_v1_prefix)
app.include_router(stock_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "shy-boutique-api"}


@app.get("/api/v1", tags=["meta"])
def api_root() -> dict[str, str]:
    return {"name": settings.app_name, "version": "0.3.0"}

