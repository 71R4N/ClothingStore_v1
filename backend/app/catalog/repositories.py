from app.core.repository import SqlAlchemyRepo
from app.catalog.models import Category, Product, ProductImage, ProductSize, ProductColor, SizeChart
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

class CategoryRepo(SqlAlchemyRepo):
    model = Category

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tree(self) -> list[Category]:
        """Возвращает корневые категории с подкатегориями."""
        stmt = select(self.model).where(self.model.parent_id.is_(None)).options(
            selectinload(self.model.children).selectinload(self.model.children)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

class ProductRepo(SqlAlchemyRepo):
    model = Product

    async def read_all_with_relations(self, skip: int = 0, limit: int = 20, category_id: int | None = None,
                                     search: str | None = None, sort_by: str | None = None, order: str = "asc"):
        stmt = select(self.model).options(
            selectinload(self.model.images),
            selectinload(self.model.sizes),
            selectinload(self.model.colors)
        )
        if category_id:
            stmt = stmt.where(self.model.category_id == category_id)
        if search:
            stmt = stmt.where(
                or_(
                    self.model.name.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%")
                )
            )
        if sort_by == "price":
            col = self.model.price
            stmt = stmt.order_by(col.asc() if order == "asc" else col.desc())
        elif sort_by == "created_at":
            col = self.model.created_at
            stmt = stmt.order_by(col.asc() if order == "asc" else col.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def read_by_slug(self, slug: str) -> Product | None:
        stmt = select(self.model).where(self.model.slug == slug).options(
            selectinload(self.model.images),
            selectinload(self.model.sizes),
            selectinload(self.model.colors)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # в ProductRepo
    async def get_size_by_id(self, size_id: int):
        from app.catalog.models import ProductSize
        stmt = select(ProductSize).where(ProductSize.id == size_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

class SizeChartRepo(SqlAlchemyRepo):
    model = SizeChart

    async def get_by_category_region(self, category: str, region: str) -> SizeChart | None:
        stmt = select(self.model).where(self.model.category == category, self.model.region == region)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
