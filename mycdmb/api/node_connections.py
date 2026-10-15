""NodeConnection CRUD + 拓扑查询"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from ..core.auth import require_write
from ..db import get_db
from ..models.network_node import NetworkNode
from ..models.node_connection import NodeConnection
from ..models.user import User
from ..schemas.node_connection import NodeConnectionCreate, NodeConnectionUpdate, NodeConnectionResponse

router = APIRouter(prefix='/node-connections', tags=['node_connections'])


@router.get('', response_model=list[NodeConnectionResponse])
def list_connections(
    src_node_id: int | None = Query(None),
    dst_node_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(NodeConnection).options(
        selectinload(NodeConnection.src_node), selectinload(NodeConnection.dst_node)
    )
    if src_node_id: q = q.filter(NodeConnection.src_node_id == src_node_id)
    if dst_node_id: q = q.filter(NodeConnection.dst_node_id == dst_node_id)
    return q.offset(offset).limit(limit).all()


@router.get('/topology/{node_id}')
def topology(node_id: int, db: Session = Depends(get_db)):
    center = db.get(NetworkNode, node_id)
    if not center:
        raise HTTPException(status_code=404, detail='NetworkNode not found')
    parent = db.get(NetworkNode, center.parent_node_id) if center.parent_node_id else None
    upstream = db.query(NodeConnection).filter(
        NodeConnection.dst_node_id == node_id
    ).options(selectinload(NodeConnection.src_node), selectinload(NodeConnection.dst_node)).all()
    downstream = db.query(NodeConnection).filter(
        NodeConnection.src_node_id == node_id
    ).options(selectinload(NodeConnection.src_node), selectinload(NodeConnection.dst_node)).all()
    return {
        'center': {'id': center.id, 'name': center.node_name, 'type': center.network_type},
        'parent': {'id': parent.id, 'name': parent.node_name} if parent else None,
        'upstream': [
            {
                'id': c.id, 'media_type': c.media_type, 'bandwidth': c.bandwidth,
                'src': {'id': c.src_node.id, 'name': c.src_node.node_name},
                'dst': {'id': c.dst_node.id, 'name': c.dst_node.node_name},
            } for c in upstream
        ],
        'downstream': [
            {
                'id': c.id, 'media_type': c.media_type, 'bandwidth': c.bandwidth,
                'src': {'id': c.src_node.id, 'name': c.src_node.node_name},
                'dst': {'id': c.dst_node.id, 'name': c.dst_node.node_name},
            } for c in downstream
        ],
    }


@router.post('', response_model=NodeConnectionResponse, status_code=201)
def create_connection(
    payload: NodeConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    c = NodeConnection(**payload.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c


@router.patch('/{conn_id}', response_model=NodeConnectionResponse)
def update_connection(
    conn_id: int,
    payload: NodeConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    c = db.get(NodeConnection, conn_id)
    if not c:
        raise HTTPException(status_code=404, detail='NodeConnection not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c


@router.delete('/{conn_id}', status_code=204)
def delete_connection(
    conn_id: int,
    db: Session = Depends(get_db), current_user: User = Depends(require_write),
):
    c = db.get(NodeConnection, conn_id)
    if not c:
        raise HTTPException(status_code=404, detail='NodeConnection not found')
    db.delete(c); db.commit()
