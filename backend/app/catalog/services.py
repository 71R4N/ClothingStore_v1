from app.catalog.repositories import CategoryRepo, ProductRepo, SizeChartRepo
from app.catalog.schemas import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate
from app.catalog.exceptions import CategoryNotFoundError, ProductNotFoundError
from typing import Optional

class CatalogService:
    def __init__(self, category_repo: CategoryRepo, product_repo: ProductRepo, size_chart_repo: SizeChartRepo):
        self.category_repo = category_repo
        self.product_repo = product_repo
        self.size_chart_repo = size_chart_repo

    # Категории
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

    # Продукты
    async def create_product(self, data: ProductCreate) -> int:
        # product создаётся без вложенных коллекций, их нужно обрабатывать отдельно
        # Но в схеме данные уже все вместе, можно создать продукт и связанные сущности.
        # Упростим: создадим только продукт, а изображения, размеры и цвета добавим в репозитории.
        product_data = data.model_dump(exclude={"images", "sizes", "colors"})
        product_id = await self.product_repo.create(ProductCreate(**product_data))
        # TODO: добавить создание images, sizes, colors через отдельные репозитории, но для MVP можно пропустить
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

    async def get_products(self, skip: int = 0, limit: int = 20, category_id: Optional[int] = None,
                           search: Optional[str] = None, sort_by: Optional[str] = None, order: str = "asc"):
        return await self.product_repo.read_all_with_relations(skip, limit, category_id, search, sort_by, order)

    async def update_product(self, product_id: int, data: ProductUpdate):
        await self.get_product(product_id)
        return await self.product_repo.update(data, product_id, exclude_unset=True)

    async def delete_product(self, product_id: int):
        await self.get_product(product_id)
        return await self.product_repo.delete(product_id)

    # Размерные сетки
    async def get_size_chart(self, category: str, region: str):
        chart = await self.size_chart_repo.get_by_category_region(category, region)
        if not chart:
            raise NotFoundException(detail="Size chart not found")
        return chart
    