from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel, Timestamped


class ProductBase(ORMModel):
    product_name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=120)
    unit_of_measure: str = Field(min_length=1, max_length=50)
    selling_price: Decimal = Field(ge=0)
    active_status: bool = True


class ProductCreate(ProductBase):
    initial_quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=0, ge=0)


class ProductUpdate(ORMModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=120)
    unit_of_measure: str | None = Field(default=None, min_length=1, max_length=50)
    selling_price: Decimal | None = Field(default=None, ge=0)
    active_status: bool | None = None


class ProductRead(ProductBase, Timestamped):
    product_id: UUID


class InventoryRead(ORMModel):
    inventory_id: UUID
    product_id: UUID
    available_quantity: int
    reserved_quantity: int
    reorder_level: int


class InventoryAdjust(ORMModel):
    available_delta: int = 0
    reserved_delta: int = 0
