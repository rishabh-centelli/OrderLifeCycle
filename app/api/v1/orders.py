from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.order import Order
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.order import OrderCancel, OrderCreate, OrderRead, OrderUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent, UserRole.user))])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await OrderService(db).create(payload)


@router.get("", response_model=Page[OrderRead])
async def list_orders(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(Order, db).list(params.page, params.size, None, None, params.sort_by, params.sort_order)
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db)):
    return await OrderService(db).get(order_id)


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(order_id: UUID, payload: OrderUpdate, db: AsyncSession = Depends(get_db)):
    return await OrderService(db).update(order_id, payload)


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(order_id: UUID, _: OrderCancel | None = None, db: AsyncSession = Depends(get_db)):
    return await OrderService(db).cancel(order_id)
