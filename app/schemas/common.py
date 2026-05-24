from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(25, ge=1, le=100)
    search: str | None = None
    sort_by: str | None = None
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int


class Timestamped(ORMModel):
    created_at: datetime
    updated_at: datetime


class QuoteOrderItem(BaseModel):
    item_id: int = Field(ge=1)
    product_id: UUID
    product_name: str | None = None
    description: str | None = None
    quantity: int = Field(gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_amount: Decimal | None = Field(default=None, ge=0)


class ServiceRequestItem(BaseModel):
    item_id: int = Field(ge=1)
    product_id: UUID
    product_name: str | None = None
    issue_description: str = Field(min_length=3, max_length=1000)
    quantity: int = Field(gt=0)
    requested_action: str = Field(pattern="^(return|replacement|complaint)$")


class IdempotencyHeaders(BaseModel):
    idempotency_key: str | None = None


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return value
    stripped = value.strip()
    if stripped and not all(ch.isdigit() or ch in "+- ()" for ch in stripped):
        raise ValueError("Invalid phone number")
    return stripped


class PhoneMixin(BaseModel):
    @field_validator("phone_no", check_fields=False)
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_phone(value)
