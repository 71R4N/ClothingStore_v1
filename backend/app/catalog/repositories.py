from app.core.repository import SqlAlchemyRepo
from app.catalog.models import Category, Product, ProductVariant
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload


class CategoryRepo(SqlAlchemyRepo):
    model = Category

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tree(self) -> list[Category]:
        """Возвращает корневые категории с подкатегориями (до 2 уровней)."""
        stmt = (
            select(self.model)
            .where(self.model.parent_id.is_(None))
            .options(
                selectinload(self.model.children).selectinload(self.model.children)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()


class ProductRepo(SqlAlchemyRepo):
    model = Product

    async def read_all_with_relations(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        order: str = "asc"
    ):
        stmt = select(self.model).options(
            selectinload(self.model.sizes),
            selectinload(self.model.colors),
            selectinload(self.model.variants).selectinload(ProductVariant.color),
            selectinload(self.model.variants).selectinload(ProductVariant.size),
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

        # Сортировка по цене через подзапрос
        if sort_by == "price":
            min_price_subq = (
                select(
                    ProductVariant.product_id,
                    func.min(ProductVariant.price).label("min_price")
                )
                .group_by(ProductVariant.product_id)
                .subquery()
            )
            stmt = stmt.outerjoin(min_price_subq, self.model.id == min_price_subq.c.product_id)
            sort_col = min_price_subq.c.min_price
            stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc().nulls_last())
        elif sort_by == "created_at":
            stmt = stmt.order_by(
                self.model.created_at.asc() if order == "asc" else self.model.created_at.desc()
            )
        else:
            stmt = stmt.order_by(self.model.id.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def read_by_slug(self, slug: str) -> Product | None:
        stmt = (
            select(self.model)
            .where(self.model.slug == slug)
            .options(
                selectinload(self.model.sizes),
                selectinload(self.model.colors),
                selectinload(self.model.variants).selectinload(ProductVariant.color),
                selectinload(self.model.variants).selectinload(ProductVariant.size),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ProductVariantRepo(SqlAlchemyRepo):
    model = ProductVariant

    async def bulk_create(self, variants: list[ProductVariant]) -> list[ProductVariant]:
        self.session.add_all(variants)
        await self.session.flush()
        return variants