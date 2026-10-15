""NetworkNode CRUD + 下联统计 + 拓扑"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.auth import require_write
from ..db import get_db
from ..enums import NetworkType
from ..models.access_link import AccessLink
from ..models.network_node import NetworkNode
from ..models.user import User
from ..schemas.network_node import NetworkNodeCreate, NetworkNodeUpdate, NetworkNodeResponse

router = APIRouter(prefix='/network-nodes', tags=['network_nodes'])


@router.get('', response_model=list[NetworkNodeResponse])
def list_nodes(
    network_type: str | None = Query(None),
    q: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    qr = db.query(NetworkNode)
    if network_type: qr = qr.filter(NetworkNode.network_type == network_type)
    if q: qr = qr.filter(NetworkNode.node_name.ilike(f'%{q}%'))
    return qr.order_by(NetworkNode.id.desc()).offset(offset).limit(limit).all()


@router.get('/{node_id}', response_model=NetworkNodeResponse)
def get_node(node_id: int, db: Session = Depends(get_db)):
    n = db.get(NetworkNode, node_id)
    if not n:
        raise HTTPException(status_code=404, detail='NetworkNode not found')
    return n


@router.get('/{node_id}/downstream-count')
def downstream_count(node_id: int, db: Session = Depends(get_db)):
    n = db.get(NetworkNode, node_id)
    if not n:
        raise HTTPException(status_code=404, detail='NetworkNode not found')
    count = db.query(func.count(AccessLink.id)).filter(AccessLink.network_node_id == node_id).scalar() or 0
    return {'node_id': node_id, 'downstream_links': count}


@router.post('', response_model=NetworkNodeResponse, status_code=201)
def create_node(
    payload: NetworkNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    n = NetworkNode(**payload.model_dump())
    db.add(n); db.commit(); db.refresh(n)
    return n


@router.patch('/{node_id}', response_model=NetworkNodeResponse)
def update_node(
    node_id: int,
    payload: NetworkNodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    n = db.get(NetworkNode, node_id)
    if not n:
        raise HTTPException(status_code=404, detail='NetworkNode not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(n, k, v)
    db.commit(); db.refresh(n)
    return n


@router.delete('/{node_id}', status_code=204)
def delete_node(
    node_id: int,
    db: Session = Depends(get_db), current_user: User = Depends(require_write),
):
    n = db.get(NetworkNode, node_id)
    if not n:
        raise HTTPException(status_code=404, detail='NetworkNode not found')
    db.delete(n); db.commit()
