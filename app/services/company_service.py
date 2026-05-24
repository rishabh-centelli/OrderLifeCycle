from uuid import UUID

from fastapi import status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.company import Company
from app.repositories.base import BaseRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Company, db)

    async def create(self, payload: CompanyCreate) -> Company:
        existing = await self.db.execute(
            select(Company).where(
                or_(Company.company_email == payload.company_email, Company.gst_number == payload.gst_number)
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Company email or GST number already exists")
        company = await self.repo.create(payload.model_dump())
        await self.db.commit()
        return company

    async def get(self, company_id: UUID) -> Company:
        company = await self.repo.get("company_id", company_id)
        if not company:
            raise NotFoundError("Company not found")
        return company

    async def update(self, company_id: UUID, payload: CompanyUpdate) -> Company:
        company = await self.get(company_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(company, key, value)
        await self.db.commit()
        await self.db.refresh(company)
        return company
