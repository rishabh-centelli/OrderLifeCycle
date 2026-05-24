from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.company import Company
from app.models.customer import Customer
from app.repositories.base import BaseRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Customer, db)

    async def create(self, payload: CustomerCreate) -> Customer:
        if not await self.db.get(Company, payload.company_id):
            raise NotFoundError("Company not found")
        result = await self.db.execute(select(Customer).where(Customer.email == payload.email))
        if result.scalar_one_or_none():
            raise ConflictError("Customer email already exists")
        customer = await self.repo.create(payload.model_dump())
        await self.db.commit()
        return customer

    async def get(self, customer_id: UUID) -> Customer:
        customer = await self.repo.get("customer_id", customer_id)
        if not customer:
            raise NotFoundError("Customer not found")
        return customer

    async def update(self, customer_id: UUID, payload: CustomerUpdate) -> Customer:
        customer = await self.get(customer_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer
