from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.config import get_settings


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=None,
    )
    application.include_router(api_v1_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
