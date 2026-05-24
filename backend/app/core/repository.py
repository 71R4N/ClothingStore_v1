from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import Base

SchemaType = TypeVar("SchemaType", bound=BaseModel)
ModelType = TypeVar("ModelType", bound=Base)

class AbstractRepo(ABC, Generic[ModelType, SchemaType]):
    @abstractmethod
    async def create(self, data: SchemaType) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: int, data: SchemaType, exclude_none: bool = True) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> int:
        raise NotImplementedError

class SQLAlchemyRepo(AbstractRepo[ModelType, SchemaType]):
    model: ModelType = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update(self, id: int, data: SchemaType, exclude_none: bool = True) -> Optional[ModelType]:
        stmt = update(self.model).where(self.model.id == id).values(**data.model_dump(exclude_none=exclude_none)).returning(self.model)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.scalar_one_or_none()

    async def delete(self, id: int) -> int:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        deleted_id = res.scalar_one_or_none()
        return deleted_id if deleted_id is not None else 0