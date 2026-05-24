from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.models.order import OrderStatus, PaymentStatus
from app.schemas.common import ORMModel, QuoteOrderItem, Timestamped


class OrderCreate(ORMModel):
    customer_id: UUID
    quote_id: UUID | None = None
    order_date: date
    expected_delivery_date: date | None = None
    order_status: OrderStatus = OrderStatus.confirmed
    notes: str | None = Field(default=None, max_length=2000)
    items: list[QuoteOrderItem] | None = Field(default=None, min_length=1)


class OrderUpdate(ORMModel):
    expected_delivery_date: date | None = None
    order_status: OrderStatus | None = None
    notes: str | None = Field(default=None, max_length=2000)


class OrderRead(Timestamped):
    order_id: UUID
    customer_id: UUID
    quote_id: UUID | None
    order_date: date
    expected_delivery_date: date | None
    order_status: OrderStatus
    payment_status: PaymentStatus
    notes: str | None
    items: list[dict]
    total_amount: Decimal


class OrderCancel(ORMModel):
    reason: str | None = Field(default=None, max_length=1000)
