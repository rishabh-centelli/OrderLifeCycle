from typing import Any, Generic, TypeVar

from sqlalchemy import Select, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id_field: str, value: Any) -> ModelT | None:
        result = await self.db.execute(select(self.model).where(getattr(self.model, id_field) == value))
        return result.scalar_one_or_none()

    async def create(self, data: dict[str, Any]) -> ModelT:
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def list(
        self,
        page: int = 1,
        size: int = 25,
        search: str | None = None,
        search_fields: list[str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        statement: Select | None = None,
    ) -> tuple[list[ModelT], int]:
        stmt = statement or select(self.model)
        if search and search_fields:
            conditions = [getattr(self.model, field).ilike(f"%{search}%") for field in search_fields]
            stmt = stmt.where(or_(*conditions))

        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        if sort_by and hasattr(self.model, sort_by):
            sort_col = getattr(self.model, sort_by)
            stmt = stmt.order_by(desc(sort_col) if sort_order == "desc" else asc(sort_col))

        result = await self.db.execute(stmt.offset((page - 1) * size).limit(size))
        return list(result.scalars().unique().all()), total
