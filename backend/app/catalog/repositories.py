from app.core.repository import SqlAlchemyRepo
from app.catalog.models import Category, Product, ProductVariant
from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import selectinload


class CategoryRepo(SqlAlchemyRepo):
    model = Category

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tree(self) -> list[Category]:
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
            min_price: float | None = None,
            max_price: float | None = None,
            sort_by: str | None = None,
            order: str = "asc"
    ):
        stmt = select(Product).options(
            selectinload(Product.sizes),
            selectinload(Product.colors),
            selectinload(Product.variants).selectinload(ProductVariant.color),
            selectinload(Product.variants).selectinload(ProductVariant.size),
        )
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if search:
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        if min_price is not None or max_price is not None:
            price_conditions = []
            if min_price is not None:
                price_conditions.append(ProductVariant.price >= min_price)
            if max_price is not None:
                price_conditions.append(ProductVariant.price <= max_price)

            stmt = stmt.where(
                Product.id.in_(
                    select(ProductVariant.product_id).where(and_(*price_conditions))
                )
            )
        if sort_by == "price":
            min_price_subq = (
                select(
                    ProductVariant.product_id,
                    func.min(ProductVariant.price).label("min_price")
                )
                .group_by(ProductVariant.product_id)
                .subquery()
            )
            stmt = stmt.outerjoin(min_price_subq, Product.id == min_price_subq.c.product_id)
            sort_col = min_price_subq.c.min_price
            stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc().nulls_last())
        elif sort_by == "created_at":
            stmt = stmt.order_by(Product.created_at.asc() if order == "asc" else Product.created_at.desc())
        else:
            stmt = stmt.order_by(Product.id.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def read_by_slug(self, slug: str) -> Product | None:
        stmt = (
            select(self.model)
            .where(self.model.slug == slug)
            .options(selectinload(self.model.sizes),
                    selectinload(self.model.colors),
                    selectinload(self.model.variants).selectinload(ProductVariant.color),
                    selectinload(self.model.variants).selectinload(ProductVariant.size),))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ProductVariantRepo(SqlAlchemyRepo):
    model = ProductVariant

    async def bulk_create(self, variants: list[ProductVariant]) -> list[ProductVariant]:
        self.session.add_all(variants)
        await self.session.flush()
        return variants