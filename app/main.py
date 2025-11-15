from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routers import health, workflows


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/",                 # 👈 Swagger root’ta
        redoc_url=None,               # İstersen açabilirsin
        openapi_url="/openapi.json",  # OpenAPI JSON
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(workflows.router, prefix="/api")  # /api/workflows/ vs.

    @app.on_event("startup")
    def on_startup():
        init_db()

    return app


app = create_app()
