import httpx
from app.orders.repositories import OrderRepo, OrderItemRepo, PaymentRepo, ReturnRepo, AddressRepo
from app.orders.schemas import OrderCreate, OrderStatusUpdate, ReturnRequest
from app.orders.exceptions import OrderNotFoundError, PaymentFailedError, InvalidOrderStatusError
from app.cart.services import CartService  # для очистки корзины
from app.core.config import settings
from typing import Optional, List
from uuid import UUID

from app.orders.models import Order

from app.orders.models import PaymentTransaction, Return

from app.orders.schemas import OrderItemBase


class OrderService:
    def __init__(self, order_repo: OrderRepo, order_item_repo: OrderItemRepo,
                 payment_repo: PaymentRepo, return_repo: ReturnRepo,
                 address_repo: AddressRepo, cart_service: CartService):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.payment_repo = payment_repo
        self.return_repo = return_repo
        self.address_repo = address_repo
        self.cart_service = cart_service

    async def create_order(self, user_id: Optional[str], session_id: Optional[str], data: OrderCreate) -> Order:
        # Получаем корзину
        cart_items = await self.cart_service.get_cart(user_id, session_id)
        if not cart_items:
            raise ValueError("Cart is empty")

        # Вычисляем суммы
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        shipping_cost = 0.0  # можно рассчитать
        total = subtotal + shipping_cost - 0  # discount пока 0

        # Создаём заказ
        order = await self.order_repo.create(OrderCreate(
            user_id=user_id,
            guest_email=data.guest_email,
            status="pending",
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            shipping_address_id=data.shipping_address_id,
            payment_method=data.payment_method,
            payment_status="pending"
        ))

        # Переносим элементы корзины в order_items
        for item in cart_items:
            order_item = OrderItemBase(
                product_id=item.product_id,
                size_id=item.size_id,
                color_id=item.color_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            await self.order_item_repo.create(order_item, order_id=order.id)

        # Очищаем корзину
        await self.cart_service.clear_cart(user_id, session_id)

        return order

    async def get_order(self, order_id: str) -> Order:
        order = await self.order_repo.get_with_items(order_id)
        if not order:
            raise OrderNotFoundError()
        return order

    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 20):
        return await self.order_repo.get_user_orders(user_id, skip, limit)

    async def update_status(self, order_id: str, status: str):
        order = await self.get_order(order_id)
        # Проверка допустимости перехода
        valid_transitions = {
            "pending": ["paid", "cancelled"],
            "paid": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["delivered", "returned"],
            "delivered": ["returned"],
            "returned": [],
            "cancelled": []
        }
        if status not in valid_transitions.get(order.status, []):
            raise InvalidOrderStatusError()
        await self.order_repo.update(OrderStatusUpdate(status=status), order_id, exclude_unset=False)

    async def initiate_payment(self, order_id: str) -> PaymentTransaction:
        order = await self.get_order(order_id)
        if order.payment_status != "pending":
            raise PaymentFailedError(detail="Payment already processed")

        # Вызов T-Bank API (эмуляция)
        async with httpx.AsyncClient() as client:
            payload = {
                "order_id": str(order.id),
                "amount": order.total,
                "return_url": "http://localhost:5173/order/result"
            }
            # В реальности используем API Т-Банка
            # response = await client.post(f"{settings.TBANK_API_URL}/init", json=payload)
            # external_id = response.json().get("payment_id")
            # Эмуляция
            external_id = f"tb_{order.id}"
            payment_status = "success"  # sandbox

        payment = PaymentTransaction(
            order_id=order.id,
            provider="tbank",
            external_id=external_id,
            amount=order.total,
            status=payment_status,
            response_data={"sandbox": True}
        )
        payment = await self.payment_repo.create(payment)

        # Обновить статус заказа и платежа
        if payment_status == "success":
            await self.update_status(str(order.id), "paid")
            await self.order_repo.update({"payment_status": "success"}, order.id, exclude_unset=True)
        else:
            await self.order_repo.update({"payment_status": "failed"}, order.id, exclude_unset=True)

        return payment

    async def request_return(self, order_id: str, user_id: str, data: ReturnRequest) -> Return:
        order = await self.get_order(order_id)
        if order.status not in ["delivered", "shipped"]:
            raise InvalidOrderStatusError("Return not allowed in current status")
        ret = Return(
            order_id=order.id,
            user_id=user_id,
            reason=data.reason,
            comment=data.comment,
            items=data.items,
            status="requested"
        )
        return await self.return_repo.create(ret)

    async def process_return(self, return_id: str, status: str):
        ret = await self.return_repo.read_by_id(return_id)
        if not ret:
            raise NotFoundException(detail="Return request not found")
        ret.status = status
        if status in ["refunded", "rejected"]:
            ret.resolved_at = datetime.utcnow()
        return await self.return_repo.update(ret, return_id, exclude_unset=False)
    