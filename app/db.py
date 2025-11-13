from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# SQLite için connect_args gerekli
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: request başına DB session üretir."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Uygulama ayağa kalkarken tüm tabloları otomatik oluşturur.
    Tabloların oluşması için app.models içindeki bütün SQLAlchemy modelleri
    Base.metadata'ya register edilir.
    """
    # Buradaki import çok kritik:
    #  - circular import engellenir
    #  - modeller Base'e register edilir
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
