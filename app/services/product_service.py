from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.inventory import Inventory
from app.models.product import Product
from app.repositories.base import BaseRepository
from app.schemas.product import InventoryAdjust, ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Product, db)

    async def create(self, payload: ProductCreate) -> Product:
        data = payload.model_dump(exclude={"initial_quantity", "reorder_level"})
        product = await self.repo.create(data)
        self.db.add(
            Inventory(
                product_id=product.product_id,
                available_quantity=payload.initial_quantity,
                reserved_quantity=0,
                reorder_level=payload.reorder_level,
            )
        )
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get(self, product_id: UUID) -> Product:
        product = await self.repo.get("product_id", product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    async def update(self, product_id: UUID, payload: ProductUpdate) -> Product:
        product = await self.get(product_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def adjust_inventory(self, product_id: UUID, payload: InventoryAdjust) -> Inventory:
        result = await self.db.execute(select(Inventory).where(Inventory.product_id == product_id).with_for_update())
        inventory = result.scalar_one_or_none()
        if not inventory:
            raise NotFoundError("Inventory not found")
        if inventory.available_quantity + payload.available_delta < 0:
            raise BusinessRuleError("Available inventory cannot become negative")
        if inventory.reserved_quantity + payload.reserved_delta < 0:
            raise BusinessRuleError("Reserved inventory cannot become negative")
        inventory.available_quantity += payload.available_delta
        inventory.reserved_quantity += payload.reserved_delta
        await self.db.commit()
        await self.db.refresh(inventory)
        return inventory
