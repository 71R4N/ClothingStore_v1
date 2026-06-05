from app.orders.repositories import OrderRepo, OrderItemRepo
from app.orders.schemas import OrderCreate, OrderStatusUpdate
from app.orders.exceptions import OrderNotFoundError, InvalidOrderStatusError
from app.cart.services import CartService
from app.catalog.repositories import ProductVariantRepo
from app.orders.models import Order, OrderItem, OrderStatus
from app.core.exceptions import ForbiddenException
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
        # 1. Получаем корзину
        cart_items = await self.cart_service.get_cart(user_id, session_id)
        if not cart_items:
            raise ValueError("Cart is empty")

        # 2. Проверяем наличие всех вариантов и вычисляем сумму
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
                "price_at_purchase": float(variant.price),
                "variant": variant  # Сохраняем ссылку на объект для оптимизации обновления остатков
            })

        # 3. Создаём заказ напрямую через ORM-модель, минуя Pydantic-схему OrderCreate
        order = Order(
            user_id=user_id,
            guest_email=data.guest_email,
            street=data.street,
            city=data.city,
            total=total,
            status="pending"
        )
        self.order_repo.session.add(order)
        await self.order_repo.session.flush()  # Фиксируем для генерации и получения order.id

        # 4. Создаём позиции заказа (OrderItem)
        for item_data in validated_items:
            order_item = OrderItem(
                order_id=order.id,
                variant_id=item_data["variant_id"],
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price_at_purchase"]
            )
            self.order_repo.session.add(order_item)

        # 5. Уменьшаем остатки на складе
        for item_data in validated_items:
            variant = item_data["variant"]
            variant.stock_quantity -= item_data["quantity"]

        # 6. Очищаем корзину пользователя/гостя
        await self.cart_service.clear_cart(user_id, session_id)

        # 7. Коммитим единую транзакцию
        await self.order_repo.session.commit()

        # 8. Возвращаем заказ с жадно подгруженными связями (items, variants)
        return await self.get_order(order.id)

    async def get_order(self, order_id: UUID) -> Order:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise OrderNotFoundError()
        return order

    async def get_user_orders(self, user_id: UUID, skip: int = 0, limit: int = 20):
        return await self.order_repo.get_user_orders(user_id, skip, limit)

    async def get_user_orders_filtered(
            self,
            user_id: UUID,
            status_group: str = "all",
            skip: int = 0,
            limit: int = 20
    ):
        """
        Возвращает заказы пользователя с фильтрацией по группе статусов.
        """
        return await self.order_repo.get_user_orders_by_group(
            user_id, status_group, skip, limit
        )

    async def cancel_order_by_user(self, order_id: UUID, user_id: UUID):
        """
        Позволяет пользователю отменить собственный заказ в статусе PENDING.
        """
        order = await self.get_order(order_id)

        if order.user_id != user_id:
            raise ForbiddenException(detail="Cannot cancel another user's order")

        if order.status != OrderStatus.PENDING:
            raise InvalidOrderStatusError(
                detail=f"Cannot cancel order in status {order.status}. Only pending orders can be cancelled."
            )

        # Возвращаем остатки на склад
        for item in order.items:
            variant = await self.variant_repo.read_by_id(item.variant_id)
            if variant:
                variant.stock_quantity += item.quantity

        # Обновляем статус заказа
        update_schema = OrderStatusUpdate(status=OrderStatus.CANCELLED.value)
        await self.order_repo.update(update_schema, order_id, exclude_unset=True)

        return await self.get_order(order_id)

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
