"""
Alembic Environment Configuration
Configures Alembic to use the same Base as the application.
"""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the root directory to the path so we can import app modules
# Path structure: backend/alembic/env.py -> backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Also add the backend/app directory to be sure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

# Now import from the app package
from app.database.session import Base
from app.database.models import *  # noqa: ensure all models are imported
from app.core.config import settings

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment or settings."""
    return os.getenv("DATABASE_URL") or settings.DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Build configuration dynamically
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
