import enum
from uuid import UUID

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class CompanyType(str, enum.Enum):
    credit = "credit"
    cash = "cash"


class Company(Base, TimestampMixin):
    company_id: Mapped[UUID] = uuid_pk()
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    gst_number: Mapped[str | None] = mapped_column(String(15), unique=True, nullable=True)
    phone_no: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    type: Mapped[CompanyType] = mapped_column(Enum(CompanyType, name="company_type"), nullable=False)

    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
