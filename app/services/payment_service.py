from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.order import Order, PaymentStatus
from app.models.payment import Payment, TransactionStatus
from app.repositories.base import BaseRepository
from app.schemas.payment import PaymentCreate


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Payment, db)

    async def paid_amount(self, order_id: UUID) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.order_id == order_id, Payment.payment_status == TransactionStatus.success
            )
        )
        return Decimal(result.scalar_one()).quantize(Decimal("0.01"))

    async def create(self, payload: PaymentCreate) -> Payment:
        order = await self.db.get(Order, payload.order_id, with_for_update=True)
        if not order:
            raise NotFoundError("Order not found")
        duplicate = await self.db.execute(
            select(Payment).where(Payment.transaction_reference == payload.transaction_reference)
        )
        if duplicate.scalar_one_or_none():
            raise ConflictError("Duplicate transaction_reference")

        if payload.payment_status == TransactionStatus.success:
            paid = await self.paid_amount(order.order_id)
            if paid + payload.amount > order.total_amount:
                raise BusinessRuleError("Payment would exceed order total")

        payment = await self.repo.create(payload.model_dump())
        await self._sync_order_payment_status(order)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def _sync_order_payment_status(self, order: Order) -> None:
        paid = await self.paid_amount(order.order_id)
        if paid <= 0:
            order.payment_status = PaymentStatus.unpaid
        elif paid < order.total_amount:
            order.payment_status = PaymentStatus.partial
        else:
            order.payment_status = PaymentStatus.paid
