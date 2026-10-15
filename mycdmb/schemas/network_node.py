""NetworkNode schemas"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from ..enums import NetworkType, NetworkNodeRole


class NetworkNodeBase(BaseModel):
    network_type: NetworkType
    node_role: NetworkNodeRole
    node_name: str
    location: str | None = None
    management_ip: str | None = None
    remark: str | None = None
    parent_node_id: int | None = None

    @field_validator('network_type', mode='before')
    @classmethod
    def _flex_nt(cls, v):
        if isinstance(v, NetworkType): return v
        return NetworkType.from_any(v)

    @field_validator('node_role', mode='before')
    @classmethod
    def _flex_nr(cls, v):
        if isinstance(v, NetworkNodeRole): return v
        return NetworkNodeRole.from_any(v)


class NetworkNodeCreate(NetworkNodeBase): pass


class NetworkNodeUpdate(BaseModel):
    network_type: NetworkType | None = None
    node_role: NetworkNodeRole | None = None
    node_name: str | None = None
    location: str | None = None
    management_ip: str | None = None
    remark: str | None = None
    parent_node_id: int | None = None

    @field_validator('network_type', mode='before')
    @classmethod
    def _flex_nt(cls, v):
        if v is None or isinstance(v, NetworkType): return v
        return NetworkType.from_any(v)

    @field_validator('node_role', mode='before')
    @classmethod
    def _flex_nr(cls, v):
        if v is None or isinstance(v, NetworkNodeRole): return v
        return NetworkNodeRole.from_any(v)


class NetworkNodeResponse(NetworkNodeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
