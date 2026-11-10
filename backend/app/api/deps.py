import secrets
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.commerce import User


def _user_from_token(authorization: str | None) -> int | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    user_id = decode_token(authorization.split(" ", 1)[1])
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    user_id = _user_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non authentifié.")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur inactif ou introuvable.")
    return user


def get_current_user_optional(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User | None:
    user_id = _user_from_token(authorization)
    if not user_id:
        return None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        return None
    return user


def require_admin(x_admin_api_key: str | None = Header(default=None)) -> None:
    configured = settings.admin_api_key
    if not configured:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Administration non configurée.")
    if not x_admin_api_key or not secrets.compare_digest(x_admin_api_key, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé d'administration invalide.")
