# app/routers/admin.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas import WorkflowRead

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


# ==========================
# Users – tüm kullanıcıları listele
# ==========================

@router.get("/users/")
def list_users(
    db: Session = Depends(get_db),
):
    """
    Tüm kullanıcıları basit bir JSON listesi olarak döner.
    Admin panelde tabloya basmak için.
    """
    users: List[models.User] = db.query(models.User).order_by(models.User.id.asc()).all()

    result = []
    for u in users:
        result.append(
            {
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "is_active": u.is_active,
                "created_at": (
                    u.created_at.isoformat() + "Z" if isinstance(u.created_at, datetime) else u.created_at
                ),
                "last_login": (
                    u.last_login.isoformat() + "Z" if isinstance(u.last_login, datetime) and u.last_login else None
                ),
            }
        )

    return result


# ==========================
# Workflows – admin görünümü
# ==========================

@router.get("/workflows/", response_model=List[WorkflowRead])
def admin_list_workflows(
    owner_id: Optional[int] = Query(default=None, description="Opsiyonel filtre: belirli owner_id için"),
    db: Session = Depends(get_db),
) -> List[WorkflowRead]:
    """
    Admin için tüm workflow kayıtlarını listeler.
    (owner filtresi opsiyonel)
    Auth yok – sadece internal kullanım.
    """
    query = db.query(models.Workflow)

    if owner_id is not None:
        query = query.filter(models.Workflow.owner_id == owner_id)

    workflows: List[models.Workflow] = (
        query.order_by(models.Workflow.created_at.desc()).all()
    )
    return workflows


@router.get("/workflows/{workflow_id}", response_model=WorkflowRead)
def admin_get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
) -> WorkflowRead:
    """
    Admin için tek bir workflow getirir (auth yok).
    """
    wf = db.query(models.Workflow).filter_by(id=workflow_id).first()
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    return wf
