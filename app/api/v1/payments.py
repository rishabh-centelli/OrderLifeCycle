from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import UserRole
from app.repositories.idempotency import get_idempotent_response, save_idempotent_response
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(require_roles(UserRole.admin, UserRole.agent))])


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    endpoint = "POST /payments"
    if idempotency_key:
        existing = await get_idempotent_response(db, idempotency_key, endpoint)
        if existing:
            return existing
    payment = await PaymentService(db).create(payload)
    response = PaymentRead.model_validate(payment).model_dump(mode="json")
    if idempotency_key:
        await save_idempotent_response(db, idempotency_key, endpoint, response)
        await db.commit()
    return response
