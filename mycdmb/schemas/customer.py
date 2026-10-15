""Customer schemas"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from ..enums import BusinessType


class CustomerBase(BaseModel):
    name: str
    contact_person: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    business_type: BusinessType = BusinessType.OTHER
    remark: str | None = None

    @field_validator('business_type', mode='before')
    @classmethod
    def _flex(cls, v):
        if v is None or isinstance(v, BusinessType): return v
        return BusinessType.from_any(v)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    business_type: BusinessType | None = None
    remark: str | None = None

    @field_validator('business_type', mode='before')
    @classmethod
    def _flex(cls, v):
        if v is None or isinstance(v, BusinessType): return v
        return BusinessType.from_any(v)


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
