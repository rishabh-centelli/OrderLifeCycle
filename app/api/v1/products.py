from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.product import Product
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.product import InventoryAdjust, InventoryRead, ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent))])


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await ProductService(db).create(payload)


@router.get("", response_model=Page[ProductRead])
async def list_products(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(Product, db).list(
        params.page, params.size, params.search, ["product_name", "category"], params.sort_by, params.sort_order
    )
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ProductService(db).get(product_id)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: UUID, payload: ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await ProductService(db).update(product_id, payload)


@router.post("/{product_id}/inventory/adjust", response_model=InventoryRead)
async def adjust_inventory(product_id: UUID, payload: InventoryAdjust, db: AsyncSession = Depends(get_db)):
    return await ProductService(db).adjust_inventory(product_id, payload)
