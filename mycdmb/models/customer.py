from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    contact_person: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(64))
    address: Mapped[str | None] = mapped_column(String(500))
    business_type: Mapped[str] = mapped_column(String(32), default='OTHER')
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    cpe_devices: Mapped[list['CpeDevice']] = relationship(back_populates='customer')
