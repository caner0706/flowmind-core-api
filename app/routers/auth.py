# app/routers/auth.py

from datetime import datetime
from typing import Optional
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app import models

# 🔹 Router
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# ---------- Helpers ----------

def _hash_password(password: str) -> str:
    """
    Basit SHA256 hash (sadece dev/test için).
    Üretim ortamında bcrypt/argon2 tercih edilmeli.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    return _hash_password(password) == password_hash


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class AuthUser(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: EmailStr
    is_verified: bool = True
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


# ---------- Endpoints ----------

@router.post("/register", response_model=AuthUser, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> AuthUser:
    """
    Kayıt:
    - full_name (opsiyonel), email, password alır
    - Email varsa 400 döner
    - Şifreyi hashleyip kaydeder
    - Email doğrulama / kod gönderme YOK
    """
    existing = db.query(models.User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        is_active=True,
        is_verified=True,        # ✅ Doğrudan doğrulanmış kabul ediyoruz
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthUser(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Giriş:
    - email + password alır
    - Şifre yanlışsa 401
    - Email doğrulama kontrolü YOK
    """
    user: Optional[models.User] = (
        db.query(models.User).filter_by(email=payload.email).first()
    )
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    token = str(user.id)  # geçici/dev token

    return LoginResponse(
        access_token=token,
        user=AuthUser(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ),
    )
