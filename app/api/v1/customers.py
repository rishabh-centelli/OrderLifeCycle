from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.customer import Customer
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent, UserRole.user))])


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(payload: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await CustomerService(db).create(payload)


@router.get("", response_model=Page[CustomerRead])
async def list_customers(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(Customer, db).list(
        params.page, params.size, params.search, ["customer_name", "email"], params.sort_by, params.sort_order
    )
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: UUID, db: AsyncSession = Depends(get_db)):
    return await CustomerService(db).get(customer_id)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(customer_id: UUID, payload: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    return await CustomerService(db).update(customer_id, payload)
