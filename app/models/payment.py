import enum
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    bank_transfer = "bank_transfer"
    card = "card"
    upi = "upi"
    cheque = "cheque"
    credit = "credit"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"


class Payment(Base, TimestampMixin):
    payment_id: Mapped[UUID] = uuid_pk()
    order_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, name="payment_method"), nullable=False)
    transaction_reference: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    payment_status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status"), nullable=False
    )
    remarks: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    order = relationship("Order", back_populates="payments")
