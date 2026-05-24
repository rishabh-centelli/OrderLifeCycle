from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class Product(Base, TimestampMixin):
    __table_args__ = (CheckConstraint("selling_price >= 0", name="ck_product_selling_price_non_negative"),)

    product_id: Mapped[UUID] = uuid_pk()
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(50), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    active_status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
