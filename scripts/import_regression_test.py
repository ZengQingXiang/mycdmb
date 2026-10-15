""Excel 批量导入回归测试（4 场景）"""
import io, sys, uuid, httpx
import openpyxl
from openpyxl import Workbook

BASE = 'http://127.0.0.1:8000'
TAG = uuid.uuid4().hex[:6]
HEADERS = [
    'customer_name', 'contact_person', 'contact_phone', 'customer_address',
    'business_type', 'device_type', 'vendor', 'model', 'serial_number',
    'mac_address', 'management_ip', 'cpe_location', 'network_type',
    'node_role', 'node_name', 'node_location', 'node_management_ip',
    'media_type', 'fiber_core_count', 'install_date', 'link_remark',
]
PASS = FAIL = 0; CHECKS = []

def check(n, c, d=''):
    global PASS, FAIL
    if c: PASS += 1; CHECKS.append(('PASS', n, d))
    else: FAIL += 1; CHECKS.append(('FAIL', n, d))

def login(u, p):
    r = httpx.post(f'{BASE}/api/auth/login', data={'username': u, 'password': p}, timeout=5)
    return r.json().get('access_token') if r.status_code == 200 else None

def h(tok): return {'Authorization': f'Bearer {tok}'}

def make_xlsx(rows):
    wb = Workbook(); ws = wb.active; ws.append(HEADERS)
    for r in rows: ws.append([r.get(c) for c in HEADERS])
    buf = io.BytesIO(); wb.save(buf); return buf.getvalue()

def tagged(rows):
    out = []
    for r in rows:
        r = dict(r)
        for k in ('customer_name', 'node_name', 'serial_number'):
            if r.get(k): r[k] = f"{r[k]}#{TAG}"
        out.append(r)
    return out

def upload(tok, content, fname='t.xlsx'):
    return httpx.post(f'{BASE}/api/import/access-links',
        headers=h(tok), files={'file': (fname, content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        timeout=30)

print('=' * 60); print('Excel 批量导入回归测试'); print('=' * 60)
admin_tok = login('admin', 'admin123'); check('admin', admin_tok is not None)

# 场景 1：单行中文 label
row1 = {
    'customer_name': '回归测试-政企客户甲', 'contact_person': '李', 'contact_phone': '1111',
    'customer_address': '北京海淀', 'business_type': '政企专线',
    'device_type': '光纤收发器', 'vendor': '华为', 'model': 'MA5616',
    'serial_number': 'SN-REG-0001', 'mac_address': 'AA:BB:CC:00:00:01',
    'management_ip': '10.30.30.11', 'network_type': 'PTN', 'node_role': 'PTN 节点',
    'node_name': '回归测试-PTN汇聚节点-01', 'node_location': '中关村机房', 'node_management_ip': '10.10.10.11',
    'media_type': '光纤', 'fiber_core_count': 2, 'install_date': '2024-06-01',
}
r = upload(admin_tok, make_xlsx(tagged([row1])))
check('HTTP 200', r.status_code == 200, f'{r.status_code}')
b = r.json() if r.status_code == 200 else r.text
if isinstance(b, dict):
    check('t=1', b.get('total') == 1); check('s=1', b.get('success') == 1); check('f=0', b.get('failed') == 0)

# 场景 2：批量中英文混填
rows2 = [
    {'customer_name': '回归测试-政企客户乙', 'business_type': 'ENTERPRISE',
     'device_type': 'ONU', 'vendor': '中兴', 'serial_number': 'SN-REG-0002',
     'management_ip': '10.30.30.12', 'network_type': 'PTN', 'node_role': 'PTN_NODE',
     'node_name': '回归测试-PTN汇聚节点-02', 'media_type': 'FIBER', 'install_date': '2024-07-15'},
    {'customer_name': '回归测试-家庭客户丙', 'business_type': '家庭宽带',
     'device_type': 'ONU', 'vendor': '华为', 'serial_number': 'SN-REG-0003',
     'management_ip': '10.30.30.13', 'network_type': 'MSTP', 'node_role': 'MSTP 节点',
     'node_name': '回归测试-MSTP节点-01', 'media_type': '超五类网线', 'install_date': '2024-08-01'},
    {'customer_name': '回归测试-家庭客户丙', 'business_type': '家庭宽带',
     'device_type': '交换机', 'vendor': '华为', 'serial_number': 'SN-REG-0004',
     'network_type': 'MSTP', 'node_role': 'MSTP 节点',
     'node_name': '回归测试-MSTP节点-01', 'media_type': '六类网线', 'install_date': '2024-08-02'},
]
rows2_t = tagged(rows2)
r = upload(admin_tok, make_xlsx(rows2_t)); check('batch HTTP 200', r.status_code == 200)
b = r.json(); check('batch t=3', b['total'] == 3); check('batch s=3', b['success'] == 3); check('batch f=0', b['failed'] == 0)

# 场景 3：幂等
r = upload(admin_tok, make_xlsx(rows2_t)); b = r.json()
check('idempotent s=0', b.get('success') == 0); check('skipped=3', b.get('skipped') == 3)

# 场景 4：错误隔离
rows4 = [
    {'customer_name': '隔离A', 'business_type': '政企专线', 'device_type': '路由器',
     'serial_number': 'SN-ISO-A', 'management_ip': '10.30.30.14',
     'network_type': 'PTN', 'node_role': 'PTN 节点', 'node_name': '隔离节点X',
     'media_type': '光纤', 'install_date': '2024-09-01'},
    {'customer_name': '隔离B', 'business_type': '政企专线', 'device_type': '路由器',
     'serial_number': 'SN-ISO-B', 'management_ip': '10.30.30.15',
     'network_type': 'MSTP', 'node_role': 'MSTP 节点', 'node_name': '隔离节点X',
     'media_type': '光纤', 'install_date': '2024-09-02'},  # 同 node 但 network_type 冲突
    {'customer_name': '隔离C', 'business_type': '政企专线', 'device_type': '不存在的类型',
     'network_type': 'PTN', 'node_role': 'PTN 节点', 'node_name': '隔离节点Y'},
    {'customer_name': '隔离D', 'business_type': '家庭宽带', 'device_type': 'ONU',
     'serial_number': 'SN-ISO-D', 'management_ip': '10.30.30.16',
     'network_type': 'PTN', 'node_role': 'PTN 节点', 'node_name': '隔离节点Z',
     'media_type': '光纤', 'install_date': '2024-09-03'},
]
r = upload(admin_tok, make_xlsx(tagged(rows4))); b = r.json()
check('iso t=4', b['total'] == 4); check('iso s=2', b['success'] == 2); check('iso f=2', b['failed'] == 2)
errs = b.get('errors', []); check('err 有 row', all('row' in e for e in errs))

print(f'\n结果: {PASS} PASS / {FAIL} FAIL ({PASS+FAIL} 项)')
if FAIL:
    [print(f'  ❌ {n} — {d}') for s, n, d in CHECKS if s == 'FAIL']
    sys.exit(1)
print('✅ Excel 回归通过')
