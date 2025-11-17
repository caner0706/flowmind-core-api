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
    pass  # 👈 artı bir field yok
    
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


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
