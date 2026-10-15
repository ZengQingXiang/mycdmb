""AuditLog 查询端点"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..db import get_db
from ..enums import UserRole
from ..models.audit_log import AuditLog
from ..models.user import User

router = APIRouter(prefix='/audit-logs', tags=['audit'])


@router.get('')
def list_audit_logs(
    entity_type: str | None = Query(None),
    action: str | None = Query(None),
    user_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    q = db.query(AuditLog)
    if current.role != UserRole.ADMIN:
        q = q.filter(AuditLog.user_id == current.id)
    elif user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if action:
        q = q.filter(AuditLog.action == action)
    return q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
