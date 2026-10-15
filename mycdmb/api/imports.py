""批量导入：模板下载 + Excel 上传"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..core.auth import require_write
from ..db import get_db
from ..models.user import User
from ..services.import_service import run_import

router = APIRouter(prefix='/import', tags=['import'])


@router.get('/template')
def download_template():
    """下载空白 Excel 模板（openpyxl 生成）"""
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active
    ws.title = 'access_links'
    headers = [
        'customer_name', 'contact_person', 'contact_phone', 'customer_address',
        'business_type', 'device_type', 'vendor', 'model', 'serial_number',
        'mac_address', 'management_ip', 'cpe_location', 'network_type',
        'node_role', 'node_name', 'node_location', 'node_management_ip',
        'media_type', 'fiber_core_count', 'install_date', 'link_remark',
    ]
    ws.append(headers)
    sample = [
        '示例客户', '张经理', '13800000000', '北京市海淀区中关村大街1号',
        '政企专线', '光纤收发器', '华为', 'MA5616', 'SN-000001',
        'AA:BB:CC:DD:EE:01', '10.30.30.1', '用户侧机柜',
        'PTN', 'PTN 节点', '示例-PTN汇聚节点-01', '中关村机房', '10.10.10.1',
        '光纤', 2, '2024-06-01', '示例链路',
    ]
    ws.append(sample)
    from io import BytesIO
    buf = BytesIO(); wb.save(buf)
    buf.seek(0)
    return Response(
        content=buf.read(),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=access_links_template.xlsx'},
    )


@router.post('/access-links')
def import_access_links(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_write),
):
    """上传 Excel 批量导入 AccessLink。

    - 一行 = 一条完整 AccessLink（Customer + CpeDevice + NetworkNode + Link）
    - 每个实体按业务唯一键 upsert
    - 行级事务隔离
    """
    if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xlsm')):
        raise HTTPException(status_code=400, detail='只支持 .xlsx 文件')
    data = file.file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail='文件为空')
    return run_import(db, data)
