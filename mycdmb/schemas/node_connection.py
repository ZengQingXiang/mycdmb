""NodeConnection schemas"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NodeConnectionBase(BaseModel):
    src_node_id: int
    dst_node_id: int
    media_type: str | None = None
    bandwidth: str | None = None
    distance_km: float | None = None
    remark: str | None = None


class NodeConnectionCreate(NodeConnectionBase): pass


class NodeConnectionUpdate(BaseModel):
    src_node_id: int | None = None
    dst_node_id: int | None = None
    media_type: str | None = None
    bandwidth: str | None = None
    distance_km: float | None = None
    remark: str | None = None


class NodeConnectionResponse(NodeConnectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
