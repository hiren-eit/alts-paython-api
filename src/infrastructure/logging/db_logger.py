from datetime import datetime, timezone
import logging
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class DatabaseHandler(logging.Handler):
    """Logging handler for DB logs."""

    def __init__(self, db_url: str):
        super().__init__()
        self.engine = create_engine(db_url, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False)

    def emit(self, record: logging.LogRecord):
        session = self.SessionLocal()
        try:
            message = record.getMessage()
            level = record.levelname
            template = record.msg
            if record.exc_info:
                formatter = self.formatter or logging.Formatter()
                exception_text = formatter.formatException(record.exc_info)
            else:
                exception_text = None
            properties = getattr(record, "properties", None)

            session.execute(
                text(
                    """
                    INSERT INTO frame.tbl_logs (id, message, message_template, level, timestamp, exception, log_event, created, is_active)
                    VALUES (:id, :message, :template, :level, NOW(), :exception, :props, :created, :is_active)"""
                ),
                {
                    "message": message,
                    "template": template,
                    "level": level,
                    "exception": exception_text,
                    "props": properties,
                    "created": datetime.now(timezone.utc),
                    "is_active": True,
                },
            )
            session.commit()
        except Exception as e:
            session.rollback()
            print("DB LOGGING ERROR:", e)
        finally:
            session.close()
