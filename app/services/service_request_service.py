from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.order import Order, OrderStatus
from app.models.service_request import ServiceRequest, ServiceRequestStatus
from app.repositories.base import BaseRepository
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestUpdate


class ServiceRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(ServiceRequest, db)

    async def create(self, payload: ServiceRequestCreate) -> ServiceRequest:
        order = await self.db.get(Order, payload.order_id)
        if not order:
            raise NotFoundError("Order not found")
        if order.customer_id != payload.customer_id:
            raise BusinessRuleError("Service request customer does not match order")
        if order.order_status != OrderStatus.delivered:
            raise BusinessRuleError("Only delivered orders can raise service requests")

        order_product_ids = {str(item["product_id"]) for item in order.items}
        requested_product_ids = {str(item.product_id) for item in payload.items}
        if not requested_product_ids.issubset(order_product_ids):
            raise BusinessRuleError("Requested product must exist in original order")

        open_requests = await self.db.execute(
            select(ServiceRequest).where(
                ServiceRequest.order_id == payload.order_id,
                ServiceRequest.status.in_([ServiceRequestStatus.open, ServiceRequestStatus.in_progress]),
            )
        )
        for request in open_requests.scalars().all():
            existing_products = {str(item["product_id"]) for item in request.items}
            if existing_products.intersection(requested_product_ids):
                raise BusinessRuleError("Duplicate open request exists for one or more products")

        service_request = await self.repo.create(
            {**payload.model_dump(mode="json"), "status": ServiceRequestStatus.open}
        )
        await self.db.commit()
        return service_request

    async def get(self, request_id: UUID) -> ServiceRequest:
        request = await self.repo.get("request_id", request_id)
        if not request:
            raise NotFoundError("Service request not found")
        return request

    async def update(self, request_id: UUID, payload: ServiceRequestUpdate) -> ServiceRequest:
        request = await self.get(request_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(request, key, value)
        await self.db.commit()
        await self.db.refresh(request)
        return request
