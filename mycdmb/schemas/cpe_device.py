""CpeDevice schemas"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from ..enums import CpeDeviceType


class CpeDeviceBase(BaseModel):
    device_type: CpeDeviceType
    vendor: str | None = None
    model: str | None = None
    serial_number: str | None = None
    mac_address: str | None = None
    management_ip: str | None = None
    location: str | None = None
    remark: str | None = None

    @field_validator('device_type', mode='before')
    @classmethod
    def _flex(cls, v):
        if isinstance(v, CpeDeviceType): return v
        return CpeDeviceType.from_any(v)


class CpeDeviceCreate(CpeDeviceBase):
    customer_id: int


class CpeDeviceUpdate(BaseModel):
    device_type: CpeDeviceType | None = None
    vendor: str | None = None
    model: str | None = None
    serial_number: str | None = None
    mac_address: str | None = None
    management_ip: str | None = None
    location: str | None = None
    remark: str | None = None

    @field_validator('device_type', mode='before')
    @classmethod
    def _flex(cls, v):
        if v is None or isinstance(v, CpeDeviceType): return v
        return CpeDeviceType.from_any(v)


class CpeDeviceResponse(CpeDeviceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    created_at: datetime
