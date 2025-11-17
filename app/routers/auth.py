# app/routers/auth.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app import models

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    email: EmailStr


class AuthUser(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr


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
    Çok basit register:
    - Sadece email alır
    - Eğer email zaten varsa 400 döner
    """
    existing = db.query(models.User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = models.User(email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthUser(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Çok basit login:
    - Eğer email kayıtlıysa token olarak user.id döner
    - Şifre yok, sadece dev ortamı için.
    """
    user: Optional[models.User] = (
        db.query(models.User).filter_by(email=payload.email).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = str(user.id)  # 👈 geçici token

    return LoginResponse(
        access_token=token,
        user=AuthUser(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
        ),
    )
