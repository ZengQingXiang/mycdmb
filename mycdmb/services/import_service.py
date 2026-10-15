""Excel 导入服务：openpyxl 解析 + 4 层 upsert + 行级事务"""
from __future__ import annotations

from datetime import datetime, date
from io import BytesIO

from openpyxl import load_workbook
from sqlalchemy.orm import Session

from ..models.access_link import AccessLink
from ..models.customer import Customer
from ..models.cpe_device import CpeDevice
from ..models.network_node import NetworkNode


HEADERS = [
    'customer_name', 'contact_person', 'contact_phone', 'customer_address',
    'business_type', 'device_type', 'vendor', 'model', 'serial_number',
    'mac_address', 'management_ip', 'cpe_location', 'network_type',
    'node_role', 'node_name', 'node_location', 'node_management_ip',
    'media_type', 'fiber_core_count', 'install_date', 'link_remark',
]


def _parse_date(val) -> date | None:
    if val is None or val == '':
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'):
            try:
                return datetime.strptime(val.strip(), fmt).date()
            except ValueError:
                continue
    return None


def _to_enum(value, cls):
    if value is None or value == '':
        return cls.OTHER if hasattr(cls, 'OTHER') else None
    if isinstance(value, cls):
        return value
    return cls.from_any(str(value).strip())


def _upsert_customer(db: Session, row: dict) -> Customer:
    name = str(row['customer_name']).strip()
    business_type = _to_enum(row.get('business_type'), __import__('mycdmb.enums', fromlist=['BusinessType']).BusinessType)
    existing = db.query(Customer).filter(
        Customer.name == name,
        Customer.business_type == business_type.value,
    ).first()
    if existing:
        existing.contact_person = row.get('contact_person')
        existing.contact_phone = row.get('contact_phone')
        existing.address = row.get('customer_address')
        return existing
    new = Customer(
        name=name,
        business_type=business_type.value,
        contact_person=row.get('contact_person'),
        contact_phone=row.get('contact_phone'),
        address=row.get('customer_address'),
    )
    db.add(new); db.flush()
    return new


def _upsert_network_node(db: Session, row: dict) -> NetworkNode:
    nt = _to_enum(row.get('network_type'), __import__('mycdmb.enums', fromlist=['NetworkType']).NetworkType)
    nr = _to_enum(row.get('node_role'), __import__('mycdmb.enums', fromlist=['NetworkNodeRole']).NetworkNodeRole)
    node_name = str(row['node_name']).strip()
    existing = db.query(NetworkNode).filter(
        NetworkNode.network_type == nt.value,
        NetworkNode.node_name == node_name,
    ).first()
    if existing:
        if existing.network_type != nt.value:
            raise ValueError(f'节点名 {node_name} 已存在但 network_type 不匹配')
        existing.node_role = nr.value
        existing.location = row.get('node_location')
        existing.management_ip = row.get('node_management_ip')
        return existing
    new = NetworkNode(
        network_type=nt.value, node_role=nr.value, node_name=node_name,
        location=row.get('node_location'), management_ip=row.get('node_management_ip'),
    )
    db.add(new); db.flush()
    return new


def _upsert_cpe_device(db: Session, row: dict, customer_id: int) -> CpeDevice:
    serial = row.get('serial_number')
    mac = row.get('mac_address')
    device_type = _to_enum(row.get('device_type'), __import__('mycdmb.enums', fromlist=['CpeDeviceType']).CpeDeviceType)
    existing = None
    if serial or mac:
        q = db.query(CpeDevice)
        if serial: q = q.filter(CpeDevice.serial_number == str(serial).strip())
        if mac: q = q.filter(CpeDevice.mac_address == str(mac).strip())
        existing = q.first()
    if existing:
        existing.device_type = device_type.value
        existing.vendor = row.get('vendor')
        existing.model = row.get('model')
        existing.management_ip = row.get('management_ip')
        existing.location = row.get('cpe_location')
        return existing
    new = CpeDevice(
        customer_id=customer_id,
        device_type=device_type.value,
        vendor=row.get('vendor'),
        model=row.get('model'),
        serial_number=str(serial).strip() if serial else None,
        mac_address=str(mac).strip() if mac else None,
        management_ip=row.get('management_ip'),
        location=row.get('cpe_location'),
    )
    db.add(new); db.flush()
    return new


def run_import(db: Session, xlsx_data: bytes) -> dict:
    """解析 Excel，逐行 upsert，返回 JSON report。"""
    from ..enums import BusinessType, NetworkType, NetworkNodeRole, CpeDeviceType, MediaType

    wb = load_workbook(filename=BytesIO(xlsx_data), read_only=True, data_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    header = list(next(rows_iter))
    idx = {h.strip(): i for i, h in enumerate(header)}

    total = success = skipped = failed = 0
    errors: list[dict] = []

    for row_num, values in enumerate(rows_iter, start=2):
        if not any(v not in (None, '') for v in values):
            continue
        total += 1
        row_dict = {h: values[idx.get(h, i)] for i, h in enumerate(header) if h in idx}
        local = db.begin_nested()
        try:
            customer = _upsert_customer(db, row_dict)
            node = _upsert_network_node(db, row_dict)
            device = _upsert_cpe_device(db, row_dict, customer.id)
            link = AccessLink(
                customer_id=customer.id,
                cpe_device_id=device.id,
                network_node_id=node.id,
                network_type=_to_enum(row_dict.get('network_type'), NetworkType).value,
                media_type=_to_enum(row_dict.get('media_type'), MediaType).value,
                fiber_core_count=row_dict.get('fiber_core_count'),
                install_date=_parse_date(row_dict.get('install_date')),
                remark=row_dict.get('link_remark'),
            )
            db.add(link); db.flush()
            local.commit(); success += 1
        except Exception as e:
            local.rollback(); failed += 1
            errors.append({'row': row_num, 'reason': str(e)})

    db.commit()
    return {'total': total, 'success': success, 'skipped': skipped, 'failed': failed, 'errors': errors}
