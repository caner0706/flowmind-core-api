# app/routers/workflows.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas import (
    WorkflowCreate,
    WorkflowRead,
    WorkflowUpdate,
)
from app.security import get_current_user  # 👈 Auth dependency


router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
)


@router.get("/", response_model=List[WorkflowRead])
def list_workflows(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> List[WorkflowRead]:
    """
    Giriş yapmış kullanıcının tüm workflow kayıtlarını listele.
    """
    workflows: List[models.Workflow] = (
        db.query(models.Workflow)
        .filter_by(owner_id=current_user.id)
        .order_by(models.Workflow.created_at.desc())
        .all()
    )
    return workflows


@router.post(
    "/", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED
)
def create_workflow(
    payload: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> WorkflowRead:
    """
    Giriş yapmış kullanıcı için yeni bir workflow yarat.
    owner_id dışarıdan gelmez, current_user'dan alınır.
    """
    wf = models.Workflow(
        name=payload.name,
        description=payload.description,
        graph_json=payload.graph_json,
        is_active=payload.is_active,
        owner_id=current_user.id,  # 👈 kritik nokta
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> WorkflowRead:
    """
    Tek bir workflow getir.
    Sadece sahibiyse görebilir.
    """
    wf = db.query(models.Workflow).filter_by(id=workflow_id).first()
    if not wf or wf.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    return wf


@router.put("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(
    workflow_id: int,
    payload: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> WorkflowRead:
    """
    Workflow güncelle.
    Kullanıcı sadece kendi workflow'unu güncelleyebilir.
    """
    wf = db.query(models.Workflow).filter_by(id=workflow_id).first()
    if not wf or wf.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wf, field, value)

    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    """
    Workflow sil.
    Kullanıcı sadece kendi workflow'unu silebilir.
    """
    wf = db.query(models.Workflow).filter_by(id=workflow_id).first()
    if not wf or wf.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    db.delete(wf)
    db.commit()
    return None
