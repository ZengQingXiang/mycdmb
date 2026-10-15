""Customer CRUD"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.auth import require_write
from ..db import get_db
from ..models.customer import Customer
from ..models.user import User
from ..schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix='/customers', tags=['customers'])


@router.get('', response_model=list[CustomerResponse])
def list_customers(
    q: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)
    if q:
        query = query.filter(
            Customer.name.ilike(f'%{q}%') | Customer.contact_phone.ilike(f'%{q}%')
        )
    return query.order_by(Customer.id.desc()).offset(offset).limit(limit).all()


@router.get('/{customer_id}', response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail='Customer not found')
    return c


@router.post('', response_model=CustomerResponse, status_code=201)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    c = Customer(**payload.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c


@router.patch('/{customer_id}', response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail='Customer not found')
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c


@router.delete('/{customer_id}', status_code=204)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db), current_user: User = Depends(require_write),
):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail='Customer not found')
    db.delete(c); db.commit()
