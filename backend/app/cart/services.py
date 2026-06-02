from app.cart.repositories import CartRepo
from app.catalog.repositories import ProductVariantRepo
from app.cart.schemas import CartItemCreate, CartItemUpdate
from app.cart.exceptions import CartItemNotFoundError, OutOfStockError
from typing import Optional
from uuid import UUID


class CartService:
    def __init__(self, cart_repo: CartRepo, variant_repo: ProductVariantRepo):
        self.cart_repo = cart_repo
        self.variant_repo = variant_repo

    async def add_to_cart(
            self,
            user_id: Optional[UUID],
            session_id: Optional[str],
            data: CartItemCreate
    ):
        variant = await self.variant_repo.read_by_id(data.variant_id)
        if not variant:
            raise CartItemNotFoundError(detail="Product variant not found")

        if variant.stock_quantity < data.quantity:
            raise OutOfStockError()

        existing = await self.cart_repo.find_item(user_id, session_id, data.variant_id)

        if existing:
            new_quantity = existing.quantity + data.quantity
            if variant.stock_quantity < new_quantity:
                raise OutOfStockError()
            update_schema = CartItemUpdate(quantity=new_quantity)
            return await self.cart_repo.update(update_schema, existing.id, exclude_unset=True)
        else:
            item_data = data.model_dump()
            item_data["user_id"] = user_id
            item_data["session_id"] = session_id
            return await self.cart_repo.create_item(**item_data)

    async def get_cart(self, user_id: Optional[UUID], session_id: Optional[str]) -> list:
        if user_id:
            return await self.cart_repo.get_user_cart(user_id)
        elif session_id:
            return await self.cart_repo.get_session_cart(session_id)
        return []

    async def update_item(self, item_id: UUID, quantity: int):
        item = await self.cart_repo.read_by_id(item_id)
        if not item:
            raise CartItemNotFoundError()

        variant = await self.variant_repo.read_by_id(item.variant_id)
        if variant and variant.stock_quantity < quantity:
            raise OutOfStockError()

        update = CartItemUpdate(quantity=quantity)
        return await self.cart_repo.update(update, item_id, exclude_unset=True)

    async def remove_item(self, item_id: UUID):
        await self.cart_repo.delete(item_id)

    async def clear_cart(self, user_id: Optional[UUID], session_id: Optional[str]):
        await self.cart_repo.clear_cart(user_id, session_id)