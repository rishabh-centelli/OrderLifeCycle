from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.customer import Customer
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.quote import Quote, QuoteStatus
from app.repositories.base import BaseRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.common import build_priced_items, release_inventory, reserve_inventory


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Order, db)

    async def create(self, payload: OrderCreate) -> Order:
        if not await self.db.get(Customer, payload.customer_id):
            raise NotFoundError("Customer not found")

        if payload.quote_id:
            quote = await self.db.get(Quote, payload.quote_id)
            if not quote:
                raise NotFoundError("Quote not found")
            if quote.customer_id != payload.customer_id:
                raise BusinessRuleError("Quote belongs to another customer")
            if quote.status != QuoteStatus.approved:
                raise BusinessRuleError("Only approved quotes can be converted to orders")
            items, total = quote.items, quote.total_amount
        else:
            if not payload.items:
                raise BusinessRuleError("Manual order must contain at least one item")
            items, total = await build_priced_items(self.db, payload.items)

        await reserve_inventory(self.db, items)
        order = await self.repo.create(
            {
                **payload.model_dump(exclude={"items"}),
                "items": items,
                "total_amount": total,
                "payment_status": PaymentStatus.unpaid,
            }
        )
        await self.db.commit()
        return order

    async def get(self, order_id: UUID) -> Order:
        order = await self.repo.get("order_id", order_id)
        if not order or order.deleted_at is not None:
            raise NotFoundError("Order not found")
        return order

    async def update(self, order_id: UUID, payload: OrderUpdate) -> Order:
        order = await self.get(order_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel(self, order_id: UUID) -> Order:
        order = await self.get(order_id)
        if order.order_status in {OrderStatus.dispatched, OrderStatus.delivered}:
            raise BusinessRuleError("Dispatched or delivered orders cannot be cancelled")
        if order.order_status != OrderStatus.cancelled:
            await release_inventory(self.db, order.items)
            order.order_status = OrderStatus.cancelled
            order.deleted_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(order)
        return order
