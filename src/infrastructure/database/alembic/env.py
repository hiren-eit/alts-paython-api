import os
import sys

# Correctly add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the rest of the libraries
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv
from src.infrastructure.database.base import Base  # Your declarative Base model
from src.domain.entities.file_manager import FileManager
from src.domain.entities.logger import Logs
from src.domain.entities import account_master,extract_file,file_configuration,firm_master,publishing_control 
from src.core.settings import get_connection_config
# Load environment variables from .env file
load_dotenv()

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogeneration
target_metadata = Base.metadata

# Dynamically get the connection string based on config.ini
DATABASE_URL, active_repository_path = get_connection_config()

# --- Run migrations in offline mode ---
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()



# --- Run migrations in online mode ---
def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Create a connection engine using the URL
    connectable = engine_from_config(
        {'sqlalchemy.url': DATABASE_URL},  # Pass the URL directly into the engine configuration
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,  # Use no connection pooling
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


# Choose whether to run migrations offline or online based on the context
if context.is_offline_mode():
    run_migrations_offline()  # Run in offline mode
else:
    run_migrations_online()  # Run in online mode
