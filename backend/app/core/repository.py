from abc import ABC, abstractmethod
from app.core.database import SessionDbDep
from sqlalchemy import insert, select, update, delete
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

SchemaType = TypeVar("SchemaType", bound=BaseModel)

class AbstractRepo(ABC):
    @abstractmethod
    async def create(self, data: SchemaType) -> int | str:
        raise NotImplementedError

    @abstractmethod
    async def read_by_id(self, id: int | str):
        raise NotImplementedError

    @abstractmethod
    async def read_all(self, skip: int = 0, limit: int = 100):
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: SchemaType, id: int | str, exclude_unset: bool = True):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int | str):
        raise NotImplementedError

class SqlAlchemyRepo(AbstractRepo):
    model = None

    def __init__(self, session: SessionDbDep):
        self.session = session

    async def create(self, data: SchemaType):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def read_by_id(self, id):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all(self, skip: int = 0, limit: int = 100):
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, data: SchemaType, id, exclude_unset: bool = True):
        values = data.model_dump(exclude_unset=exclude_unset)
        stmt = update(self.model).values(**values).where(self.model.id == id).returning(self.model)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, id):
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
