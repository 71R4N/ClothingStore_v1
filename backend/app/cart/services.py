from app.cart.repositories import CartRepo
from app.cart.schemas import CartItemCreate, CartItemUpdate
from app.cart.exceptions import CartItemNotFoundError, OutOfStockError
from app.catalog.repositories import ProductRepo
from typing import Optional
from uuid import UUID

class CartService:
    def __init__(self, cart_repo: CartRepo, product_repo: ProductRepo):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    async def add_to_cart(self, user_id: Optional[str], session_id: Optional[str], data: CartItemCreate):
        # Проверяем наличие товара и размер
        product = await self.product_repo.read_by_id(data.product_id)
        if not product:
            raise CartItemNotFoundError(detail="Product not found")
        if data.size_id:
            size = await self.product_repo.get_size_by_id(data.size_id)  # добавим метод
            if not size or size.product_id != product.id:
                raise CartItemNotFoundError(detail="Size not found")
            if size.stock_quantity < data.quantity:
                raise OutOfStockError()
        # Ищем существующий элемент корзины
        existing = await self.cart_repo.find_item(user_id, session_id, data.product_id, data.size_id, data.color_id)
        if existing:
            existing.quantity += data.quantity
            # обновим через репозиторий
            from app.cart.schemas import CartItemUpdate
            return await self.cart_repo.update(CartItemUpdate(quantity=existing.quantity), existing.id, exclude_unset=True)
        else:
            new_data = data.model_dump()
            new_data["user_id"] = user_id
            new_data["session_id"] = session_id
            return await self.cart_repo.create(CartItemCreate(**new_data))

    async def get_cart(self, user_id: Optional[str], session_id: Optional[str]) -> list:
        if user_id:
            return await self.cart_repo.get_user_cart(user_id)
        elif session_id:
            return await self.cart_repo.get_session_cart(session_id)
        return []

    async def update_item(self, item_id: str, quantity: int):
        item = await self.cart_repo.read_by_id(item_id)
        if not item:
            raise CartItemNotFoundError()
        # проверим сток
        if item.size_id:
            size = await self.product_repo.get_size_by_id(item.size_id)
            if size and size.stock_quantity < quantity:
                raise OutOfStockError()
        update = CartItemUpdate(quantity=quantity)
        return await self.cart_repo.update(update, item_id, exclude_unset=True)

    async def remove_item(self, item_id: str):
        await self.cart_repo.delete(item_id)

    async def clear_cart(self, user_id: Optional[str], session_id: Optional[str]):
        # реализуем в репозитории
        pass
