import enum
from datetime import date
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class ServiceRequestType(str, enum.Enum):
    return_request = "return"
    replacement = "replacement"
    complaint = "complaint"


class ServiceRequestStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class ServiceRequest(Base, TimestampMixin):
    request_id: Mapped[UUID] = uuid_pk()
    order_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("customer.customer_id"), nullable=False)
    request_date: Mapped[date] = mapped_column(Date, nullable=False)
    request_type: Mapped[ServiceRequestType] = mapped_column(
        Enum(ServiceRequestType, name="service_request_type", values_callable=enum_values), nullable=False
    )
    status: Mapped[ServiceRequestStatus] = mapped_column(
        Enum(ServiceRequestStatus, name="service_request_status", values_callable=enum_values), nullable=False
    )
    resolution_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    items: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)

    order = relationship("Order", back_populates="service_requests")
