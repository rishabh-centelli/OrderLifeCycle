from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.common import QuoteOrderItem


def decimal_money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


async def build_priced_items(db: AsyncSession, requested_items: list[QuoteOrderItem]) -> tuple[list[dict], Decimal]:
    items: list[dict] = []
    total = Decimal("0.00")
    seen: set[UUID] = set()
    for index, item in enumerate(requested_items, start=1):
        if item.product_id in seen:
            raise BusinessRuleError("Duplicate product in items is not allowed")
        seen.add(item.product_id)

        product = await db.get(Product, item.product_id)
        if not product or not product.active_status:
            raise NotFoundError(f"Product {item.product_id} not found or inactive")

        unit_price = decimal_money(item.unit_price if item.unit_price is not None else product.selling_price)
        line_total = decimal_money((unit_price * item.quantity) - item.discount_amount + item.tax_amount)
        if line_total < 0:
            raise BusinessRuleError("Item total cannot be negative")

        payload = item.model_dump(mode="json")
        payload.update(
            {
                "item_id": item.item_id or index,
                "product_name": item.product_name or product.product_name,
                "description": item.description or product.description,
                "unit_price": str(unit_price),
                "total_amount": str(line_total),
            }
        )
        items.append(payload)
        total += line_total
    return items, decimal_money(total)


async def validate_inventory_available(db: AsyncSession, items: list[dict]) -> None:
    for item in items:
        result = await db.execute(select(Inventory).where(Inventory.product_id == UUID(str(item["product_id"]))).with_for_update())
        inventory = result.scalar_one_or_none()
        if inventory is None:
            raise BusinessRuleError(f"Inventory not configured for product {item['product_id']}")
        if inventory.available_quantity < int(item["quantity"]):
            raise BusinessRuleError(f"Insufficient stock for product {item['product_id']}")


async def reserve_inventory(db: AsyncSession, items: list[dict]) -> None:
    await validate_inventory_available(db, items)
    for item in items:
        result = await db.execute(select(Inventory).where(Inventory.product_id == UUID(str(item["product_id"]))).with_for_update())
        inventory = result.scalar_one()
        qty = int(item["quantity"])
        inventory.available_quantity -= qty
        inventory.reserved_quantity += qty


async def release_inventory(db: AsyncSession, items: list[dict]) -> None:
    for item in items:
        result = await db.execute(select(Inventory).where(Inventory.product_id == UUID(str(item["product_id"]))).with_for_update())
        inventory = result.scalar_one_or_none()
        if inventory:
            qty = int(item["quantity"])
            inventory.available_quantity += qty
            inventory.reserved_quantity = max(0, inventory.reserved_quantity - qty)
