from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class Customer(Base, TimestampMixin):
    __table_args__ = (UniqueConstraint("company_id", "email", name="uq_customer_company_email"),)

    customer_id: Mapped[UUID] = uuid_pk()
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_no: Mapped[str | None] = mapped_column(String(30), nullable=True)

    company = relationship("Company", back_populates="customers")
    quotes = relationship("Quote", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
