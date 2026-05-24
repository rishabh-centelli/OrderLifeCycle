from typing import Annotated

from fastapi import Query

from app.schemas.common import PaginationParams


async def pagination_params(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 25,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$")] = "asc",
) -> PaginationParams:
    return PaginationParams(page=page, size=size, search=search, sort_by=sort_by, sort_order=sort_order)
