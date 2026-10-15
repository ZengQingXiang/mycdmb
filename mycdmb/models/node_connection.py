from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class NodeConnection(Base):
    __tablename__ = 'node_connections'
    __table_args__ = (
        UniqueConstraint('src_node_id', 'dst_node_id', name='uq_node_connections_src_dst'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    src_node_id: Mapped[int] = mapped_column(ForeignKey('network_nodes.id'))
    dst_node_id: Mapped[int] = mapped_column(ForeignKey('network_nodes.id'))
    media_type: Mapped[str | None] = mapped_column(String(32))
    bandwidth: Mapped[str | None] = mapped_column(String(64))
    distance_km: Mapped[float | None] = mapped_column(Float)
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    src_node: Mapped['NetworkNode'] = relationship(foreign_keys=[src_node_id])
    dst_node: Mapped['NetworkNode'] = relationship(foreign_keys=[dst_node_id])
