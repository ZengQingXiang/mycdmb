# MyCDMB 领域模型

## 核心实体

| 实体 | 职责 | 唯一键 |
|------|------|--------|
| Customer | 业务客户（企业 / 家庭 / 其他） | name + business_type |
| CpeDevice | 客户侧 CPE 设备（收发器 / ONU / 交换机 / 路由器 / 裸纤端点） | serial_number + mac_address |
| NetworkNode | 承载网节点（IP 城域网 / MSTP / PTN / SDH / 裸纤） | network_type + node_name |
| AccessLink | 接入链路（客户—CPE—承载网节点 的四元组） | customer_id + cpe_device_id + network_node_id + network_type |
| NodeConnection | 承载网节点互联（有向双向边） | src_node_id + dst_node_id |
| User | 系统用户（ADMIN / OPERATOR / VIEWER） | username |
| AuditLog | 自动审计日志 | — |

## 核心查询场景

1. **用户端故障反向查询** — 给定 management_ip / mac_address / serial_number 反查完整链路
2. **承载网故障影响面** — 给定 network_node_id 或 network_type 查下联客户
3. **承载网节点下联统计** — 给定 network_node_id 直接返回 count
4. **历史安装资料批量补录** — Excel 上传，4 层 upsert + 行级事务隔离
