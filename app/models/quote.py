import enum
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class QuoteStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


class Quote(Base, TimestampMixin):
    quote_id: Mapped[UUID] = uuid_pk()
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("customer.customer_id"), nullable=False)
    quote_date: Mapped[date] = mapped_column(Date, nullable=False)
    valid_till: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[QuoteStatus] = mapped_column(Enum(QuoteStatus, name="quote_status"), nullable=False, default=QuoteStatus.draft)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    items: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    customer = relationship("Customer", back_populates="quotes")
    orders = relationship("Order", back_populates="quote")
