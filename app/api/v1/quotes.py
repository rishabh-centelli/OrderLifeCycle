from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.quote import Quote
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.quote import QuoteCreate, QuoteRead, QuoteUpdate
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["quotes"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent, UserRole.user))])


@router.post("", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
async def create_quote(payload: QuoteCreate, db: AsyncSession = Depends(get_db)):
    return await QuoteService(db).create(payload)


@router.get("", response_model=Page[QuoteRead])
async def list_quotes(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(Quote, db).list(params.page, params.size, None, None, params.sort_by, params.sort_order)
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.get("/{quote_id}", response_model=QuoteRead)
async def get_quote(quote_id: UUID, db: AsyncSession = Depends(get_db)):
    return await QuoteService(db).get(quote_id)


@router.patch("/{quote_id}", response_model=QuoteRead)
async def update_quote(quote_id: UUID, payload: QuoteUpdate, db: AsyncSession = Depends(get_db)):
    return await QuoteService(db).update(quote_id, payload)


@router.post("/{quote_id}/approve", response_model=QuoteRead)
async def approve_quote(quote_id: UUID, db: AsyncSession = Depends(get_db)):
    return await QuoteService(db).approve(quote_id)
