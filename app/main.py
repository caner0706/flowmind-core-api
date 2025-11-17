# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routers import health, workflows, auth   # 👈 auth da import edildi


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/",                 # Swagger root’ta
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api")       # /api/auth/...
    app.include_router(workflows.router, prefix="/api")  # /api/workflows/...

    @app.on_event("startup")
    def on_startup():
        init_db()

    return app


app = create_app()
