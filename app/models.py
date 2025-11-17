from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db import Base


# ============================================================
# USERS (optional for now — ileride auth eklenecek)
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)          # İsim (opsiyonel)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)     # Şifre hash’i
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # ✅ Yeni alanlar: e-posta doğrulama için
    is_email_verified = Column(Boolean, default=False)         # Doğrulandı mı?
    verification_code = Column(String, nullable=True)          # Son gönderilen kod
    verification_expires_at = Column(DateTime, nullable=True)  # Kodun son kullanma tarihi

    workflows = relationship("Workflow", back_populates="owner")
    chat_sessions = relationship("ChatSession", back_populates="user")


# ============================================================
# WORKFLOWS – Kullanıcıların oluşturduğu n8n benzeri akışlar
# ============================================================
class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    graph_json = Column(JSON, nullable=False)     # tüm node/edge yapısı
    is_active = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="workflows")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# WORKFLOW RUNS – Workflow çalıştırma geçmişi
# ============================================================
class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    status = Column(String, default="running")  # running | success | failed
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)


# ============================================================
# NODES – Her workflow içindeki tek tek node’lar
# ============================================================
class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    node_id = Column(String, nullable=False)       # frontend'deki unique node key
    type = Column(String, nullable=False)          # ai, http, timer, condition...
    config = Column(JSON, nullable=True)           # node'un ayarları (prompt, url, headers)

    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)


# ============================================================
# INTEGRATION PROVIDERS — OpenAI, HF, Slack, Gmail vs.
# ============================================================
class IntegrationProvider(Base):
    __tablename__ = "integration_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)            # "openai", "huggingface", "slack"
    category = Column(String, nullable=True)         # "llm", "storage", "messaging"
    base_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)


# ============================================================
# USER CREDENTIALS – Kullanıcı kendi API keylerini girer
# ============================================================
class UserCredential(Base):
    __tablename__ = "user_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("integration_providers.id"))
    credential_json = Column(JSON, nullable=False)   # {"api_key": "...", "org_id": "..."}
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# CHAT SESSION — Chat ara yüzü konuşmaları tutar
# ============================================================
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


# ============================================================
# CHAT MESSAGE – Chat içerisindeki mesajlar
# ============================================================
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String, nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")




