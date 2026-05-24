from datetime import date
from uuid import UUID

from pydantic import Field, model_validator

from app.models.delivery import DeliveryStatus
from app.schemas.common import ORMModel, Timestamped


class DeliveryCreate(ORMModel):
    order_id: UUID
    tracking_number: str | None = Field(default=None, max_length=255)
    courier_name: str | None = Field(default=None, max_length=255)
    dispatch_date: date | None = None
    expected_delivery_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class DeliveryUpdate(ORMModel):
    tracking_number: str | None = Field(default=None, max_length=255)
    courier_name: str | None = Field(default=None, max_length=255)
    dispatch_date: date | None = None
    expected_delivery_date: date | None = None
    delivered_date: date | None = None
    delivery_status: DeliveryStatus | None = None
    failure_reason: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_failure_reason(self):
        if self.delivery_status == DeliveryStatus.failed and not self.failure_reason:
            raise ValueError("failure_reason is required when delivery_status is failed")
        return self


class DeliveryRetry(ORMModel):
    expected_delivery_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class DeliveryRead(Timestamped):
    delivery_id: UUID
    order_id: UUID
    tracking_number: str | None
    courier_name: str | None
    dispatch_date: date | None
    expected_delivery_date: date | None
    delivered_date: date | None
    delivery_status: DeliveryStatus
    attempt_count: int
    last_attempt_date: date | None
    failure_reason: str | None
    notes: str | None
