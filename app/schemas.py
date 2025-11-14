# app/schemas.py
from datetime import datetime
from typing import Any, Optional, List, Dict

from pydantic import BaseModel


# ==============================
# Workflow Schemas
# ==============================
class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    # React Flow graph (nodes + edges)
    graph_json: Dict[str, Any] = {}
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    owner_id: Optional[int] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowRead(WorkflowBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WorkflowList(BaseModel):
    items: List[WorkflowRead]

    class Config:
        orm_mode = True
