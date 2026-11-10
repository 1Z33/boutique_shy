import secrets
from fastapi import Header, HTTPException, status
from app.core.config import settings

def require_admin(x_admin_api_key: str | None = Header(default=None)) -> None:
    configured = settings.admin_api_key
    if not configured:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Administration non configurée.")
    if not x_admin_api_key or not secrets.compare_digest(x_admin_api_key, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé d'administration invalide.")
