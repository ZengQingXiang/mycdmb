""审计事件监听器：SQLAlchemy before_flush → AuditLog"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import event
from sqlalchemy.orm import Session, attributes

from ..db import Base
from ..models.audit_log import AuditLog

AUDIT_EXCLUDED_TABLES = {'audit_logs', 'users'}


def _is_auditable(obj) -> bool:
    return isinstance(obj, Base) and obj.__tablename__ not in AUDIT_EXCLUDED_TABLES


def _json_safe(val):
    if val is None:
        return None
    if isinstance(val, Enum):
        val = val.value
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, (list, tuple)):
        return [_json_safe(v) for v in val]
    if isinstance(val, dict):
        return {k: _json_safe(v) for k, v in val.items()}
    return str(val)


def _entity_pk_str(obj) -> str:
    pks = [c.name for c in obj.__table__.primary_key.columns]
    values = [str(getattr(obj, k)) for k in pks]
    return ','.join(values) if len(values) > 1 else values[0]


def _serialize(obj) -> dict | None:
    try:
        data = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if val is None:
                continue
            data[col.name] = _json_safe(val)
        return data
    except Exception:
        return None


def setup_audit(db: Session, user, request) -> None:
    """把审计上下文写入 session.info，供 before_flush 读取。"""
    db.info['audit_user_id'] = getattr(user, 'id', None)
    db.info['audit_username'] = getattr(user, 'username', None)
    db.info['audit_url'] = getattr(request, 'url', None)
    db.info['audit_method'] = getattr(request, 'method', None)


def _before_flush(session: Session, flush_context, instances) -> None:
    if session.info.get('_audit_running'):
        return
    if not session.info.get('audit_user_id'):
        return
    user_id = session.info['audit_user_id']
    username = session.info.get('audit_username')
    url = session.info.get('audit_url')
    method = session.info.get('audit_method')

    session.info['_audit_running'] = True
    try:
        for obj in list(session.new):
            if not _is_auditable(obj):
                continue
            try:
                session.add(AuditLog(
                    user_id=user_id, username=username,
                    entity_type=obj.__tablename__, entity_id=_entity_pk_str(obj),
                    action='INSERT', old_values=None, new_values=_serialize(obj),
                    url=url, method=method,
                ))
            except Exception:
                pass

        for obj in list(session.dirty):
            if not _is_auditable(obj):
                continue
            changes = {}
            for attr in attributes.instance_state(obj).attrs:
                history = attr.history
                if history.has_changes():
                    old = history.deleted[0] if history.deleted else None
                    new = history.added[0] if history.added else None
                    if old != new:
                        changes[attr.key] = {'old': old, 'new': new}
            if not changes:
                continue
            try:
                session.add(AuditLog(
                    user_id=user_id, username=username,
                    entity_type=obj.__tablename__, entity_id=_entity_pk_str(obj),
                    action='UPDATE',
                    old_values={k: _json_safe(v['old']) for k, v in changes.items()},
                    new_values={k: _json_safe(v['new']) for k, v in changes.items()},
                    url=url, method=method,
                ))
            except Exception:
                pass

        for obj in list(session.deleted):
            if not _is_auditable(obj):
                continue
            try:
                session.add(AuditLog(
                    user_id=user_id, username=username,
                    entity_type=obj.__tablename__, entity_id=_entity_pk_str(obj),
                    action='DELETE', old_values=_serialize(obj), new_values=None,
                    url=url, method=method,
                ))
            except Exception:
                pass
    finally:
        session.info.pop('_audit_running', None)


def register_audit_listener() -> None:
    event.listen(Session, 'before_flush', _before_flush)
