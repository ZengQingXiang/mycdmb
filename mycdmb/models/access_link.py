from datetime import datetime, date
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class AccessLink(Base):
    __tablename__ = 'access_links'
    __table_args__ = (
        UniqueConstraint('customer_id', 'cpe_device_id', 'network_node_id', 'network_type', name='uq_access_links_cpe_node_net'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    cpe_device_id: Mapped[int] = mapped_column(ForeignKey('cpe_devices.id'))
    network_node_id: Mapped[int] = mapped_column(ForeignKey('network_nodes.id'))
    network_type: Mapped[str] = mapped_column(String(32))
    media_type: Mapped[str] = mapped_column(String(32), default='FIBER')
    fiber_core_count: Mapped[int | None] = mapped_column()
    install_date: Mapped[date | None] = mapped_column(Date)
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    customer: Mapped['Customer'] = relationship()
    cpe_device: Mapped['CpeDevice'] = relationship()
    network_node: Mapped['NetworkNode'] = relationship()
