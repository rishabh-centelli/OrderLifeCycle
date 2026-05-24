from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.company import Company
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent))])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)):
    return await CompanyService(db).create(payload)


@router.get("", response_model=Page[CompanyRead])
async def list_companies(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(Company, db).list(
        params.page, params.size, params.search, ["company_name", "company_email"], params.sort_by, params.sort_order
    )
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: UUID, db: AsyncSession = Depends(get_db)):
    return await CompanyService(db).get(company_id)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(company_id: UUID, payload: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    return await CompanyService(db).update(company_id, payload)
