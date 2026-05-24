# HID Gateway Platform

# Backend 详细设计文档（V1.1 — 落地 `py_web` 骨架版）

> 改造说明：保留 V1 全部职责与组件，仅把分层、组件、接口落到当前仓库的真实路径（`app/api`、`app/services`、`app/database`、`app/core`），并把 V1 中尚未实现的能力（Redis、JWT、Alembic、WS 端点、Dispatcher / Routing / Macro / AckTracker / Queue 抽象）以「在现仓库新增的具体文件」形式补齐。

---

# 1. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | Backend Gateway Server |
| 技术栈 | FastAPI + SQLAlchemy + MySQL（PyMySQL） + Redis（二期） |
| 通信 | HTTP + WebSocket（JSON / V2 协议） |
| 架构 | 分层架构（API / Application / Domain / Infrastructure） |
| 目标 | 多用户、多设备、可扩展动作调度系统（V1 全部职责保留） |
| 部署根目录 | `f:/webpy/py_web` |
| 启动入口 | `run.py` → uvicorn `app.main:app`，监听 `0.0.0.0:8000` |

---

# 2. Backend 总体职责（V1 保留）

- 用户认证与权限控制（JWT）
- 设备注册与管理
- WebSocket 长连接管理（device + client）
- 动作调度与路由
- 队列管理（memory / redis 双后端）
- 宏执行
- 日志记录（colorlog + 异步钩子 → MySQL）
- 状态同步

---

# 3. 分层架构（落到 `py_web/app/`）

```text
API Layer            ←  app/api/{v1,v2,dev,ws,tcp(预留)}
Application Layer    ←  app/services/{dispatcher, routing, macro_engine, device_registry, queue, ack_tracker, log_bus, ...}
Domain Layer         ←  app/database/{models, schemas}
Infrastructure Layer ←  app/core/{config, logger, security, cache, templates}
                        + app/database/{session, base, base_class, crud, alembic}
```

> 不引入与现仓库冲突的顶层 `domain/`、`infrastructure/` 目录；通过 package 命名 + 边界纪律体现分层。

---

# 3.1 API Layer（接口层）

职责（V1 保留）：HTTP API、WebSocket API、参数校验、Token 鉴权、DTO 转换。禁止业务逻辑与数据库操作。

## 3.1.1 落点

```text
app/api/router.py        # 已聚合 /v1 /v2 /dev
app/api/v1/              # 业务 API（auth/device/macro/action）
app/api/v2/              # 演进 API（V2 envelope）
app/api/dev/             # 调试 API
app/api/ws/              # 【新增】
  device.py              # /ws/device
  client.py              # /ws/client
```

## 3.1.2 HTTP 端点（V1 保留 + 显式版本前缀）

```text
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/users/me

POST /api/v1/devices              # 注册
GET  /api/v1/devices              # 列表
GET  /api/v1/devices/{id}
DELETE /api/v1/devices/{id}

POST /api/v1/macros
GET  /api/v1/macros
PUT  /api/v1/macros/{id}
DELETE /api/v1/macros/{id}

POST /api/v2/action               # 单次动作（V2 envelope）
POST /api/v2/action/batch         # 批量
GET  /api/v2/logs                 # 动作日志查询
```

## 3.1.3 WebSocket 端点

```text
/ws/device   # ESP32 长连接
/ws/client   # 浏览器/脚本实时控制
```

两端统一 V2 envelope；连接时 querystring `?token=...` 鉴权。

---

# 3.2 Application Layer（应用层）

职责（V1 保留）：业务编排、调度、宏执行、路由决策、队列控制。

## 3.2.1 Dispatcher（`app/services/dispatcher.py`，新增）

```text
Client Action
   ↓
Auth Check (依赖注入)
   ↓
Permission Check (CRUD: device.owner_user_id)
   ↓
Routing Resolve (RoutingEngine)
   ↓
QueueBackend.push(device_id, envelope)
   ↓
AckTracker.expect(msg_id)
```

纯 Python 类，I/O 通过依赖注入（QueueBackend、CRUD、AckTracker），便于 pytest。

## 3.2.2 Macro Engine（`app/services/macro_engine.py`，新增）

- 顺序执行 steps
- `delay` 支持
- 可中断（cancel token）
- 步骤级 ACK / 失败回报
- Phase 2：DSL（条件 / 循环 / 变量）

## 3.2.3 Routing Engine（`app/services/routing.py`，新增）

解析 `routing` 字段：

- 单设备 `target_devices=[d1]`
- 多设备 `target_devices=[d1, d2]`
- 广播 `broadcast=true`
- 设备组 `group="office"` → 查 `device_groups` 表展开

优先级：`target_devices` > `group` > `broadcast`（见 V2 协议）。

## 3.2.4 Device Registry（`app/services/device_registry.py`，新增）

- 内存表：`{device_id: WebSocket}`
- 二期：同步写 Redis `device:online` SET，多实例可见
- 心跳超时后台 task：>30s 移除

## 3.2.5 Queue（`app/services/queue/`，新增）

抽象接口：

```python
class QueueBackend(Protocol):
    async def push(self, device_id: str, envelope: dict) -> None: ...
    async def pop(self, device_id: str) -> dict | None: ...
    async def size(self, device_id: str) -> int: ...
```

实现：

- `memory.py`：`asyncio.Queue` per device（一期默认）
- `redis.py`：`LPUSH` / `BRPOP`，key=`queue:device:<id>`（二期）

通过 `.env` `QUEUE_BACKEND=memory|redis` 切换。

## 3.2.6 ACK Tracker（`app/services/ack_tracker.py`，新增）

- 维护 `pending: dict[msg_id, Future]`
- ACK 到达 → resolve；超时 → retry（指数退避，最多 3 次）
- 幂等：缓存最近 N 条 msg_id（二期改 Redis `idem:msg:*` TTL）

## 3.2.7 Log Bus（`app/services/log_bus.py`，已有）

保留：作为日志异步事件总线，桥接 colorlog → MySQL `action_logs` → `/ws/client` 实时推送面板。

---

# 3.3 Domain Layer（领域层）

实体定义在 `app/database/models/`，DTO 在 `app/database/schemas/`。模型纯数据 + 业务方法不依赖框架。

## Entity: User（`models/user.py`）

```python
class User(Base):
    id: int
    username: str
    password_hash: str
    role: Literal["admin", "user"]
    created_at, updated_at
```

## Entity: Device（`models/device.py`）

```python
class Device(Base):
    id: int
    device_uuid: str
    owner_user_id: int | None
    name: str | None
    capabilities: dict
    status: Literal["offline","online","busy","error"]
    last_online_at: datetime
```

## Entity: Action（`schemas/action.py`，纯 DTO）

```python
class ActionPayload(BaseModel):
    type: str          # keyboard_tap / text / mouse_move / macro / ...
    # 各 type 字段（key / content / x / y / steps / delay_ms）
```

## Entity: Macro（`models/macro.py`）

```python
class Macro(Base):
    id: int
    user_id: int
    name: str
    content_json: dict   # {steps: [...]}
```

## Entity: DeviceGroup（保留 V1 设备组能力）

`models/device_group.py` + `device_group_members`。

---

# 3.4 Infrastructure Layer

外部系统集成（V1 全部保留）：

| 组件 | 落点 |
|---|---|
| MySQL | `app/database/session.py`（已用） |
| Redis | `app/core/cache.py`（新增，`redis.asyncio`） |
| WebSocket Server | `app/api/ws/`（新增） |
| Logging | `app/core/logger/`（已用，colorlog + 异步钩子） |
| Queue System | `app/services/queue/`（新增抽象） |
| Migration | `app/database/alembic/`（新增） |
| Container | `deploy/Dockerfile` + `deploy/docker-compose.yml`（新增） |

---

# 4. WebSocket 设计

## 4.1 Device WS（`/ws/device`）

ESP32 入口。生命周期（V1 保留）：

```text
CONNECT → REGISTER → ONLINE → HEARTBEAT → DISCONNECT
```

### 注册消息（V2 envelope）

```json
{
  "header": { "type": "register", "msg_id": "uuid", "device_id": "esp32_001" },
  "payload": { "name": "Desk HID", "capabilities": ["usb_keyboard", "usb_mouse"] }
}
```

### Action 消息（下行）

```json
{
  "header": { "type": "action", "msg_id": "uuid", "seq": 10001, "device_id": "esp32_001" },
  "routing": { "target_devices": ["esp32_001"] },
  "payload": { "type": "keyboard_tap", "key": "KEY_A" }
}
```

### ACK（上行）

```json
{
  "header": { "type": "ack", "msg_id": "uuid_of_ack", "ref_msg_id": "uuid_of_action" },
  "payload": { "status": "ok", "exec_time_ms": 12 }
}
```

## 4.2 Client WS（`/ws/client`）

用于 Vue / 脚本实时控制 + 状态/日志订阅；同样使用 V2 envelope。

---

# 5. Action Dispatch 系统

## 5.1 流程（V1 保留，落点对齐仓库）

```text
Client Request (HTTP /api/v2/action 或 WS /ws/client)
   ↓
API Layer (app/api/v2/action.py | app/api/ws/client.py)
   ↓
Auth (app/core/security.py:get_current_user)
   ↓
Dispatcher (app/services/dispatcher.py)
   ↓
Routing Engine (app/services/routing.py)
   ↓
QueueBackend.push (app/services/queue/*.py)
   ↓
Device WS Sender (app/api/ws/device.py)
   ↓
ESP32
   ↓ ack ← AckTracker → Log Bus → action_logs
```

## 5.2 Action Envelope

以 V2 协议为准（详见专文）。

---

# 6. Routing 系统

## 6.1 规则（V1 保留 + V2 扩展）

- 单设备
- 多设备（V2 新增）
- 设备组（V2 新增 `group`，库表 `device_groups`）
- 广播（V2 新增 `broadcast=true`）
- 用户全部设备（兜底）

## 6.2 路由逻辑（伪代码）

```python
def resolve(envelope, current_user) -> list[str]:
    r = envelope["routing"]
    if r.get("target_devices"):
        targets = r["target_devices"]
    elif r.get("group"):
        targets = crud.device_group.list_member_uuids(r["group"])
    elif r.get("broadcast"):
        targets = crud.device.list_online_uuids(owner=current_user.id)
    else:
        targets = crud.device.list_uuids_by_owner(current_user.id)
    return [d for d in targets if permission_ok(current_user, d)]
```

---

# 7. Queue 系统

## 7.1 一期：内存队列

```python
# app/services/queue/memory.py
_queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

async def push(device_id, env): await _queues[device_id].put(env)
async def pop(device_id):       return await _queues[device_id].get()
```

## 7.2 二期：Redis 队列

```python
# app/services/queue/redis.py
async def push(device_id, env):
    await redis.lpush(f"queue:device:{device_id}", json.dumps(env))

async def pop(device_id):
    _, raw = await redis.brpop(f"queue:device:{device_id}", timeout=0)
    return json.loads(raw)
```

## 7.3 Worker（Sender Coroutine）

每个在线设备的 ws handler 内部启动一个 sender task：

- 监听 `QueueBackend.pop(device_id)`
- 推送 WebSocket
- 提交 AckTracker 等待 ack
- 失败 → retry / 落 `action_logs.status='failed'`

---

# 8. 设备管理系统

## 8.1 Device Registry

```python
# app/services/device_registry.py
live: dict[str, WebSocket] = {}
```

二期：同步 `device:online` 到 Redis；`bus:device:<id>` Pub/Sub 让多实例广播。

## 8.2 状态机（V1 保留）

| 状态 | 描述 |
|---|---|
| offline | 离线 |
| online | 在线 |
| busy | 执行中 |
| error | 异常（V1.1 新增，便于排障） |

---

# 9. 权限系统

## 9.1 规则（V1 保留）

- 用户只能操作自己拥有的设备
- `role='admin'` 可管理全部设备 / 用户
- 设备组：仅组拥有者可下发

## 9.2 校验流程

```text
Request → JWT Decode (security.get_current_user)
        → User Active Check
        → Device / Group Ownership Check (CRUD)
        → Pass / 403
```

## 9.3 实现

```python
# app/core/security.py（新增内容）
def create_access_token(sub: str, role: str, exp_min: int = 60) -> str: ...
def decode_token(token: str) -> TokenPayload: ...

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User: ...

async def ws_authenticate(websocket: WebSocket) -> User:
    """从 query 或首帧拿 token，鉴权失败 close(4401)"""
```

---

# 10. MySQL 设计补充

## 10.1 索引

```sql
CREATE INDEX idx_device_owner ON devices(owner_user_id);
CREATE INDEX idx_action_device ON action_logs(device_id);
CREATE INDEX idx_action_user   ON action_logs(user_id);
CREATE UNIQUE INDEX uk_action_msg ON action_logs(msg_id);
```

## 10.2 日志写入策略（V1 保留）

- 异步写入（`log_bus` 投递）
- 一期：直接 `INSERT`
- 二期：Redis buffer + 定时批量 flush

## 10.3 迁移

- baseline：现 `vehicle_management.sql`
- Alembic：`alembic init app/database/alembic`，首版生成 users / devices / device_connections / action_logs / macros / device_groups / device_group_members

---

# 11. 日志系统设计（V1 保留）

## 11.1 日志类型

| 类型 | 说明 |
|---|---|
| system | 系统运行 |
| action | 输入动作 |
| device | 设备状态 |
| security | 登录权限 |
| protocol | WS 通信 |

## 11.2 Action Log 写入

```json
{
  "msg_id": "uuid",
  "user_id": 1,
  "device_id": "esp32_001",
  "action_type": "keyboard_tap",
  "payload_json": { "key": "KEY_A" },
  "status": "acked",
  "exec_time_ms": 12
}
```

## 11.3 实现位置

- 控制台彩色：`app/core/logger/log_config.py`（colorlog）
- 文件滚动：`logs/`
- 业务异步钩子：`app/core/logger/log_callbacks/` → `crud.action_log.create`
- 实时面板：通过 `log_bus` 推送 `/ws/client` 订阅 channel `logs`

---

# 12. 错误处理系统（V1 保留）

## 12.1 Error Code（合并 V1 + V2）

| code | 含义 |
|---|---|
| 1000 | unknown error |
| 2001 | auth failed |
| 2002 | device offline |
| 2003 | unauthorized |
| 3001 | invalid action |
| 3002 | parse error |
| 3003 | queue full |
| 4001 | retry exhausted |

## 12.2 HTTP 错误返回

```json
{ "error": { "code": 2002, "message": "device offline" } }
```

## 12.3 WS 错误帧（V2 协议）

```json
{ "header": { "type": "error", "ref_msg_id": "..." }, "payload": { "code": "E002", "message": "..." } }
```

---

# 13. 性能设计（V1 保留）

## 13.1 并发模型

- FastAPI async
- WebSocket async（每连接独立 sender task）
- 一期：进程内 asyncio.Queue
- 二期：Redis Queue + Pub/Sub 跨实例

## 13.2 性能目标

| 项目 | 目标 |
|---|---|
| LAN action 端到端 | < 50ms |
| ACK 回传 | < 50ms |
| 重试恢复 | < 200ms |
| 并发设备 | 100+（一期）/ 1000+（二期 Redis） |
| 并发客户端 | 1000+ |

---

# 14. 可测试性设计（V1 保留）

## 14.1 单元测试覆盖

- Dispatcher
- Routing Engine
- Macro Engine
- AckTracker（含 retry / 幂等）
- QueueBackend（memory / redis 两套）

## 14.2 Mock

- Mock device websocket（`asyncio.Queue` 模拟）
- Mock redis（fakeredis-aioredis）
- Mock database（SQLite in-memory）

落点：`tests/unit/`、`tests/api/`。

---

# 15. 扩展性设计（V1 保留）

预留落点：

- BLE device router → ESP32 固件 `components/ble/`
- MQTT bridge → `app/api/mqtt/`（订阅/发布桥）
- Plugin system → `app/services/plugin/`（动作类型 + 协议适配热加载）
- Script engine → `app/services/script_runner.py`（已有，扩展 Lua / Python sandbox）
- Multi-region server → Redis Pub/Sub + 网关层粘连

---

# 16. MVP Backend 范围（V1 保留）

- 用户登录（JWT）
- 设备注册
- WS device connection（`/ws/device`）
- Action dispatch（HTTP + WS）
- Queue（memory）
- MySQL log（action_logs）
- ACK 机制

---

# 17. 后续演进方向（V1 保留）

## Phase 2

- BLE HID routing
- Device group
- Macro DSL（条件 / 循环）
- Redis Queue + 多实例
- Alembic 持续迁移
- Docker / Nginx 部署

## Phase 3

- Plugin system
- Cloud sync
- AI automation（生成宏 / 异常分析）
- MQTT bridge
- OTA

---

# 18. 总结

> 构建一个可扩展、高解耦、多设备、多用户的 HID 控制中枢。

核心原则（V1 保留）：分层架构、事件驱动、队列解耦、强权限控制、可测试性优先。本版仅把所有原 V1 能力**清晰落到 `py_web/app/` 现有骨架**中，不删减任何功能。
