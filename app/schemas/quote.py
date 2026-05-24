from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field, model_validator

from app.models.quote import QuoteStatus
from app.schemas.common import ORMModel, QuoteOrderItem, Timestamped


class QuoteCreate(ORMModel):
    customer_id: UUID
    quote_date: date
    valid_till: date
    status: QuoteStatus = QuoteStatus.draft
    notes: str | None = Field(default=None, max_length=2000)
    items: list[QuoteOrderItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.valid_till < self.quote_date:
            raise ValueError("valid_till cannot be earlier than quote_date")
        return self


class QuoteUpdate(ORMModel):
    valid_till: date | None = None
    status: QuoteStatus | None = None
    notes: str | None = Field(default=None, max_length=2000)
    items: list[QuoteOrderItem] | None = Field(default=None, min_length=1)


class QuoteRead(Timestamped):
    quote_id: UUID
    customer_id: UUID
    quote_date: date
    valid_till: date
    status: QuoteStatus
    notes: str | None
    items: list[dict]
    total_amount: Decimal
