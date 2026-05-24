from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.models.payment import PaymentMethod, TransactionStatus
from app.schemas.common import ORMModel, Timestamped


class PaymentCreate(ORMModel):
    order_id: UUID
    payment_date: date
    amount: Decimal = Field(gt=0)
    payment_method: PaymentMethod
    transaction_reference: str = Field(min_length=1, max_length=255)
    payment_status: TransactionStatus = TransactionStatus.success
    remarks: str | None = Field(default=None, max_length=2000)


class PaymentRead(Timestamped):
    payment_id: UUID
    order_id: UUID
    payment_date: date
    amount: Decimal
    payment_method: PaymentMethod
    transaction_reference: str
    payment_status: TransactionStatus
    remarks: str | None
