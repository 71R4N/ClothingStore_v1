from app.core.repository import SqlAlchemyRepo
from app.payments.models import Payment
from sqlalchemy import select
from uuid import UUID
from typing import Optional


class PaymentRepo(SqlAlchemyRepo):
    model = Payment

    async def get_by_order_id(self, order_id: UUID) -> Optional[Payment]:
        stmt = (
            select(self.model)
            .where(self.model.order_id == order_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_yookassa_id(self, yookassa_payment_id: str) -> Optional[Payment]:
        stmt = select(self.model).where(
            self.model.yookassa_payment_id == yookassa_payment_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_order_payments(self, order_id: UUID) -> list[Payment]:
        stmt = (
            select(self.model)
            .where(self.model.order_id == order_id)
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self,
        payment_id: UUID,
        status: str,
        payment_method: Optional[str] = None,
        cancellation_reason: Optional[str] = None,
        cancellation_party: Optional[str] = None,
    ) -> Optional[Payment]:
        payment = await self.read_by_id(payment_id)
        if not payment:
            return None

        payment.status = status
        if payment_method:
            payment.payment_method = payment_method
        if cancellation_reason:
            payment.cancellation_reason = cancellation_reason
        if cancellation_party:
            payment.cancellation_party = cancellation_party

        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    