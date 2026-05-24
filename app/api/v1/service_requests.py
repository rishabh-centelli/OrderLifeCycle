from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import pagination_params
from app.core.database import get_db
from app.core.security import require_roles
from app.models.service_request import ServiceRequest
from app.models.user import UserRole
from app.repositories.base import BaseRepository
from app.schemas.common import Page, PaginationParams
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestRead, ServiceRequestUpdate
from app.services.service_request_service import ServiceRequestService

router = APIRouter(prefix="/service-requests", tags=["service requests"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent, UserRole.user))])


@router.post("", response_model=ServiceRequestRead, status_code=status.HTTP_201_CREATED)
async def create_service_request(payload: ServiceRequestCreate, db: AsyncSession = Depends(get_db)):
    return await ServiceRequestService(db).create(payload)


@router.get("", response_model=Page[ServiceRequestRead])
async def list_service_requests(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    items, total = await BaseRepository(ServiceRequest, db).list(params.page, params.size, None, None, params.sort_by, params.sort_order)
    return Page(items=items, total=total, page=params.page, size=params.size)


@router.get("/{request_id}", response_model=ServiceRequestRead)
async def get_service_request(request_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ServiceRequestService(db).get(request_id)


@router.patch("/{request_id}", response_model=ServiceRequestRead)
async def update_service_request(request_id: UUID, payload: ServiceRequestUpdate, db: AsyncSession = Depends(get_db)):
    return await ServiceRequestService(db).update(request_id, payload)
