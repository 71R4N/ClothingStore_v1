from backend.app.catalog.repositories import CategoryRepo, ProductRepo
from backend.app.catalog.schemas import CategoryCreate, CategoryResponse, ProductCreate, ProductResponse, ProductUpdate
from typing import Optional, List

class CatalogService:
    def __init__(self, category_repo: CategoryRepo, product_repo: ProductRepo):
        self.category_repo = category_repo
        self.product_repo = product_repo

    async def create_category(self, data: CategoryCreate) -> int:
        return await self.category_repo.create(data)

    async def get_categories(self) -> List[CategoryResponse]:
        cats = await self.category_repo.get_all()
        return [CategoryResponse.model_validate(c) for c in cats]

    async def get_category_by_slug(self, slug: str) -> Optional[CategoryResponse]:
        cat = await self.category_repo.get_by_slug(slug)
        return CategoryResponse.model_validate(cat) if cat else None

    async def create_product(self, data: ProductCreate) -> int:
        # Сначала создаём продукт без связей many-to-many? проще через репозиторий, но надо вставлять связанные данные.
        # В репозитории create сейчас вставляет только одну модель. Для связей нужно расширить.
        # Временно реализуем здесь:
        product_dict = data.model_dump(exclude={"images", "sizes", "colors"})
        product = Product(**product_dict)
        self.product_repo.session.add(product)
        await self.product_repo.session.flush()
        # Добавляем изображения, размеры, цвета
        for img in data.images:
            product.images.append(ProductImage(**img.model_dump()))
        for sz in data.sizes:
            product.sizes.append(ProductSize(**sz.model_dump()))
        for col in data.colors:
            product.colors.append(ProductColor(**col.model_dump()))
        await self.product_repo.session.commit()
        return product.id

    async def get_product_by_slug(self, slug: str) -> Optional[ProductResponse]:
        prod = await self.product_repo.get_by_slug(slug)
        return ProductResponse.model_validate(prod) if prod else None

    async def list_products(self, filters: dict, limit: int = 100, offset: int = 0) -> List[ProductResponse]:
        products = await self.product_repo.get_filtered(filters, limit, offset)
        return [ProductResponse.model_validate(p) for p in products]

    async def update_product(self, product_id: int, data: ProductUpdate) -> Optional[ProductResponse]:
        updated = await self.product_repo.update(product_id, data)
        if updated:
            return ProductResponse.model_validate(updated)
        return None
