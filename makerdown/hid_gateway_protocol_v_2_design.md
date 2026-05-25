# HID Gateway Platform

# 通信协议设计 V2.1（工业级稳定版 — 落地 `py_web` 骨架）

> 改造说明：协议本身（envelope / type / ack / retry / sequence / routing / idempotency / 错误体系）**全部保留**。本版补充每条规则在 `py_web` 仓库中的具体落点（FastAPI 路由 / Pydantic schema / 服务模块），并将原文中依赖 Redis 的能力（幂等、Pub/Sub、广播）拆为「一期 in-memory + 二期 Redis」双实现，确保 MVP 可立刻在仓库内跑起来。

---

# 1. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | Communication Protocol |
| 版本 | V2.1 |
| 基础传输 | WebSocket（FastAPI `WebSocket`） |
| 数据格式 | JSON（可扩展 MsgPack） |
| 服务端落点 | `app/api/ws/{device,client}.py` + `app/api/v2/` |
| Schema 校验 | `app/database/schemas/ws_message.py`（Pydantic） |
| 目标 | 多设备可靠调度 + 可追踪 + 可重试（V1 全部目标保留） |

---

# 2. 设计目标（V1 全部保留）

V2 协议目标是解决 V1 的问题：

- ❌ 消息不可追踪 → ✅ `header.msg_id` + `seq` + colorlog 链路
- ❌ 无序执行风险 → ✅ 用户级 `seq` 单调递增 + 设备端可选严格模式
- ❌ 无重试机制 → ✅ 服务端 `AckTracker` + 指数退避
- ❌ 无幂等控制 → ✅ msg_id 去重（一期内存 LRU / 二期 Redis SET）
- ❌ 多设备广播混乱 → ✅ `routing.target_devices / group / broadcast`
- ❌ 无执行确认机制 → ✅ 强制 ACK 帧

---

# 3. 协议核心设计思想

```text
Envelope + Event + ACK + Sequence + Routing
=  统一信封 + 事件驱动 + 可确认 + 可排序 + 可路由
```

服务端实现位置：

| 思想 | 落点 |
|---|---|
| Envelope | `app/database/schemas/ws_message.py` |
| Event 分发 | `app/services/dispatcher.py` |
| ACK | `app/services/ack_tracker.py` |
| Sequence | `app/services/seq_tracker.py` |
| Routing | `app/services/routing.py` |

---

# 4. 协议基础结构（Envelope）

所有消息统一结构：

```json
{
  "header": {
    "msg_id": "uuid",
    "seq": 10001,
    "timestamp": 1710000000,
    "source": "client/web",
    "user_id": "u123",
    "device_id": "d001",
    "type": "action",
    "priority": 1
  },
  "routing": {
    "target_devices": ["d001"],
    "broadcast": false,
    "group": null
  },
  "payload": {}
}
```

## 4.1 服务端 Pydantic 定义

```python
# app/database/schemas/ws_message.py
from pydantic import BaseModel
from typing import Literal

class WsHeader(BaseModel):
    msg_id: str
    seq: int = 0
    timestamp: int
    source: str = "web"
    user_id: str | None = None
    device_id: str | None = None
    type: Literal["register","heartbeat","action","ack","error","status","sync"]
    priority: int = 0
    ref_msg_id: str | None = None     # 仅 ack/error 使用

class WsRouting(BaseModel):
    target_devices: list[str] = []
    broadcast: bool = False
    group: str | None = None

class WsEnvelope(BaseModel):
    header: WsHeader
    routing: WsRouting = WsRouting()
    payload: dict = {}
```

---

# 5. 核心字段说明

## 5.1 header

| 字段 | 说明 | 来源 |
|---|---|---|
| msg_id | 全局唯一 ID | `uuid4()` |
| seq | 用户会话序列号（防乱序） | 客户端单调 +1 |
| timestamp | Unix 秒 | 客户端 |
| source | 来源 | `web` / `bot` / `api` |
| user_id | 用户 ID | JWT 解析自动注入 |
| device_id | 默认目标设备 | — |
| type | 消息类型 | 见 §6 |
| priority | 优先级 0-9 | 默认 0 |
| ref_msg_id | 引用 ID | ack / error 必填 |

## 5.2 routing

支持 4 种模式：

### 单设备
```json
{ "target_devices": ["d001"] }
```

### 多设备
```json
{ "target_devices": ["d001", "d002"] }
```

### 广播
```json
{ "broadcast": true }
```

### 设备组
```json
{ "group": "office_devices" }
```

服务端解析在 `app/services/routing.py:RoutingEngine.resolve()`。

---

# 6. Message Type 定义

| type | 描述 | 服务端处理位置 |
|---|---|---|
| register | 设备注册 | `app/api/ws/device.py` |
| heartbeat | 心跳 | `app/api/ws/device.py` + `device_registry.py` |
| action | 输入动作 | `app/services/dispatcher.py` |
| ack | 确认执行 | `app/services/ack_tracker.py` |
| error | 错误 | `app/core/error_handler.py` |
| status | 状态更新 | `app/services/device_registry.py` |
| sync | 状态全量同步 | `app/services/device_registry.py` |

---

# 7. Action Payload V2（V1 全部类型保留）

## 7.1 键盘
```json
{ "type": "keyboard_tap", "key": "KEY_A" }
```

## 7.2 文本输入
```json
{ "type": "text", "content": "Hello", "interval_ms": 10 }
```

## 7.3 鼠标
```json
{ "type": "mouse_move", "x": 100, "y": -50 }
```

## 7.4 宏
```json
{ "type": "macro", "steps": [] }
```

宏由 `app/services/macro_engine.py` 顺序执行，支持 delay / 中断 / 步骤级 ACK。

## 7.5 其他保留类型

`keyboard_down` / `keyboard_up` / `mouse_click` / `delay` —— 与 V1 一致。

---

# 8. ACK 机制（核心新增）

## 8.1 ACK 结构

```json
{
  "header": {
    "msg_id": "uuid",
    "ref_msg_id": "original_msg",
    "type": "ack"
  },
  "payload": {
    "status": "ok",
    "exec_time_ms": 12
  }
}
```

`status` 取值：`ok` / `failed` / `partial`。

## 8.2 ACK 规则

- 每个 action 必须 ack
- 超时触发 retry
- 最多重试 3 次

## 8.3 服务端实现

```python
# app/services/ack_tracker.py
pending: dict[str, asyncio.Future] = {}

async def expect(msg_id: str, timeout: float = 1.0) -> dict:
    fut = asyncio.get_event_loop().create_future()
    pending[msg_id] = fut
    try:
        return await asyncio.wait_for(fut, timeout)
    finally:
        pending.pop(msg_id, None)

def resolve(ref_msg_id: str, ack_payload: dict) -> None:
    fut = pending.get(ref_msg_id)
    if fut and not fut.done(): fut.set_result(ack_payload)
```

---

# 9. Retry 机制

## 9.1 策略
```text
retry_count: 3
backoff: exponential
```

## 9.2 示例
| 次数 | 延迟 |
|---|---|
| 1 | 100ms |
| 2 | 300ms |
| 3 | 900ms |

## 9.3 实现

```python
# app/services/dispatcher.py（伪代码）
async def deliver(env):
    for delay_ms in [100, 300, 900]:
        await queue.push(env["header"]["device_id"], env)
        try:
            return await ack_tracker.expect(env["header"]["msg_id"], timeout=delay_ms/1000 + 1.0)
        except asyncio.TimeoutError:
            continue
    raise RetryExhausted(env["header"]["msg_id"])  # → error 帧 + action_logs.status='failed'
```

---

# 10. Sequence 顺序控制

## 10.1 作用
- 抵御网络乱序
- 抵御并发发送冲突

## 10.2 规则
- 每个 `user_id` 独立 seq
- ESP32 可选「严格模式」（NVS 配置 `strict_seq=1`）丢弃旧 seq

## 10.3 服务端

```python
# app/services/seq_tracker.py
_last: dict[str, int] = {}      # user_id -> last_seq
# 二期：迁移到 Redis HASH `seq:user`
```

---

# 11. Idempotency（幂等性）

## 11.1 msg_id 去重

### 服务端（一期：内存 LRU）
```python
# app/services/idempotency.py
from collections import OrderedDict
_seen: OrderedDict[str, int] = OrderedDict()
MAX = 1000

def seen(msg_id: str) -> bool:
    if msg_id in _seen: return True
    _seen[msg_id] = 1
    if len(_seen) > MAX: _seen.popitem(last=False)
    return False
```

### 服务端（二期：Redis）
```text
SET idem:msg:<msg_id> 1 EX 600 NX
```

### ESP32 端
固件缓存最近 100 条 msg_id，防重放。

---

# 12. Device Group（扩展能力）

## 12.1 group 定义
```json
{ "group": "office" }
```

## 12.2 数据库支持（与架构文档 §18.6 同步）

```sql
CREATE TABLE device_groups ( ... );
CREATE TABLE device_group_members ( ... );
```

## 12.3 用途
- 多设备统一控制
- 广播宏
- 场景模式

---

# 13. 状态同步机制

## 13.1 status message
```json
{
  "type": "status",
  "payload": { "device_id": "d001", "state": "online", "load": 0.3 }
}
```

服务端处理：更新 `devices.status` + `last_online_at`，并通过 `/ws/client` 广播给订阅了该设备的前端。

## 13.2 sync
上线后服务端可向客户端推送一次 `sync` 全量快照（设备列表 / 在线状态 / 待 ack 数）。

---

# 14. 错误体系

## 14.1 error message
```json
{
  "type": "error",
  "payload": { "code": "E002", "message": "device offline" }
}
```

## 14.2 错误码（合并 V1 + V2）

| code | 含义 | HTTP 等价 |
|---|---|---|
| E001 | parse error | 400 |
| E002 | device offline | 503 |
| E003 | queue full | 429 |
| E004 | invalid action | 422 |
| E005 | unauthorized | 401 |
| E006 | retry exhausted | 504 |

FastAPI 全局异常处理：`app/core/error_handler.py`。

---

# 15. WebSocket Frame 标准

## 15.1 统一帧

所有 WS 消息必须符合：

```json
{ "header": {}, "routing": {}, "payload": {} }
```

FastAPI 端通过 `await ws.receive_json()` / `await ws.send_json(env)` 收发，由 Pydantic 模型校验。

## 15.2 兼容旧 V1 帧

旧 V1 帧 `{ "type": "...", "payload": {...} }`：服务端 `app/api/ws/device.py` 接收时若检测到无 `header`，自动包装为 V2 envelope（`source="legacy"`），保证 ESP32 早期固件兼容。

---

# 16. ESP32 协议兼容要求

ESP32 必须支持：

- out-of-order detection（seq 比对）
- duplicate detection（msg_id LRU 100 条）
- retry-safe execution（执行幂等）
- partial failure handling（macro 单步失败可继续 / 终止由 payload 控制）

---

# 17. Server 路由逻辑

## 17.1 路由优先级
```text
target_devices > group > broadcast > 用户全部设备（兜底）
```

## 17.2 分发流程（落到具体文件）

```text
Receive WS Frame  (app/api/ws/client.py)
   ↓
Pydantic Parse → WsEnvelope
   ↓
JWT Auth         (app/core/security.py:ws_authenticate)
   ↓
Idempotency      (app/services/idempotency.py)
   ↓
Seq Check        (app/services/seq_tracker.py)
   ↓
Resolve Routing  (app/services/routing.py)
   ↓
QueueBackend.push (app/services/queue/{memory|redis}.py)
   ↓
Device Sender   (app/api/ws/device.py 内部 task)
   ↓
WS Send → ESP32
   ↓
Await ACK       (app/services/ack_tracker.py)
   ↓
Retry / Log     (action_logs)
```

---

# 18. 性能设计

## 18.1 延迟目标（V1 保留）

| 场景 | 目标 |
|---|---|
| LAN action | < 20ms |
| ACK 回传 | < 50ms |
| 重试恢复 | < 200ms |

## 18.2 并发模型

- FastAPI 全异步
- 每设备一条 sender coroutine + 一条 `asyncio.Queue`
- 二期：Redis Queue + Pub/Sub 跨实例广播（`bus:device:<id>`）

---

# 19. 安全设计

## 19.1 必须字段
- `user_id`
- `token`（HTTP `Authorization: Bearer <jwt>` 或 WS query `?token=...`）
- `msg_id`

## 19.2 防护
- 防重放：msg_id 幂等
- JWT 鉴权：`app/core/security.py`（python-jose / PyJWT）
- 设备绑定用户：`devices.owner_user_id`
- CORS：`app/main.py` 已读取 `BACKEND_CORS_ORIGINS`
- 限流（二期 Redis）：`rate:<user>:<bucket>`

---

# 20. 扩展能力预留（V1 保留）

V2 协议已预留：

- MQTT bridge（`app/api/mqtt/`，Phase 2）
- HTTP fallback（`POST /api/v2/action` 同语义，便于无 WS 环境）
- BLE routing（ESP32 firmware Phase 2）
- Cloud relay（Phase 3）
- Plugin system（`app/services/plugin/`）
- AI automation（`app/services/ai_automation.py`，Phase 3）

---

# 21. MVP 协议范围（V1 保留）

必须支持：

- action message
- ack
- retry
- routing（device_id）
- heartbeat

落到当前仓库即：`app/api/ws/{device,client}.py` + `app/services/{dispatcher,routing,ack_tracker,queue/memory}.py`。

---

# 22. 总结

V2 协议目标：

> 构建一个可靠、可扩展、多设备一致性的输入控制通信标准

核心原则（V1 全部保留）：

- 可追踪（traceable）—— `msg_id + seq`，colorlog + `action_logs` 串联
- 可重试（retryable）—— `AckTracker` 指数退避，二期可换 Redis Stream
- 可排序（ordered）—— 用户级 seq + 设备端严格模式
- 可路由（routable）—— `target_devices > group > broadcast`
- 可扩展（extensible）—— `/api/v1` 与 `/api/v2` 并存，渐进迁移
