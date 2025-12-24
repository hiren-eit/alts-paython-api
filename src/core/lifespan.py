from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator
from src.infrastructure.database.connection_manager import init_db, engine
from src.infrastructure.logging.logger_manager import get_logger
from .settings import settings

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up...")

    try:
        init_db()
        logger.info("Database initialized successfully", extra={"database": "PostgreSQL"})
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)

    yield

    logger.info("Application shutting down...")
    try:
        if engine:
            engine.dispose()
            logger.info("Database connections closed", extra={"database": "PostgreSQL"})
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)
