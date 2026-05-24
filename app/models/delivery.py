import enum
from datetime import date
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class DeliveryStatus(str, enum.Enum):
    pending = "pending"
    dispatched = "dispatched"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"
    returned = "returned"


class Delivery(Base, TimestampMixin):
    delivery_id: Mapped[UUID] = uuid_pk()
    order_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("order.order_id"), nullable=False)
    tracking_number: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    courier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dispatch_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivered_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus, name="delivery_status"), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_attempt_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    order = relationship("Order", back_populates="deliveries")
