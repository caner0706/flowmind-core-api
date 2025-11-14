# app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


def _create_engine():
    url = settings.DATABASE_URL
    connect_args = {}

    if url.startswith("sqlite"):
        # Örnek: sqlite:///./data/flowmind.db  ->  ./data/flowmind.db
        raw_path = url.replace("sqlite:///", "", 1)

        db_dir = os.path.dirname(raw_path)
        if db_dir and not os.path.exists(db_dir):
            # data/ klasörü yoksa oluştur
            os.makedirs(db_dir, exist_ok=True)

        # SQLite için gerekli
        connect_args = {"check_same_thread": False}

    return create_engine(url, connect_args=connect_args)


engine = _create_engine()

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
    """Uygulama açılışında tabloları oluştur."""
    # modelleri import et ki Base metadata dolsun
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
