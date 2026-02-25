import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
from dotenv import load_dotenv

# Load .env so DATABASE_URL is available
load_dotenv()

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment (ignores the placeholder in alembic.ini)
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Set up loggers from the .ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and ALL models so autogenerate can detect every table
from app.db.base import Base           # noqa: E402
from app.db import models_import       # noqa: E402, F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the real DB)."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        connect_args={"sslmode": "require"},  # Required for Supabase
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
