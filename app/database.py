# app/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator


# DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{hostname}:5432/{database}"
# "postgresql+asyncpg://kobo:DB@mPower@786@192.168.19.89:5432/dashboard_data"
DATABASE_URL = "postgresql+asyncpg://shafi:shafi123@192.168.19.89:5432/dashboard_data"
#postgresql+psycopg2

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session_maker = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session



# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/dashboard-data"

