# app/routers/auth.py
from datetime import datetime
from typing import Optional
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app import models


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# -----------------------
# Helpers
# -----------------------
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    return _hash_password(password) == password_hash


# -----------------------
# Schemas
# -----------------------
class RegisterRequest(BaseModel):
    full_name: Optional[str] = None
    email: str                       # ❗ EmailStr kaldırıldı
    password: str = Field(min_length=6)


class AuthUser(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


# -----------------------
# Register
# -----------------------
@router.post("/register", response_model=AuthUser, status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):

    # email varsa hata
    existing = db.query(models.User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        is_active=True,              # doğrulama yok → direk aktif
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# -----------------------
# Login
# -----------------------
@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=payload.email).first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User disabled.")

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    token = str(user.id)  # ❗ Çok basit token — Bearer <id>

    return LoginResponse(access_token=token, user=user)
