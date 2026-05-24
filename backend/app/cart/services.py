from backend.app.cart.repositories import CartRepo
from backend.app.cart.schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from backend.app.catalog.repositories import ProductRepo  # позже импортируем
from decimal import Decimal
from typing import Optional

class CartService:
    def __init__(self, cart_repo: CartRepo, product_repo: ProductRepo):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    async def add_item(self, user_id: Optional[int], session_id: Optional[str], item: CartItemCreate) -> dict:
        existing = await self.cart_repo.get_item(user_id, session_id, item.product_id, item.size_id, item.color_id)
        if existing:
            existing.quantity += item.quantity
            await self.cart_repo.session.commit()
            return {"action": "updated", "id": existing.id}
        else:
            new_item = CartItem(
                user_id=user_id,
                session_id=session_id,
                product_id=item.product_id,
                size_id=item.size_id,
                color_id=item.color_id,
                quantity=item.quantity
            )
            self.cart_repo.session.add(new_item)
            await self.cart_repo.session.commit()
            return {"action": "added", "id": new_item.id}

    async def update_quantity(self, user_id: Optional[int], session_id: Optional[str], item_id: str, update: CartItemUpdate) -> bool:
        # найти item по id и проверить принадлежность
        item = await self.cart_repo.get_by_id(item_id)
        if not item:
            return False
        if (user_id and item.user_id == user_id) or (session_id and item.session_id == session_id):
            item.quantity = update.quantity
            await self.cart_repo.session.commit()
            return True
        return False

    async def remove_item(self, user_id: Optional[int], session_id: Optional[str], item_id: str) -> bool:
        item = await self.cart_repo.get_by_id(item_id)
        if not item:
            return False
        if (user_id and item.user_id == user_id) or (session_id and item.session_id == session_id):
            await self.cart_repo.session.delete(item)
            await self.cart_repo.session.commit()
            return True
        return False

    async def get_cart(self, user_id: Optional[int], session_id: Optional[str]) -> CartResponse:
        if user_id:
            items = await self.cart_repo.get_by_user(user_id)
        elif session_id:
            items = await self.cart_repo.get_by_session(session_id)
        else:
            items = []
        subtotal = Decimal(0)
        response_items = []
        for item in items:
            product = await self.product_repo.get_by_id(item.product_id)  # нужно реализовать в product_repo
            if product:
                price = product.price
                subtotal += price * item.quantity
                # Дополнительно получить изображение, размер, цвет
                image_url = product.images[0].url if product.images else None
                size_label = None
                if item.size_id:
                    size = next((s for s in product.sizes if s.id == item.size_id), None)
                    size_label = size.size_label if size else None
                color_name = None
                if item.color_id:
                    color = next((c for c in product.colors if c.id == item.color_id), None)
                    color_name = color.color_name if color else None
                response_items.append(CartItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    size_id=item.size_id,
                    color_id=item.color_id,
                    quantity=item.quantity,
                    added_at=item.added_at.isoformat(),
                    product_name=product.name,
                    product_price=price,
                    size_label=size_label,
                    color_name=color_name,
                    image_url=image_url
                ))
        return CartResponse(items=response_items, total_items=len(response_items), subtotal=subtotal)

    async def merge_guest_cart(self, user_id: int, session_id: str):
        # при логине переносим товары из гостевой корзины в пользовательскую
        guest_items = await self.cart_repo.get_by_session(session_id)
        for guest_item in guest_items:
            existing = await self.cart_repo.get_item(user_id, None, guest_item.product_id, guest_item.size_id, guest_item.color_id)
            if existing:
                existing.quantity += guest_item.quantity
            else:
                guest_item.user_id = user_id
                guest_item.session_id = None
                self.cart_repo.session.add(guest_item)
        await self.cart_repo.session.commit()
        # очистить гостевую корзину
        await self.cart_repo.clear_session_cart(session_id)
