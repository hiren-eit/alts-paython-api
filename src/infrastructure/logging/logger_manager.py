import logging
import sys
from typing import Optional
from configparser import ConfigParser
from pathlib import Path

from .db_logger import DatabaseHandler
from .app_insights_logger import AppInsightsHandler

# Load config.ini
_config = ConfigParser()
_config.read(Path(__file__).parent.parent.parent / "config.ini")

ACTIVE_LOGGER = _config.get("logging", "active_logger", fallback="db")  # db / app_insights
LOG_LEVEL = _config.get("logging", "log_level", fallback="INFO")

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    root_logger.handlers = []

    # Console handler always
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))
    root_logger.addHandler(console_handler)

    # Active backend
    if ACTIVE_LOGGER.lower() == "db":
        from src.core.settings import settings  # your dynamic DB URL
        if settings.postgres_url:
            db_handler = DatabaseHandler(settings.postgres_url)
            db_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
            db_handler.setFormatter(logging.Formatter("%(message)s"))
            root_logger.addHandler(db_handler)
            logging.getLogger(__name__).info("DB logger enabled")

    elif ACTIVE_LOGGER.lower() == "app_insights":
        from src.core.settings import settings
        if settings.app_insights_key:
            ai_handler = AppInsightsHandler(settings.app_insights_key)
            ai_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
            root_logger.addHandler(ai_handler)
            logging.getLogger(__name__).info("App Insights logger enabled")

def get_logger(name: str) -> logging.Logger:
    """Return Python-style logger"""
    return logging.getLogger(name)
