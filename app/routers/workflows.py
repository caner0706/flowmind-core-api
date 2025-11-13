# app/routers/workflows.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowRead,
    WorkflowList,
)

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
)


# ---------------------------
# Create
# ---------------------------
@router.post(
    "",
    response_model=WorkflowRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow(
    workflow_in: WorkflowCreate,
    db: Session = Depends(get_db),
):
    db_workflow = models.Workflow(
        name=workflow_in.name,
        description=workflow_in.description,
        graph_json=workflow_in.graph_json,
        is_active=workflow_in.is_active,
        owner_id=workflow_in.owner_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


# ---------------------------
# List
# ---------------------------
@router.get("", response_model=WorkflowList)
def list_workflows(
    db: Session = Depends(get_db),
):
    workflows: List[models.Workflow] = (
        db.query(models.Workflow)
        .filter(models.Workflow.is_active == True)  # noqa: E712
        .order_by(models.Workflow.created_at.desc())
        .all()
    )
    return WorkflowList(items=workflows)


# ---------------------------
# Get by id
# ---------------------------
@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    return workflow


# ---------------------------
# Update
# ---------------------------
@router.put("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(
    workflow_id: int,
    workflow_in: WorkflowUpdate,
    db: Session = Depends(get_db),
):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    data = workflow_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(workflow, field, value)

    workflow.updated_at = datetime.utcnow()

    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


# ---------------------------
# Delete (hard delete – ileride soft delete'e çevrilebilir)
# ---------------------------
@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    db.delete(workflow)
    db.commit()
    return None
