from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core import settings
from src.core.settings import get_connection_config
from src.infrastructure.database.base import Base
# from src.infrastructure.database.postgres_repositories.file_manager_repository import PostgresFileManagerRepository
# from src.infrastructure.database.mssql_repositories.file_manager_repository import MssqlFileManagerRepository



# Resolve the correct connection string (based on config.ini + .env)
DATABASE_URL, active_repository_path = get_connection_config()

# SQLAlchemy engine (supports both Postgres & SQL Server)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True 
)

# SQLAlchemy session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# FastAPI dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---- IMPORTANT ----
# init_db() must import ALL database models so metadata is complete.
# This import MUST reference the INFRASTRUCTURE MODELS, not domain entities.
def init_db():
    from src.domain import entities   # noqa
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS frame"))
    Base.metadata.create_all(bind=engine)


# def get_repository():
#     db = settings.active_db.lower()

#     if db in ("postgres", "postgresql"):
#         return PostgresFileManagerRepository()

#     if db in ("sql", "sqlserver", "mssql"):
#         return MssqlFileManagerRepository()

#     raise ValueError(f"Unsupported DB type: {settings.active_db}")