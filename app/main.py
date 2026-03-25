"""Application entry point."""

import logging

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine
from app.models import AuditLog, Role, User  # noqa: F401
from app.utils.tracking import RequestContextMiddleware

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
)
app.add_middleware(RequestContextMiddleware)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database schema."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Database initialization skipped: %s", exc)
    logger.info("Application startup completed")
