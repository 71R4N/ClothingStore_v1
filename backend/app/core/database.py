from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from sqlalchemy import func
from fastapi import Depends
from typing import Annotated, AsyncGenerator
from datetime import datetime
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
import uuid

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

engine = create_async_engine(settings.POSTGRES_DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

SessionDbDep = Annotated[AsyncSession, Depends(get_db_session)]

# Общие типы колонок
str_uniq = Annotated[str, mapped_column(unique=True)]
CreatedAtCol = Annotated[datetime, mapped_column(server_default=func.now(), nullable=False)]

class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata
    # id не задаём в базовом классе, чтобы каждая модель определяла свой тип