""CpeDevice CRUD + 反向查询"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.auth import require_write
from ..db import get_db
from ..models.cpe_device import CpeDevice
from ..models.user import User
from ..schemas.cpe_device import CpeDeviceCreate, CpeDeviceUpdate, CpeDeviceResponse

router = APIRouter(prefix='/cpe-devices', tags=['cpe_devices'])


@router.get('', response_model=list[CpeDeviceResponse])
def list_devices(
    management_ip: str | None = Query(None),
    mac_address: str | None = Query(None),
    serial_number: str | None = Query(None),
    customer_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(CpeDevice)
    if management_ip: q = q.filter(CpeDevice.management_ip == management_ip)
    if mac_address: q = q.filter(CpeDevice.mac_address == mac_address)
    if serial_number: q = q.filter(CpeDevice.serial_number == serial_number)
    if customer_id: q = q.filter(CpeDevice.customer_id == customer_id)
    return q.order_by(CpeDevice.id.desc()).offset(offset).limit(limit).all()


@router.get('/{device_id}', response_model=CpeDeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    d = db.get(CpeDevice, device_id)
    if not d:
        raise HTTPException(status_code=404, detail='CpeDevice not found')
    return d


@router.post('', response_model=CpeDeviceResponse, status_code=201)
def create_device(
    payload: CpeDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    d = CpeDevice(**payload.model_dump())
    db.add(d); db.commit(); db.refresh(d)
    return d


@router.patch('/{device_id}', response_model=CpeDeviceResponse)
def update_device(
    device_id: int,
    payload: CpeDeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    d = db.get(CpeDevice, device_id)
    if not d:
        raise HTTPException(status_code=404, detail='CpeDevice not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    db.commit(); db.refresh(d)
    return d


@router.delete('/{device_id}', status_code=204)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db), current_user: User = Depends(require_write),
):
    d = db.get(CpeDevice, device_id)
    if not d:
        raise HTTPException(status_code=404, detail='CpeDevice not found')
    db.delete(d); db.commit()
