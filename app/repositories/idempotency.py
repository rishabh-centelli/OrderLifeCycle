from uuid import UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, uuid_pk


class IdempotencyRecord(Base, TimestampMixin):
    __tablename__ = "idempotency_record"
    __table_args__ = (UniqueConstraint("key", "endpoint", name="uq_idempotency_key_endpoint"),)

    idempotency_id: Mapped[UUID] = uuid_pk()
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    response: Mapped[dict] = mapped_column(JSONB, nullable=False)


async def get_idempotent_response(db, key: str, endpoint: str) -> dict | None:
    from sqlalchemy import select

    result = await db.execute(
        select(IdempotencyRecord).where(IdempotencyRecord.key == key, IdempotencyRecord.endpoint == endpoint)
    )
    record = result.scalar_one_or_none()
    return record.response if record else None


async def save_idempotent_response(db, key: str, endpoint: str, response: dict) -> None:
    db.add(IdempotencyRecord(key=key, endpoint=endpoint, response=response))
    await db.flush()
