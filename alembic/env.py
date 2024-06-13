import asyncio
import os
from logging.config import fileConfig
import sys

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# This line will add your application's directory to the Python path
# Adjust it if your project structure is different
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import your SQLAlchemy models here
from app.database import Base

# Load database URL from the configuration file
from app.database import DATABASE_URL  # Assuming your database URL is stored in a config file

# Interpret the config file for Python logging
fileConfig(context.config.config_file_name)

# Add your models to `target_metadata` variable
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    engine = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
