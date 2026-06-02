from app.catalog.repositories import CategoryRepo, ProductRepo, ProductVariantRepo
from app.catalog.schemas import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate
from app.catalog.exceptions import CategoryNotFoundError, ProductNotFoundError
from app.catalog.models import Product, ProductSize, ProductColor, ProductVariant
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(
        self,
        category_repo: CategoryRepo,
        product_repo: ProductRepo,
        variant_repo: ProductVariantRepo
    ):
        self.category_repo = category_repo
        self.product_repo = product_repo
        self.variant_repo = variant_repo

    async def create_category(self, data: CategoryCreate) -> int:
        return await self.category_repo.create(data)

    async def get_category(self, category_id: int):
        cat = await self.category_repo.read_by_id(category_id)
        if not cat:
            raise CategoryNotFoundError()
        return cat

    async def get_category_by_slug(self, slug: str):
        cat = await self.category_repo.get_by_slug(slug)
        if not cat:
            raise CategoryNotFoundError()
        return cat

    async def get_category_tree(self):
        return await self.category_repo.get_tree()

    async def update_category(self, category_id: int, data: CategoryUpdate):
        await self.get_category(category_id)
        return await self.category_repo.update(data, category_id, exclude_unset=True)

    async def delete_category(self, category_id: int):
        await self.get_category(category_id)
        return await self.category_repo.delete(category_id)

    async def create_product(self, data: ProductCreate) -> int:
        product_data = data.model_dump(exclude={"sizes", "colors", "variants"})
        product_id = await self.product_repo.create(ProductCreate(**product_data))
        product = await self.product_repo.read_by_id(product_id)
        session = self.product_repo.session

        # Размеры
        size_map: dict[str, int] = {}
        for size_data in data.sizes:
            size = ProductSize(product_id=product_id, **size_data.model_dump())
            session.add(size)
            await session.flush()
            size_map[size_data.size_label] = size.id

        # Цвета
        color_map: dict[str, int] = {}
        for color_data in data.colors:
            color = ProductColor(product_id=product_id, **color_data.model_dump())
            session.add(color)
            await session.flush()
            color_map[color_data.color_name] = color.id

        # Варианты
        if data.variants:
            for variant_data in data.variants:
                variant = ProductVariant(product_id=product_id, **variant_data.model_dump())
                session.add(variant)
        else:
            # Автогенерация комбинаций sizes x colors
            for size_label, size_id in size_map.items():
                for color_name, color_id in color_map.items():
                    sku = f"{product.slug.upper()}-{size_label}-{color_name.replace(' ', '')}"
                    variant = ProductVariant(
                        product_id=product_id,
                        size_id=size_id,
                        color_id=color_id,
                        sku=sku,
                        stock_quantity=0,
                        price=0.0,
                    )
                    session.add(variant)

        await session.commit()
        return product_id

    async def get_product(self, product_id: int):
        prod = await self.product_repo.read_by_id(product_id)
        if not prod:
            raise ProductNotFoundError()
        return prod

    async def get_product_by_slug(self, slug: str):
        prod = await self.product_repo.read_by_slug(slug)
        if not prod:
            raise ProductNotFoundError()
        return prod

    async def get_products(
            self, skip: int = 0, limit: int = 20, category_id: Optional[int] = None,
            search: Optional[str] = None, min_price: Optional[float] = None,
            max_price: Optional[float] = None, sort_by: Optional[str] = None, order: str = "asc"
    ):
        return await self.product_repo.read_all_with_relations(
            skip, limit, category_id, search, min_price, max_price, sort_by, order
        )

    async def update_product(self, product_id: int, data: ProductUpdate):
        await self.get_product(product_id)
        return await self.product_repo.update(data, product_id, exclude_unset=True)

    async def delete_product(self, product_id: int):
        await self.get_product(product_id)
        return await self.product_repo.delete(product_id)
