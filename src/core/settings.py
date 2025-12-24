import os
from configparser import ConfigParser
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# -----------------------------------------
# Load .env
# -----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -----------------------------------------
# Load config.ini
# -----------------------------------------
config = ConfigParser()
config.read(os.path.join(BASE_DIR, "config.ini"))


class Settings(BaseSettings):
    # ======================================================
    # Application Settings
    # ======================================================
    app_name: str = Field(default=config.get("app", "name", fallback="FastAPIApp"))
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    path_base: str = Field(default="/")
    secret_key: str = Field(default="xWUHZrhPACh6pk0cRFPPCC8z7UNIfu3h")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=1380) # 23 hours

    # ======================================================
    # CORS / Hosts
    # ======================================================
    cors_origins: str = Field(default="*")
    allowed_hosts: str = Field(default="*")

    # ======================================================
    # Database Switching (from config.ini)
    # ======================================================
    active_db: str = Field(default=config.get("database", "active_db", fallback="postgres"))

    # Env-driven actual connection strings
    postgres_url: str = Field(default=os.getenv("POSTGRES_URL", ""))
    sql_url: str = Field(default=os.getenv("SQL_URL", ""))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        model_config = {
            "extra": "allow"
        }

    # ======================================================
    # Client Details
    # ======================================================
    client_id: str = Field(default=os.getenv("CLIENT_ID", ""))
    client_secret: str = Field(default=os.getenv("CLIENT_SECRET", ""))


settings = Settings()


# ======================================================
# Resolve DB Connection String
# ======================================================
def get_connection_config():
    """
    Returns:
        tuple(connection_string: str, repository_path: str)
    """

    db = settings.active_db.lower()

    if db in ("postgres", "postgresql"):
        if not settings.postgres_url:
            raise ValueError("PostgreSQL connection string not set in .env (DATABASE_URL)")
        connection_string = settings.postgres_url
        repo_path = "src.infrastructure.database.postgres_repositories"

    elif db in ("sql", "sqlserver", "mssql"):
        if not settings.sql_url:
            raise ValueError("SQL Server connection string not set in .env (SQL_DATABASE_URL)")
        connection_string = settings.sql_url
        repo_path = "src.infrastructure.database.sqlserver_repositories"

    else:
        raise ValueError(f"Unsupported database type: {settings.active_db}")

    return connection_string, repo_path

