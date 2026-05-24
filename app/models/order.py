import enum
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, uuid_pk


class OrderStatus(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"
    cancelled = "cancelled"
    dispatched = "dispatched"
    delivered = "delivered"
    returned = "returned"


class PaymentStatus(str, enum.Enum):
    unpaid = "unpaid"
    partial = "partial"
    paid = "paid"
    refunded = "refunded"


class Order(Base, TimestampMixin, SoftDeleteMixin):
    order_id: Mapped[UUID] = uuid_pk()
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("customer.customer_id"), nullable=False)
    quote_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("quote.quote_id"), nullable=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    order_status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, name="order_status"), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, name="payment_status"), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    items: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    customer = relationship("Customer", back_populates="orders")
    quote = relationship("Quote", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    deliveries = relationship("Delivery", back_populates="order", cascade="all, delete-orphan")
    service_requests = relationship("ServiceRequest", back_populates="order")
