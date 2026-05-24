from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.delivery import Delivery
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.delivery import DeliveryCreate, DeliveryRead, DeliveryRetry, DeliveryUpdate
from app.services.delivery_service import DeliveryService

router = APIRouter(prefix="/deliveries", tags=["deliveries"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent))])


@router.post("", response_model=DeliveryRead, status_code=status.HTTP_201_CREATED)
async def create_delivery(payload: DeliveryCreate, db: AsyncSession = Depends(get_db)):
    return await DeliveryService(db).create(payload)


@router.get("", response_model=Page[DeliveryRead])
async def list_deliveries(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(Delivery, db).list(params.page, params.size, params.search, ["tracking_number", "courier_name"], params.sort_by, params.sort_order)
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.patch("/{delivery_id}", response_model=DeliveryRead)
async def update_delivery(delivery_id: UUID, payload: DeliveryUpdate, db: AsyncSession = Depends(get_db)):
    return await DeliveryService(db).update(delivery_id, payload)


@router.post("/{delivery_id}/retry", response_model=DeliveryRead)
async def retry_delivery(delivery_id: UUID, payload: DeliveryRetry, db: AsyncSession = Depends(get_db)):
    return await DeliveryService(db).retry(delivery_id, payload)
