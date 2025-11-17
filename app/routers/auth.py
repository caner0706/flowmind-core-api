# app/routers/auth.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db import get_db
from app import models

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str


class AuthUser(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime


class LoginRequest(BaseModel):
    # Hem email hem username kabul edelim
    email_or_username: str


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
    - email + username alır
    - email veya username zaten varsa 400 döner
    """
    # Email kontrolü
    existing_email = db.query(models.User).filter_by(email=payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Username kontrolü
    existing_username = db.query(models.User).filter_by(username=payload.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = models.User(
        email=payload.email,
        username=payload.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthUser(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Çok basit login:
    - email VEYA username ile giriş
    - Şifre yok, sadece dev ortamı için.
    """
    user: Optional[models.User] = (
        db.query(models.User)
        .filter(
            or_(
                models.User.email == payload.email_or_username,
                models.User.username == payload.email_or_username,
            )
        )
        .first()
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
            username=user.username,
            created_at=user.created_at,
        ),
    )
