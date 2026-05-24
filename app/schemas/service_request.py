from datetime import date
from uuid import UUID

from pydantic import Field

from app.models.service_request import ServiceRequestStatus, ServiceRequestType
from app.schemas.common import ORMModel, ServiceRequestItem, Timestamped


class ServiceRequestCreate(ORMModel):
    order_id: UUID
    customer_id: UUID
    request_date: date
    request_type: ServiceRequestType
    items: list[ServiceRequestItem] = Field(min_length=1)


class ServiceRequestUpdate(ORMModel):
    status: ServiceRequestStatus | None = None
    resolution_date: date | None = None
    resolution_notes: str | None = Field(default=None, max_length=2000)


class ServiceRequestRead(Timestamped):
    request_id: UUID
    order_id: UUID
    customer_id: UUID
    request_date: date
    request_type: ServiceRequestType
    status: ServiceRequestStatus
    resolution_date: date | None
    resolution_notes: str | None
    items: list[dict]
