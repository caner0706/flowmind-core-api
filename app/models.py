# app/models.py

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db import Base


# --------------------------------------------------------------------
# Ortak mixin'ler
# --------------------------------------------------------------------


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)


# --------------------------------------------------------------------
# Kimlik / Workspace
# --------------------------------------------------------------------


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    owned_workspaces = relationship("Workspace", back_populates="owner")
    memberships = relationship("WorkspaceMember", back_populates="user")
    created_workflows = relationship(
        "Workflow",
        foreign_keys="Workflow.created_by_id",
        back_populates="created_by",
    )
    updated_workflows = relationship(
        "Workflow",
        foreign_keys="Workflow.updated_by_id",
        back_populates="updated_by",
    )
    triggered_runs = relationship(
        "WorkflowRun",
        back_populates="triggered_by",
        foreign_keys="WorkflowRun.triggered_by_id",
    )
    chat_sessions = relationship("ChatSession", back_populates="user")


class Workspace(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="owned_workspaces")

    members = relationship("WorkspaceMember", back_populates="workspace")
    workflows = relationship("Workflow", back_populates="workspace")
    api_tokens = relationship("ApiToken", back_populates="workspace")
    runs = relationship("WorkflowRun", back_populates="workspace")
    chat_sessions = relationship("ChatSession", back_populates="workspace")
    integrations = relationship("WorkspaceIntegration", back_populates="workspace")


class WorkspaceMember(Base, TimestampMixin):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # owner, admin, editor, viewer
    role = Column(String(50), nullable=False, default="editor")

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="memberships")


class ApiToken(Base, TimestampMixin):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    name = Column(String(255), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    scopes = Column(JSON, nullable=True)  # ["workflow:run", "workflow:read"]

    is_revoked = Column(Boolean, default=False, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", back_populates="api_tokens")


# --------------------------------------------------------------------
# Workflow modeli
# --------------------------------------------------------------------


class Workflow(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(255), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # ["ai", "slack", "cron"]

    is_template = Column(Boolean, default=False, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Trigger bilgisi
    trigger_type = Column(String(50), default="manual", nullable=False)  # manual, http, schedule, event

    # React Flow graf'ının ham hali
    graph_json = Column(Text, nullable=True)

    # Versioning için
    version = Column(Integer, default=1, nullable=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    workspace = relationship("Workspace", back_populates="workflows")
    nodes = relationship(
        "WorkflowNode",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )
    connections = relationship(
        "WorkflowConnection",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_workflows",
    )
    updated_by = relationship(
        "User",
        foreign_keys=[updated_by_id],
        back_populates="updated_workflows",
    )

    runs = relationship("WorkflowRun", back_populates="workflow")


class WorkflowNode(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflow_nodes"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)

    # Frontend'deki React Flow node id'si
    ui_id = Column(String(255), nullable=False, index=True)

    type = Column(String(100), nullable=False)  # llm_call, http_request, if, delay, map, vb.
    label = Column(String(255), nullable=True)

    config_json = Column(Text, nullable=True)    # parametreler, API key referansları, prompt vb.
    position_json = Column(Text, nullable=True)  # x,y,width,height vb.

    workflow = relationship("Workflow", back_populates="nodes")
    run_steps = relationship("WorkflowRunStep", back_populates="node")


class WorkflowConnection(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflow_connections"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)

    ui_id = Column(String(255), nullable=True)

    source_node_ui_id = Column(String(255), nullable=False)
    source_handle = Column(String(100), nullable=True)

    target_node_ui_id = Column(String(255), nullable=False)
    target_handle = Column(String(100), nullable=True)

    config_json = Column(Text, nullable=True)

    workflow = relationship("Workflow", back_populates="connections")


# --------------------------------------------------------------------
# Çalıştırma & log
# --------------------------------------------------------------------


class WorkflowRun(Base, TimestampMixin):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    triggered_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, running, success, failed, cancelled, timeout

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    input_json = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    workflow = relationship("Workflow", back_populates="runs")
    workspace = relationship("Workspace", back_populates="runs")
    triggered_by = relationship("User", back_populates="triggered_runs")

    steps = relationship(
        "WorkflowRunStep",
        back_populates="run",
        cascade="all, delete-orphan",
    )


class WorkflowRunStep(Base, TimestampMixin):
    __tablename__ = "workflow_run_steps"

    id = Column(Integer, primary key=True, index=True)
    run_id = Column(Integer, ForeignKey("workflow_runs.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("workflow_nodes.id"), nullable=False)

    status = Column(
        String(50),
        default="pending",
        nullable=False,
    )  # pending, running, success, failed, skipped

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    input_json = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    run = relationship("WorkflowRun", back_populates="steps")
    node = relationship("WorkflowNode", back_populates="run_steps")


# --------------------------------------------------------------------
# Chat oturumları
# --------------------------------------------------------------------


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)

    title = Column(String(255), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)

    workspace = relationship("Workspace", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    workflow = relationship("Workflow")

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)

    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    payload_json = Column(JSON, nullable=True)

    session = relationship("ChatSession", back_populates="messages")


# --------------------------------------------------------------------
# Entegrasyonlar
# --------------------------------------------------------------------


class IntegrationProvider(Base, TimestampMixin):
    __tablename__ = "integration_providers"

    id = Column(Integer, primary key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # "openai", "slack"
    display_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)  # "llm", "chat", "storage", "webhook"

    integrations = relationship("WorkspaceIntegration", back_populates="provider")


class WorkspaceIntegration(Base, TimestampMixin):
    __tablename__ = "workspace_integrations"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("integration_providers.id"), nullable=False)

    name = Column(String(255), nullable=False)
    config_json = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    workspace = relationship("Workspace", back_populates="integrations")
    provider = relationship("IntegrationProvider", back_populates="integrations")
