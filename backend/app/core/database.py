from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData, func
from datetime import datetime
from typing import Annotated
from fastapi import Depends

from backend.app.core.config import settings

# Конвенция именования индексов и ограничений
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

engine = create_async_engine(settings.POSTGRES_DB_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

SessionDbDep = Annotated[AsyncSession, Depends(get_db_session)]

# Общие аннотации для моделей
str_uniq = Annotated[str, mapped_column(unique=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]

class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
