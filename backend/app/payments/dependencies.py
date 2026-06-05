from typing import Annotated
from fastapi import Depends
from app.core.database import SessionDbDep
from app.payments.repositories import PaymentRepo
from app.payments.services import PaymentService
from app.orders.repositories import OrderRepo


def get_payment_service(session: SessionDbDep) -> PaymentService:
    """Фабрика для создания PaymentService."""
    payment_repo = PaymentRepo(session)
    order_repo = OrderRepo(session)
    return PaymentService(payment_repo, order_repo)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
