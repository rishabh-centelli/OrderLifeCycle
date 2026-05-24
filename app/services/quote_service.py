from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.customer import Customer
from app.models.quote import Quote, QuoteStatus
from app.repositories.base import BaseRepository
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.services.common import build_priced_items, validate_inventory_available


class QuoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Quote, db)

    async def create(self, payload: QuoteCreate) -> Quote:
        if not await self.db.get(Customer, payload.customer_id):
            raise NotFoundError("Customer not found")
        items, total = await build_priced_items(self.db, payload.items)
        await validate_inventory_available(self.db, items)
        quote = await self.repo.create({**payload.model_dump(exclude={"items"}), "items": items, "total_amount": total})
        await self.db.commit()
        return quote

    async def get(self, quote_id: UUID) -> Quote:
        quote = await self.repo.get("quote_id", quote_id)
        if not quote:
            raise NotFoundError("Quote not found")
        return quote

    async def update(self, quote_id: UUID, payload: QuoteUpdate) -> Quote:
        quote = await self.get(quote_id)
        if quote.status in {QuoteStatus.approved, QuoteStatus.rejected, QuoteStatus.expired} and payload.items:
            raise BusinessRuleError("Finalized quotes cannot change items")
        data = payload.model_dump(exclude_unset=True)
        if payload.items is not None:
            items, total = await build_priced_items(self.db, payload.items)
            await validate_inventory_available(self.db, items)
            data["items"] = items
            data["total_amount"] = total
        for key, value in data.items():
            setattr(quote, key, value)
        await self.db.commit()
        await self.db.refresh(quote)
        return quote

    async def approve(self, quote_id: UUID) -> Quote:
        quote = await self.get(quote_id)
        if quote.valid_till < date.today():
            quote.status = QuoteStatus.expired
            await self.db.commit()
            raise BusinessRuleError("Quote has expired")
        quote.status = QuoteStatus.approved
        await self.db.commit()
        await self.db.refresh(quote)
        return quote
