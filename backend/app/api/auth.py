from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.commerce import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    full_name: str
    phone: str
    password: str

class LoginIn(BaseModel):
    phone: str
    password: str

@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(400, "Phone already registered")
    user = User(full_name=data.full_name, phone=data.phone, password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token(str(user.id))
    return {"access_token": token, "user_id": user.id}

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(str(user.id))
    return {"access_token": token, "user_id": user.id}
