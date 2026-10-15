""AccessLink CRUD + 三大核心查询场景"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from ..core.auth import require_write
from ..db import get_db
from ..models.access_link import AccessLink
from ..models.user import User
from ..schemas.access_link import AccessLinkCreate, AccessLinkUpdate, AccessLinkResponse, AccessLinkDetail

router = APIRouter(prefix='/access-links', tags=['access_links'])


@router.get('', response_model=list[AccessLinkDetail])
def list_links(
    customer_id: int | None = Query(None),
    cpe_device_id: int | None = Query(None),
    network_node_id: int | None = Query(None),
    network_type: str | None = Query(None),
    management_ip: str | None = Query(None),
    mac_address: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(AccessLink).options(
        selectinload(AccessLink.customer), selectinload(AccessLink.cpe_device), selectinload(AccessLink.network_node)
    )
    if customer_id: q = q.filter(AccessLink.customer_id == customer_id)
    if cpe_device_id: q = q.filter(AccessLink.cpe_device_id == cpe_device_id)
    if network_node_id: q = q.filter(AccessLink.network_node_id == network_node_id)
    if network_type: q = q.filter(AccessLink.network_type == network_type)
    if management_ip:
        from ..models.cpe_device import CpeDevice
        q = q.join(CpeDevice, CpeDevice.id == AccessLink.cpe_device_id).filter(CpeDevice.management_ip == management_ip)
    if mac_address:
        from ..models.cpe_device import CpeDevice
        q = q.join(CpeDevice, CpeDevice.id == AccessLink.cpe_device_id).filter(CpeDevice.mac_address == mac_address)
    return q.order_by(AccessLink.id.desc()).offset(offset).limit(limit).all()


@router.get('/{link_id}', response_model=AccessLinkDetail)
def get_link(link_id: int, db: Session = Depends(get_db)):
    link = db.query(AccessLink).options(
        selectinload(AccessLink.customer), selectinload(AccessLink.cpe_device), selectinload(AccessLink.network_node)
    ).get(link_id)
    if not link:
        raise HTTPException(status_code=404, detail='AccessLink not found')
    return link


@router.post('', response_model=AccessLinkResponse, status_code=201)
def create_access_link(
    payload: AccessLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    link = AccessLink(**payload.model_dump())
    db.add(link); db.commit(); db.refresh(link)
    return link


@router.patch('/{link_id}', response_model=AccessLinkResponse)
def update_access_link(
    link_id: int,
    payload: AccessLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    link = db.get(AccessLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail='AccessLink not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(link, k, v)
    db.commit(); db.refresh(link)
    return link


@router.delete('/{link_id}', status_code=204)
def delete_access_link(
    link_id: int,
    db: Session = Depends(get_db), current_user: User = Depends(require_write),
):
    link = db.get(AccessLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail='AccessLink not found')
    db.delete(link); db.commit()
