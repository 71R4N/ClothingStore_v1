from app.orders.repositories import OrderRepo, OrderItemRepo
from app.orders.schemas import OrderCreate, OrderStatusUpdate
from app.orders.exceptions import OrderNotFoundError, InvalidOrderStatusError
from app.cart.services import CartService
from app.catalog.repositories import ProductVariantRepo
from app.orders.models import Order, OrderItem
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
            self,
            order_repo: OrderRepo,
            order_item_repo: OrderItemRepo,
            cart_service: CartService,
            variant_repo: ProductVariantRepo
    ):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.cart_service = cart_service
        self.variant_repo = variant_repo

    async def create_order(
            self,
            user_id: Optional[UUID],
            session_id: Optional[str],
            data: OrderCreate
    ) -> Order:
        # Получаем корзину
        cart_items = await self.cart_service.get_cart(user_id, session_id)
        if not cart_items:
            raise ValueError("Cart is empty")

        # Проверяем наличие всех вариантов и вычисляем сумму
        total = 0.0
        validated_items = []

        for cart_item in cart_items:
            variant = await self.variant_repo.read_by_id(cart_item.variant_id)
            if not variant:
                raise ValueError(f"Variant {cart_item.variant_id} not found")
            if variant.stock_quantity < cart_item.quantity:
                raise ValueError(f"Insufficient stock for variant {variant.sku}")
            item_total = float(variant.price) * cart_item.quantity
            total += item_total

            validated_items.append({
                "variant_id": cart_item.variant_id,
                "quantity": cart_item.quantity,
                "price_at_purchase": float(variant.price)
            })

        # Создаём заказ
        order_data = data.model_dump()
        order_data["user_id"] = user_id
        order_data["total"] = total
        order_data["status"] = "pending"

        order = await self.order_repo.create(OrderCreate(**order_data))

        # Создаём элементы заказа
        for item_data in validated_items:
            order_item = OrderItem(
                order_id=order,
                variant_id=item_data["variant_id"],
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price_at_purchase"]
            )
            await self.order_item_repo.create(order_item)

        for item_data in validated_items:
            variant = await self.variant_repo.read_by_id(item_data["variant_id"])
            variant.stock_quantity -= item_data["quantity"]
            await self.variant_repo.update(variant, variant.id)

        # Очищаем корзину
        await self.cart_service.clear_cart(user_id, session_id)

        # Возвращаем заказ с подгруженными items
        return await self.get_order(order)

    async def get_order(self, order_id: UUID) -> Order:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise OrderNotFoundError()
        return order

    async def get_user_orders(self, user_id: UUID, skip: int = 0, limit: int = 20):
        return await self.order_repo.get_user_orders(user_id, skip, limit)

    async def update_status(self, order_id: UUID, status: str):
        order = await self.get_order(order_id)

        # Проверка допустимости перехода
        valid_transitions = {
            "pending": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": [],
            "cancelled": []
        }

        if status not in valid_transitions.get(order.status, []):
            raise InvalidOrderStatusError(
                detail=f"Cannot transition from {order.status} to {status}"
            )

        update_schema = OrderStatusUpdate(status=status)
        await self.order_repo.update(update_schema, order_id, exclude_unset=True)
        return await self.get_order(order_id)