from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class NetworkNode(Base):
    __tablename__ = 'network_nodes'
    __table_args__ = (
        UniqueConstraint('network_type', 'node_name', name='uq_network_nodes_type_name'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    network_type: Mapped[str] = mapped_column(String(32))
    node_role: Mapped[str] = mapped_column(String(32))
    node_name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(500))
    management_ip: Mapped[str | None] = mapped_column(String(64))
    remark: Mapped[str | None] = mapped_column(Text)
    parent_node_id: Mapped[int | None] = mapped_column(ForeignKey('network_nodes.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    parent: Mapped['NetworkNode | None'] = relationship(remote_side=[id], backref='children')
