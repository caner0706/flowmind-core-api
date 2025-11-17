# app/routers/auth.py
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.config import settings
from app.email_utils import send_verification_email

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# ---------- Helpers ----------

def _hash_password(password: str) -> str:
    """
    Basit SHA256 hash (sadece dev/test için).
    Üretim ortamında bcrypt/argon2 gibi güçlü bir yöntem tercih edilmeli.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    return _hash_password(password) == password_hash


def _generate_verification_code() -> str:
    """
    6 haneli sayısal kod üret (örnek: 483920).
    İstersen burada length'i değiştirebilirsin.
    """
    return f"{secrets.randbelow(900000) + 100000}"  # 100000 - 999999


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class AuthUser(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: EmailStr
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
    code: str = Field(min_length=4, max_length=16)


class VerifyEmailResponse(BaseModel):
    detail: str
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
    - E-posta doğrulama kodu oluşturur ve mail gönderir
    """
    existing = db.query(models.User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # ✅ Şifre hashle
    pwd_hash = _hash_password(payload.password)

    # ✅ Doğrulama kodu üret
    code = _generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
    )

    # ✅ Kullanıcı kaydı
    user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=pwd_hash,
        is_active=True,
        is_email_verified=False,
        verification_code=code,
        verification_expires_at=expires_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Mail gönder (SMTP yoksa sadece loglayacak)
    send_verification_email(to_email=user.email, code=code)

    return AuthUser(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> VerifyEmailResponse:
    """
    Kullanıcı mailine gelen kodu doğrular:
    - Email + code eşleşmezse 400
    - Kod süresi geçmişse 400
    - Başarılıysa is_email_verified = True yapılır
    """
    user: Optional[models.User] = (
        db.query(models.User).filter_by(email=payload.email).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    if not user.verification_code or not user.verification_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found, please register again.",
        )

    # Kod kontrolü
    if payload.code.strip() != user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )

    # Süre kontrolü
    if datetime.utcnow() > user.verification_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired, please register again.",
        )

    # ✅ Doğrulama başarılı
    user.is_email_verified = True
    user.verification_code = None
    user.verification_expires_at = None
    db.add(user)
    db.commit()
    db.refresh(user)

    return VerifyEmailResponse(
        detail="Email verified successfully",
        user=AuthUser(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Giriş:
    - email + password alır
    - Şifre doğrulanmazsa 401
    - Email doğrulanmamışsa 403
    - access_token olarak şimdilik user.id string’i döner
    """
    user: Optional[models.User] = (
        db.query(models.User).filter_by(email=payload.email).first()
    )
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    # Last login güncelle
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    token = str(user.id)  # 👈 geçici/dev token

    return LoginResponse(
        access_token=token,
        user=AuthUser(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
        ),
    )
