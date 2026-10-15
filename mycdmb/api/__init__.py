""API routes"""
from fastapi import APIRouter

from . import auth, customers, cpe_devices, network_nodes, access_links, node_connections, imports, audit_logs

api_router = APIRouter()
for mod in [auth, customers, cpe_devices, network_nodes, access_links, node_connections, imports, audit_logs]:
    api_router.include_router(mod.router)
