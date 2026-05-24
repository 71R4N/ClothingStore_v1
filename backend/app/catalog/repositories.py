from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from backend.app.core.repository import SQLAlchemyRepo
from backend.app.catalog.models import Category, Product, ProductImage, ProductSize, ProductColor
from backend.app.catalog.schemas import CategoryCreate, ProductCreate, ProductUpdate

class CategoryRepo(SQLAlchemyRepo[Category, CategoryCreate]):
    model = Category

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_tree(self) -> list[Category]:
        # простой вариант: все категории, потом группировка на клиенте
        stmt = select(Category)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

class ProductRepo(SQLAlchemyRepo[Product, ProductCreate]):
    model = Product

    async def get_by_slug(self, slug: str) -> Product | None:
        stmt = select(Product).options(
            selectinload(Product.images),
            selectinload(Product.sizes),
            selectinload(Product.colors),
            selectinload(Product.category)
        ).where(Product.slug == slug)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_category(self, category_id: int, limit: int = 100, offset: int = 0) -> list[Product]:
        stmt = select(Product).where(Product.category_id == category_id).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_filtered(self, filters: dict, limit: int = 100, offset: int = 0) -> list[Product]:
        # filters может содержать: category_id, min_price, max_price, search
        conditions = []
        if filters.get("category_id"):
            conditions.append(Product.category_id == filters["category_id"])
        if filters.get("min_price"):
            conditions.append(Product.price >= filters["min_price"])
        if filters.get("max_price"):
            conditions.append(Product.price <= filters["max_price"])
        if filters.get("search"):
            conditions.append(Product.name.ilike(f"%{filters['search']}%"))
        stmt = select(Product).where(and_(*conditions)).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
