from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.company import CompanyType
from app.models.customer import Customer
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order, OrderStatus, PaymentStatus
from app.repositories.base import BaseRepository
from app.schemas.delivery import DeliveryCreate, DeliveryRetry, DeliveryUpdate


class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Delivery, db)

    async def create(self, payload: DeliveryCreate) -> Delivery:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.customer).selectinload(Customer.company))
            .where(Order.order_id == payload.order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("Order not found")
        company = order.customer.company if order.customer else None
        if company and company.type == CompanyType.cash and order.payment_status != PaymentStatus.paid:
            raise BusinessRuleError("Cash customer orders must be paid before dispatch")
        if order.order_status not in {OrderStatus.confirmed, OrderStatus.dispatched}:
            raise BusinessRuleError("Only confirmed orders can be dispatched")
        order.order_status = OrderStatus.dispatched
        delivery = await self.repo.create({**payload.model_dump(), "delivery_status": DeliveryStatus.dispatched, "attempt_count": 1})
        await self.db.commit()
        return delivery

    async def get(self, delivery_id: UUID) -> Delivery:
        delivery = await self.repo.get("delivery_id", delivery_id)
        if not delivery:
            raise NotFoundError("Delivery not found")
        return delivery

    async def update(self, delivery_id: UUID, payload: DeliveryUpdate) -> Delivery:
        delivery = await self.get(delivery_id)
        data = payload.model_dump(exclude_unset=True)
        if data.get("delivery_status") == DeliveryStatus.delivered:
            data.setdefault("delivered_date", date.today())
            delivery.order.order_status = OrderStatus.delivered
        for key, value in data.items():
            setattr(delivery, key, value)
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def retry(self, delivery_id: UUID, payload: DeliveryRetry) -> Delivery:
        delivery = await self.get(delivery_id)
        if delivery.delivery_status != DeliveryStatus.failed:
            raise BusinessRuleError("Only failed deliveries can be retried")
        delivery.delivery_status = DeliveryStatus.dispatched
        delivery.attempt_count += 1
        delivery.last_attempt_date = date.today()
        delivery.failure_reason = None
        delivery.expected_delivery_date = payload.expected_delivery_date or delivery.expected_delivery_date
        delivery.notes = payload.notes or delivery.notes
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery
