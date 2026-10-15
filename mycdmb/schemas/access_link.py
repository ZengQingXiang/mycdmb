""AccessLink schemas"""
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, field_validator
from ..enums import NetworkType, MediaType
from .customer import CustomerResponse
from .cpe_device import CpeDeviceResponse
from .network_node import NetworkNodeResponse


class AccessLinkBase(BaseModel):
    network_type: NetworkType
    media_type: MediaType = MediaType.FIBER
    fiber_core_count: int | None = None
    install_date: date | None = None
    remark: str | None = None

    @field_validator('network_type', mode='before')
    @classmethod
    def _flex_nt(cls, v):
        if isinstance(v, NetworkType): return v
        return NetworkType.from_any(v)

    @field_validator('media_type', mode='before')
    @classmethod
    def _flex_mt(cls, v):
        if isinstance(v, MediaType): return v
        return MediaType.from_any(v)


class AccessLinkCreate(AccessLinkBase):
    customer_id: int
    cpe_device_id: int
    network_node_id: int


class AccessLinkUpdate(BaseModel):
    network_type: NetworkType | None = None
    media_type: MediaType | None = None
    fiber_core_count: int | None = None
    install_date: date | None = None
    remark: str | None = None
    cpe_device_id: int | None = None
    network_node_id: int | None = None

    @field_validator('network_type', mode='before')
    @classmethod
    def _flex_nt(cls, v):
        if v is None or isinstance(v, NetworkType): return v
        return NetworkType.from_any(v)

    @field_validator('media_type', mode='before')
    @classmethod
    def _flex_mt(cls, v):
        if v is None or isinstance(v, MediaType): return v
        return MediaType.from_any(v)


class AccessLinkResponse(AccessLinkBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    cpe_device_id: int
    network_node_id: int
    created_at: datetime


class AccessLinkDetail(AccessLinkResponse):
    customer: CustomerResponse
    cpe_device: CpeDeviceResponse
    network_node: NetworkNodeResponse
