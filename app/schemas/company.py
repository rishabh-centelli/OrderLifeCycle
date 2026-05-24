import re
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.models.company import CompanyType
from app.schemas.common import PhoneMixin, Timestamped


class CompanyBase(PhoneMixin):
    company_name: str = Field(min_length=1, max_length=255)
    company_email: EmailStr
    gst_number: str | None = Field(default=None, max_length=15)
    phone_no: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=1000)
    type: CompanyType

    @field_validator("gst_number")
    @classmethod
    def validate_gst(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.upper().strip()
        if not re.fullmatch(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$", normalized):
            raise ValueError("Invalid GST number")
        return normalized


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(PhoneMixin):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    company_email: EmailStr | None = None
    gst_number: str | None = Field(default=None, max_length=15)
    phone_no: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=1000)
    type: CompanyType | None = None


class CompanyRead(CompanyBase, Timestamped):
    company_id: UUID
