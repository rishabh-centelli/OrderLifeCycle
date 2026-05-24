from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import PhoneMixin, Timestamped


class CustomerBase(PhoneMixin):
    company_id: UUID
    customer_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone_no: str | None = Field(default=None, max_length=30)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(PhoneMixin):
    company_id: UUID | None = None
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone_no: str | None = Field(default=None, max_length=30)


class CustomerRead(CustomerBase, Timestamped):
    customer_id: UUID
