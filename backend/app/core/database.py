from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from sqlalchemy import func
from fastapi import Depends
from typing import Annotated, AsyncGenerator
from datetime import datetime
from sqlalchemy import MetaData
import logging

logger = logging.getLogger(__name__)

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
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


SessionDbDep = Annotated[AsyncSession, Depends(get_db_session)]

# Общие типы колонок
str_uniq = Annotated[str, mapped_column(unique=True)]
CreatedAtCol = Annotated[datetime, mapped_column(server_default=func.now(), nullable=False)]


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata


from app.users.models import User, UserSession
from app.catalog.models import Category, Product, ProductSize, ProductColor, ProductVariant
from app.cart.models import CartItem
from app.orders.models import Order, OrderItem
from app.wishlist.models import Wishlist
from app.tryon.models import TryOnSession
from app.payments.models import Payment
from app.returns.models import Return, ReturnItem
