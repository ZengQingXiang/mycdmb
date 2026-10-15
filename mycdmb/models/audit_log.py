from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, func, Index
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_logs_user', 'user_id'),
        Index('ix_audit_logs_created', 'created_at'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer)
    username: Mapped[str | None] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(128))
    entity_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(16))
    old_values: Mapped[dict | None] = mapped_column(JSON)
    new_values: Mapped[dict | None] = mapped_column(JSON)
    url: Mapped[str | None] = mapped_column(String(1024))
    method: Mapped[str | None] = mapped_column(String(16))
    remote_ip: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
