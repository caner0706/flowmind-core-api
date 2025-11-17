# app/routers/auth.py
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.email_utils import send_verification_email

# 🔹 Router'ı MUTLAKA global seviyede tanımlıyoruz
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


def _generate_verification_code(length: int = 6) -> str:
    """Sadece rakamlardan oluşan doğrulama kodu üretir."""
    return "".join(random.choices(string.digits, k=length))


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class AuthUser(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: EmailStr
    is_verified: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


# ---------- Endpoints ----------

@router.post("/register", response_model=AuthUser, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> AuthUser:
    """
    Kayıt:
    - full_name (opsiyonel), email, password alır
    - Email zaten varsa 400
    - Şifreyi hashler
    - Doğrulama kodu üretip mail gönderir
    """
    existing = db.query(models.User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    verification_code = _generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        is_active=True,
        is_verified=False,
        verification_code=verification_code,
        verification_expires_at=expires_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✉️ Doğrulama maili gönder
    try:
        send_verification_email(user.email, verification_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User created but failed to send verification email: {e}",
        )

    return AuthUser(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


@router.post("/verify-email", response_model=AuthUser)
def verify_email(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> AuthUser:
    """
    Kullanıcı email + kod gönderir.
    """
    user: Optional[models.User] = (
        db.query(models.User).filter_by(email=payload.email).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    if not user.verification_code or not user.verification_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active verification code for this user.",
        )

    if user.verification_code != payload.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code.",
        )

    if datetime.utcnow() > user.verification_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired.",
        )

    user.is_verified = True
    user.verification_code = None
    user.verification_expires_at = None
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
    - Email doğrulanmamışsa 403
    """
    user: Optional[models.User] = (
        db.query(models.User).filter_by(email=payload.email).first()
    )
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified.",
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
