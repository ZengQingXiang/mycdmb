""全链路冒烟测试：RBAC 三角色 + 审计 + UI + /me + 模板"""
import time, sys, httpx

BASE = 'http://127.0.0.1:8000'
PASS = FAIL = 0
CHECKS = []

def check(name, cond, detail=''):
    global PASS, FAIL
    if cond: PASS += 1; CHECKS.append(('PASS', name, detail))
    else: FAIL += 1; CHECKS.append(('FAIL', name, detail))

def login(u, p):
    r = httpx.post(f'{BASE}/api/auth/login', data={'username': u, 'password': p}, timeout=5)
    return r.json().get('access_token') if r.status_code == 200 else None

def h(tok): return {'Authorization': f'Bearer {tok}'}

print('=' * 60); print('MyCDMB 全链路冒烟测试'); print('=' * 60)

r = httpx.get(f'{BASE}/health', timeout=5); check('health', r.status_code == 200)
admin_tok = login('admin', 'admin123'); check('bootstrap admin', admin_tok is not None)

# 注册 operator / viewer
r = httpx.post(f'{BASE}/api/auth/register', json={'username': 'op1', 'password': 'op123', 'role': 'OPERATOR'}, headers=h(admin_tok))
check('admin register operator', r.status_code == 201)
r = httpx.post(f'{BASE}/api/auth/register', json={'username': 'vw1', 'password': 'vw123', 'role': 'VIEWER'}, headers=h(admin_tok))
check('admin register viewer', r.status_code == 201)
op_tok, vw_tok = login('op1', 'op123'), login('vw1', 'vw123')
check('login op1/vw1', op_tok and vw_tok)

# RBAC 矩阵
r = httpx.post(f'{BASE}/api/customers', headers=h(vw_tok), json={'name': 'A', 'business_type': '政企专线'}); check('viewer 403', r.status_code == 403)
r = httpx.post(f'{BASE}/api/auth/register', headers=h(op_tok), json={'username': 'x', 'password': 'x', 'role': 'VIEWER'}); check('op register 403', r.status_code == 403)
r = httpx.post(f'{BASE}/api/customers', headers=h(op_tok), json={'name': '企业甲', 'business_type': '政企专线'}); check('op POST 201', r.status_code == 201)
r = httpx.post(f'{BASE}/api/customers', headers=h(admin_tok), json={'name': '家庭乙', 'business_type': '家庭宽带'}); check('admin POST 201', r.status_code == 201)
r = httpx.get(f'{BASE}/api/customers'); check('public GET', r.status_code == 200)

# 审计
import sqlite3; time.sleep(0.3)
r = httpx.get(f'{BASE}/api/audit-logs?limit=10', headers=h(admin_tok)); check('audit endpoint', r.status_code == 200)
logs = r.json(); check('有 INSERT', any(l['entity_type'] == 'customers' and l['action'] == 'INSERT' for l in logs))
print(f'  审计日志: {len(logs)} 条')
r = httpx.get(f'{BASE}/api/audit-logs?limit=50', headers=h(op_tok)); op_logs = r.json()
check('op 只看自己的', all(l['username'] == 'op1' for l in op_logs))

# UI
r = httpx.get(f'{BASE}/'); check('GET /', r.status_code == 200 and 'MyCDMB' in r.text[:500])
r = httpx.get(f'{BASE}/ui/login.html'); check('login.html', r.status_code == 200 and '登录' in r.text)
r = httpx.get(f'{BASE}/ui/index.html'); check('index.html', r.status_code == 200)
r = httpx.get(f'{BASE}/api/customers'); check('/api 不被吃', r.status_code == 200)

# 模板 + /me
r = httpx.get(f'{BASE}/api/import/template'); check('template', r.status_code == 200)
r = httpx.get(f'{BASE}/api/auth/me', headers=h(admin_tok)); check('/me admin', r.status_code == 200 and r.json()['role'] == 'ADMIN')
r = httpx.get(f'{BASE}/api/auth/me', headers=h(vw_tok)); check('/me viewer', r.status_code == 200 and r.json()['role'] == 'VIEWER')
r = httpx.get(f'{BASE}/api/auth/me'); check('/me no token 401', r.status_code == 401)

print(f'\n结果: {PASS} PASS / {FAIL} FAIL ({PASS+FAIL} 项)')
if FAIL:
    [print(f'  ❌ {n} — {d}') for s, n, d in CHECKS if s == 'FAIL']
    sys.exit(1)
print('✅ 全链路通过')
