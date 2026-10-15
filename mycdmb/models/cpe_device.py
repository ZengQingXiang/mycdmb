from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class CpeDevice(Base):
    __tablename__ = 'cpe_devices'
    __table_args__ = (
        UniqueConstraint('serial_number', 'mac_address', name='uq_cpe_serial_mac'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    device_type: Mapped[str] = mapped_column(String(32))
    vendor: Mapped[str | None] = mapped_column(String(128))
    model: Mapped[str | None] = mapped_column(String(128))
    serial_number: Mapped[str | None] = mapped_column(String(255))
    mac_address: Mapped[str | None] = mapped_column(String(64))
    management_ip: Mapped[str | None] = mapped_column(String(64))
    location: Mapped[str | None] = mapped_column(String(500))
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    customer: Mapped['Customer'] = relationship(back_populates='cpe_devices')
