import os
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import create_engine, pool
from alembic import context

# ✅ Load .env variables
load_dotenv()

# ✅ Alembic Config object
config = context.config
fileConfig(config.config_file_name)

# ✅ Import your Base + Models
from JDdb import Base
from db import Model  # This should import all models: User, JD, Profile, etc.

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        os.getenv("DATABASE_URL"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
