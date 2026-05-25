# HID Gateway Platform

# 详细系统架构设计文档（V1.1 — 落地 `py_web` 骨架版）

> 改造说明：本版**不删减任何 V1 既定功能**，仅把设计思路重新落到当前 `f:/webpy/py_web` 仓库的真实结构上。原 V1 中尚未在仓库出现的能力（Redis、JWT、Docker、Alembic、loguru、TS、WS 端点、宏引擎等）改写为「在现有 `app/`、`vue-project/` 骨架内的接入位置 + 落地步骤」，确保架构图与代码可一一对应。

---

# 1. 文档信息

| 项目 | 内容 |
|---|---|
| 项目名称 | HID Gateway Platform |
| 文档版本 | V1.1 |
| 当前阶段 | MVP 架构设计（已对齐 `py_web` 骨架） |
| 开发板 | ESP32-S3 N16R8 |
| 后端 | FastAPI + SQLAlchemy + MySQL（PyMySQL） |
| 前端 | Vue 3 + Vite + Element Plus（JavaScript，沿用 `vue-project/`） |
| 缓存/队列 | asyncio.Queue（一期，运行中） + Redis（二期，可平滑切换） |
| 通信协议 | HTTP + WebSocket + JSON（详见 V2 协议） |
| 进程入口 | `run.py` → uvicorn `app.main:app`，监听 `0.0.0.0:8000` |
| 部署根目录 | `f:/webpy/py_web` |

---

# 2. 项目目标

构建一个：

> 可扩展、多设备、多用户的网络 HID 输入转发平台。

端到端链路保持不变：

```text
Client → Gateway Server (FastAPI) → ESP32 → HID Output (USB / BLE)
```

所有 V1 列出的能力（多客户端、多设备、宏、队列、日志、权限、多协议）**全部保留**，本版只调整「在何处实现、用什么实现」。

---

# 3. 系统角色（保留 V1）

## 3.1 用户（User）

登录、管理设备、创建宏、下发动作。

## 3.2 客户端（Client）

| 类型 | 在本仓库的落点 |
|---|---|
| Vue Web UI | `vue-project/`（已存在，沿用） |
| HTTP Client | 任意 REST 调用方，走 `/api/v1`、`/api/v2` |
| WS Client | `/ws/client`（**新增到 `app/api/`**，见 §9） |
| 自动化脚本 / Bot | 与 HTTP / WS Client 同入口 |
| TCP Client | 预留 `app/api/tcp/`（Phase 2） |
| Mobile App | 复用 HTTP / WS API |

## 3.3 Device（ESP32）

通过 `/ws/device` 长连接注册、心跳、收 action、回 ack、上报状态。

## 3.4 Gateway Server

承担：用户认证、设备管理、动作调度、协议解析、队列、权限、日志（**全部保留**）。

---

# 4. 整体系统架构（落点已对齐仓库）

```text
┌──────────────────────────────────────────────┐
│                   Clients                    │
│  vue-project (Vite dev:5173 / build:dist)    │
│  HTTP / WebSocket Client / Bot               │
└──────────────────┬───────────────────────────┘
                   │ HTTP / WebSocket
                   ▼
┌──────────────────────────────────────────────┐
│         Gateway Server  (FastAPI :8000)      │
│                                              │
│  app/api/v1, v2, dev   ← REST                │
│  app/api/ws/{device,client}  ← 新增 WS 端点   │
│  app/services/{dispatcher,routing,macro,...} │
│  app/database/{models,schemas,crud}          │
│  app/core/{config,logger,security,templates} │
│  /  →  StaticFiles(vue-project/dist)         │
└──────────────────┬───────────────────────────┘
                   │ WebSocket
                   ▼
┌──────────────────────────────────────────────┐
│              ESP32 Devices                    │
│  Protocol Parser · Action Queue · Executor   │
│  USB HID / BLE HID                           │
└──────────────────────────────────────────────┘
```

---

# 5. 架构原则（保留 V1）

## 5.1 模块解耦

```text
WS → Protocol → Action Queue → Executor → HID
```

禁止 WS 层直接触达执行层。

## 5.2 分层落地映射

V1 的「API / Application / Domain / Infrastructure」四层 → `py_web` 现有目录：

| V1 分层 | py_web 落点 |
|---|---|
| API Layer | `app/api/v1`、`app/api/v2`、`app/api/dev`、`app/api/ws/`（新增） |
| Application Layer | `app/services/`（已有 `script_runner`/`log_bus`，新增 `dispatcher.py` / `routing.py` / `macro_engine.py` / `device_registry.py`） |
| Domain Layer | `app/database/models/`、`app/database/schemas/`（按 DDD 解读为 Entity + DTO） |
| Infrastructure | `app/core/`（config / logger / security）+ `app/database/session.py` + `app/services/queue/`（新增） |

> 不新建顶层 `domain/`、`infrastructure/` 目录，避免与现有结构冲突；通过 **package 命名 + 内部清晰边界** 体现分层。

## 5.3 高可扩展性（保留所有 V1 预留点）

BLE HID / 多设备广播 / 插件系统 / 云同步 / MQTT / Lua 宏 / Gamepad / 多协议——全部保留，落点见 §11.

## 5.4 可测试性

核心业务逻辑（Dispatcher / Routing / Macro）以纯 Python 类编写，**不依赖** FastAPI / SQLAlchemy / WebSocket，便于 pytest 单测；I/O 通过依赖注入传入。

---

# 6. 后端技术栈（V1 全部保留，仅替换 1:1 等价品）

| 模块 | V1 计划 | V1.1 落地 | 备注 |
|---|---|---|---|
| Web 框架 | FastAPI | FastAPI（已用） | — |
| ORM | SQLAlchemy | SQLAlchemy（已用） | — |
| DB Migration | Alembic | **Alembic（新增 `app/database/alembic/`）** | 现有 `vehicle_management.sql` 作为 baseline，转 Alembic init revision |
| Database | MySQL 8 | MySQL 8 + PyMySQL（已用） | — |
| Cache | Redis | **Redis（新增 `app/core/cache.py`）** | 通过 `redis.asyncio` 注入 |
| Queue | Redis Queue | **抽象 `QueueBackend`：MemoryBackend（一期）/ RedisBackend（二期）**（`app/services/queue/`） | 同一接口，零业务改动切换 |
| Auth | JWT | **JWT（在 `app/core/security.py` 实现）** | 现 `security.py` 为空文件，正好落实 |
| Logging | loguru | **colorlog（已封装于 `app/core/logger/`）保留并对齐 loguru 体验** | 等价能力：彩色控制台 + 文件滚动 + 异步回调（`log_callbacks/`） |
| Validation | Pydantic | Pydantic + pydantic_settings（已用） | — |
| Testing | pytest | pytest + pytest-asyncio（新增到 `tests/`） | — |
| Container | Docker | **Docker + docker-compose（新增 `deploy/`）** | 见 §22 |
| 模板 | Jinja2 | Jinja2（保留 `app/templates/`） | 用于后台调试页 |
| 配置 | YAML / .env | `pyyaml` + `pydantic_settings`（已用） | — |

> 结论：**没有删除任何 V1 计划组件**。loguru 改用 colorlog 是等价替换（项目已选定）；其余 V1 中尚未实现的（Alembic / Redis / JWT / Docker / pytest）全部以「在现仓库新增的明确文件路径」形式补齐。

---

# 7. 前端技术栈（V1 计划全部保留 / 替换语言为 JS）

| 模块 | V1 计划 | V1.1 落地（`vue-project/`） |
|---|---|---|
| Framework | Vue3 | Vue 3.5（已用） |
| Language | TypeScript | **JavaScript + JSDoc 类型注释**（已用 JS） |
| UI | Element Plus | Element Plus 2.13（已用） |
| State | Pinia | Pinia 3（已用） |
| Router | — | vue-router 4（已用） |
| HTTP | Axios | Axios（`baseURL='/api'`，已用） |
| WS | Native WebSocket | 在 `vue-project/src/utils/ws.js` 新增统一 WS 客户端（自动重连 / 心跳 / 订阅模型） |
| Build | Vite | Vite 7（已用） |
| 类型补强 | TS | **`vue-project/types/*.d.ts` + JSDoc**，保留类型可读性 |

> 不强制升级 TS（避免大改既有代码），但通过 `jsconfig.json` + JSDoc 提供与 V1 等价的类型提示能力。

---

# 8. ESP32 技术栈（保持 V1）

| 模块 | 技术 |
|---|---|
| SDK | ESP-IDF |
| USB HID | TinyUSB |
| BLE HID | NimBLE |
| JSON | cJSON |
| WS Client | esp_websocket_client |
| Storage | NVS |
| RTOS | FreeRTOS |

---

# 9. 后端目录结构（在现仓库**增量**落点）

```text
py_web/
├── run.py
├── requirements.txt                # 增补：redis、python-jose[cryptography]、passlib[bcrypt]、alembic、pytest、pytest-asyncio、httpx
├── .env                            # 增补：JWT_SECRET、REDIS_URL、QUEUE_BACKEND=memory|redis
├── vehicle_management.sql          # 现业务保留
├── deploy/                         # 【新增】Docker / nginx / compose
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── app/
│   ├── main.py                     # 已挂 /api 与 / 静态；新增 ws router 注册
│   ├── api/
│   │   ├── router.py               # 已聚合 v1 / v2 / dev
│   │   ├── v1/                     # 业务 API：auth / device / macro / action
│   │   ├── v2/                     # 演进 API（V2 协议适配）
│   │   ├── dev/                    # 调试 API
│   │   ├── ws/                     # 【新增】
│   │   │   ├── device.py           # /ws/device
│   │   │   └── client.py           # /ws/client
│   │   └── tcp/                    # 【预留】Phase 2
│   ├── core/
│   │   ├── config/config.py        # pydantic_settings（已用）
│   │   ├── logger/                 # colorlog（已用）
│   │   ├── security.py             # 【落实】JWT 编解码 + 密码哈希 + 依赖注入 get_current_user
│   │   ├── cache.py                # 【新增】redis.asyncio 客户端工厂
│   │   └── templates.py            # Jinja2（保留）
│   ├── database/
│   │   ├── base.py / base_class.py / session.py
│   │   ├── alembic/                # 【新增】Alembic 迁移目录
│   │   ├── models/                 # 增加 user / device / device_connection / action_log / macro
│   │   ├── schemas/                # 同步增加 DTO
│   │   └── crud/                   # 同步增加 CRUD
│   ├── services/
│   │   ├── dispatcher.py           # 【新增】Application 层：动作分发
│   │   ├── routing.py              # 【新增】路由引擎（device / group / broadcast）
│   │   ├── macro_engine.py         # 【新增】宏顺序执行 + 可中断 + delay
│   │   ├── device_registry.py      # 【新增】在线设备注册表（内存 + Redis 同步）
│   │   ├── queue/                  # 【新增】队列抽象
│   │   │   ├── base.py             # QueueBackend 接口
│   │   │   ├── memory.py           # asyncio.Queue 实现（一期默认）
│   │   │   └── redis.py            # Redis List 实现（二期）
│   │   ├── ack_tracker.py          # 【新增】ACK + retry + 幂等去重
│   │   ├── log_bus.py              # 已有：异步事件总线
│   │   ├── script_runner.py        # 已有：保留
│   │   └── plugin/                 # 【预留】插件系统（Phase 2）
│   ├── web/views/                  # 旧 SSR 入口（保留备用）
│   ├── templates/                  # Jinja2 模板（保留）
│   ├── resource/                   # 静态资源 / 配置 / 脚本
│   └── utils/
│
├── vue-project/                    # 前端（沿用）
│   └── src/
│       ├── api/                    # 增加 device.js / macro.js / action.js / auth.js
│       ├── route/
│       ├── store/                  # 增加 user / device / ws stores
│       ├── views/                  # 增加 Login / Devices / Console / Macros / Logs
│       ├── components/
│       ├── styles/
│       ├── utils/
│       │   ├── http.js             # axios 拦截器（注入 Bearer）
│       │   └── ws.js               # 【新增】WS 客户端（envelope + ack + reconnect）
│       └── types/                  # JSDoc 类型 d.ts
│
├── logs/
└── tests/                          # pytest
    ├── unit/
    └── api/
```

---

# 10. 前端目录结构

保持 `vue-project/` 不变，按 §9 增量补齐 `api/`、`store/`、`views/`、`utils/ws.js`、`types/`。

---

# 11. ESP32 固件目录结构（保留 V1）

```text
firmware/
├── main/
├── components/
│   ├── wifi/  ├── websocket/  ├── protocol/
│   ├── action_queue/  ├── executor/
│   ├── hid/  ├── usb/  └── ble/
├── tests/
└── CMakeLists.txt
```

详见 ESP32 固件设计文档。

---

# 12. 数据流设计（保留 V1，端点对齐仓库）

```text
Client (Vue/Script)
   ↓ HTTP POST /api/v2/action  或  WS /ws/client
FastAPI Route Handler (app/api/...)
   ↓
Auth (app/core/security.py:get_current_user)
   ↓
Permission Check (CRUD: device.owner_user_id)
   ↓
Dispatcher (app/services/dispatcher.py)
   ↓
Routing Engine (app/services/routing.py)
   ↓
QueueBackend.push(device_id, envelope)   ← memory / redis
   ↓
Device Sender Coroutine  (app/api/ws/device.py)
   ↓
ESP32 (Protocol → Queue → Executor → USB HID)
   ↓ ack 反向 → AckTracker → 落库 action_logs
```

---

# 13. 输入动作系统（保留 V1 全部类型）

## 13.1 Action Envelope（V2 协议见专文）

```json
{
  "header": {
    "msg_id": "uuid", "seq": 10001, "timestamp": 1710000000,
    "source": "web", "user_id": "u123", "device_id": "esp32_001",
    "type": "action", "priority": 1
  },
  "routing": { "target_devices": ["esp32_001"], "broadcast": false, "group": null },
  "payload": { "type": "keyboard_tap", "key": "KEY_A" }
}
```

## 13.2 Action 类型（保留 V1 全部）

| 类型 | 描述 |
|---|---|
| keyboard_tap | 键盘点击 |
| keyboard_down | 按下 |
| keyboard_up | 释放 |
| text | 文本逐字输入（`interval_ms`） |
| mouse_move | 鼠标移动 |
| mouse_click | 鼠标点击 |
| delay | 延迟 |
| macro | 宏（steps） |

## 13.3 宏结构（保留 V1）

```json
{
  "type": "macro",
  "steps": [
    { "type": "keyboard_down", "key": "KEY_CTRL" },
    { "type": "keyboard_tap",  "key": "KEY_C" },
    { "type": "keyboard_up",   "key": "KEY_CTRL" }
  ]
}
```

---

# 14. WebSocket 协议端点

| 路径 | 文件 | 用途 |
|---|---|---|
| `/ws/device` | `app/api/ws/device.py` | ESP32 长连接 |
| `/ws/client` | `app/api/ws/client.py` | 浏览器/脚本实时控制 |

协议类型：`register / heartbeat / action / ack / error / status / sync`，详见 V2 协议文档。

---

# 15. 设备生命周期（保留 V1）

```text
BOOT → WIFI_CONNECT → WS_CONNECT → REGISTER → ONLINE → HEARTBEAT
                                                       ↓
                                                DISCONNECT → RECONNECT
```

- ESP32 心跳：10s
- 服务端离线判定：>30s 未收到心跳；由 `device_registry.py` 中后台 task 维护

---

# 16. 队列系统（保留 V1，新增抽象）

## 16.1 抽象

```python
# app/services/queue/base.py
class QueueBackend(Protocol):
    async def push(self, device_id: str, envelope: dict) -> None: ...
    async def pop(self, device_id: str) -> dict | None: ...
    async def size(self, device_id: str) -> int: ...
```

## 16.2 一期：MemoryBackend

```python
# app/services/queue/memory.py
_queues: dict[str, asyncio.Queue] = {}
```

避免单设备阻塞影响整体。

## 16.3 二期：RedisBackend

```text
key: queue:device:<device_id>   命令: LPUSH / BRPOP
```

通过 `.env` `QUEUE_BACKEND=redis` 切换，业务代码零改动。

## 16.4 Dispatcher 流程（保留 V1）

```text
Receive Action → Validate → Permission Check → QueueBackend.push → Sender → WS
```

---

# 17. 权限系统（保留 V1）

## 17.1 JWT

登录返回 `Bearer Token`，由 `app/core/security.py` 实现：

- `create_access_token(user_id, role) -> str`
- `decode_token(token) -> TokenPayload`
- FastAPI dependency `get_current_user`
- WS 鉴权：连接 querystring `?token=...` 或首帧 `auth`

## 17.2 设备归属

`devices.owner_user_id` 控权；`role='admin'` 绕过。

---

# 18. MySQL 数据库设计（保留 V1 全部表 + 与现仓库风格统一）

> 命名 / 字符集 / 时间戳约定继承 `vehicle_management.sql`：utf8mb4_general_ci、`created_at` / `updated_at`（`ON UPDATE CURRENT_TIMESTAMP`）、ENUM 状态、外键 `ON DELETE CASCADE`。

## 18.1 users

```sql
CREATE TABLE `users` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(64) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin','user') DEFAULT 'user',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

## 18.2 devices

```sql
CREATE TABLE `devices` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `device_uuid` VARCHAR(128) NOT NULL UNIQUE,
    `owner_user_id` BIGINT,
    `name` VARCHAR(128),
    `capabilities` JSON,
    `status` ENUM('offline','online','busy','error') DEFAULT 'offline',
    `last_online_at` DATETIME,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_device_owner` FOREIGN KEY (`owner_user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_device_owner` (`owner_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';
```

## 18.3 device_connections

```sql
CREATE TABLE `device_connections` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `device_id` BIGINT NOT NULL,
    `ip` VARCHAR(64),
    `session_id` VARCHAR(128),
    `connected_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `disconnected_at` DATETIME,
    CONSTRAINT `fk_conn_device` FOREIGN KEY (`device_id`) REFERENCES `devices`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备连接历史';
```

## 18.4 action_logs

```sql
CREATE TABLE `action_logs` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `msg_id` CHAR(36) NOT NULL UNIQUE,
    `user_id` BIGINT,
    `device_id` BIGINT,
    `action_type` VARCHAR(64),
    `payload_json` JSON,
    `status` ENUM('pending','sent','acked','failed') DEFAULT 'pending',
    `exec_time_ms` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_action_device` (`device_id`),
    INDEX `idx_action_user`   (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动作日志';
```

## 18.5 macros

```sql
CREATE TABLE `macros` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `name` VARCHAR(128) NOT NULL,
    `content_json` JSON NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_macro_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='宏定义';
```

## 18.6 device_groups（保留 V1 设备组能力）

```sql
CREATE TABLE `device_groups` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `owner_user_id` BIGINT NOT NULL,
    `name` VARCHAR(128) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备组';

CREATE TABLE `device_group_members` (
    `group_id` BIGINT NOT NULL,
    `device_id` BIGINT NOT NULL,
    PRIMARY KEY (`group_id`, `device_id`),
    CONSTRAINT `fk_dgm_group`  FOREIGN KEY (`group_id`)  REFERENCES `device_groups`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dgm_device` FOREIGN KEY (`device_id`) REFERENCES `devices`(`id`)       ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备组成员';
```

## 18.7 迁移策略

- baseline：现 `vehicle_management.sql` 作 v0 schema
- 引入 Alembic：`alembic init app/database/alembic` → 生成首个 revision 包含上述新表
- 后续表结构变更全部走 Alembic

---

# 19. 日志系统（保留 V1，落到现 logger 体系）

## 19.1 框架（已存在 + 增强）

- `app/core/logger/log_config.py`：colorlog 格式 + `RotatingFileHandler`（等价 loguru rotate）
- `app/core/logger/logger.py`：统一 `logger`
- `app/core/logger/execution_logger.py`：动作链路 trace（msg_id 串联）
- `app/core/logger/log_callbacks/`：异步钩子，桥接 → MySQL `action_logs`、WS 推送 `/ws/client` 实时日志面板

## 19.2 日志类型（保留 V1）

| 类型 | 描述 |
|---|---|
| system | 系统启动 / 配置 |
| action | 动作下发 / ACK / 重试 |
| device | 设备上线 / 心跳 / 离线 |
| protocol | WS 帧 raw / parsed |
| security | 登录 / 权限拒绝 |

## 19.3 目标（保留 V1）

动作追踪、用户审计、协议调试、错误分析、性能分析。

---

# 20. Redis 设计（保留 V1，落到 `app/core/cache.py`）

| 功能 | 用途 | Key 约定 |
|---|---|---|
| 队列 | 设备动作队列 | `queue:device:<device_id>` |
| 会话 | JWT 黑名单 | `auth:blacklist:<jti>` |
| 在线状态 | 在线设备集合 | `device:online`（SET） |
| 限流 | 接口/WS 防刷 | `rate:<user>:<bucket>` |
| 幂等 | msg_id 去重 | `idem:msg:<msg_id>`（TTL） |
| Pub/Sub | 多实例广播 | `bus:device:<device_id>` |

---

# 21. ESP32 FreeRTOS 架构（保留 V1）

## 21.1 Task

| Task | 用途 |
|---|---|
| wifi_task | WiFi 连接 |
| ws_task | WebSocket 通信 |
| protocol_task | 协议解析 |
| action_task | 动作调度 |
| hid_task | USB HID 输出 |
| heartbeat_task | 心跳上报 |

## 21.2 数据流

```text
WS Receive → Protocol Parse → Action Queue → Executor → USB HID → ACK
```

---

# 22. 部署架构（V1 Docker 全保留）

## 22.1 开发

```bash
python run.py                  # 后端 :8000
cd vue-project && npm run dev  # 前端 :5173（CORS 已放行）
cd vue-project && npm run build  # 生产产物 → FastAPI 挂 /
```

## 22.2 docker-compose（`deploy/docker-compose.yml`）

```yaml
services:
  backend:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    env_file: ../.env
    depends_on: [mysql, redis]
    ports: ["8000:8000"]

  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DB}
    volumes: ["mysql_data:/var/lib/mysql"]

  redis:
    image: redis:7
    volumes: ["redis_data:/data"]

  nginx:
    image: nginx:1.27
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ../vue-project/dist:/usr/share/nginx/html:ro
    ports: ["80:80"]
    depends_on: [backend]

volumes:
  mysql_data:
  redis_data:
```

## 22.3 Docker 网络结构

```text
Browser → Nginx → (静态: vue-project/dist | /api,/ws: backend) → MySQL / Redis
```

---

# 23. 单元测试（保留 V1）

## 23.1 Backend

| 类型 | 技术 | 落点 |
|---|---|---|
| Unit | pytest | `tests/unit/` |
| API | httpx.AsyncClient | `tests/api/` |
| Async | pytest-asyncio | — |
| Mock | unittest.mock | mock device ws / queue / db |

## 23.2 ESP32

`ESP-IDF Unity Test`

---

# 24. MVP 范围（保留 V1）

## 24.1 必须完成

- ESP32 自动连接服务端（`/ws/device`）
- Vue 控制台发送输入
- USB Keyboard / Mouse / 文本输入
- 多设备管理 + 用户登录（JWT）
- 动作日志（MySQL）
- ACK + Queue（一期 memory）

## 24.2 延期项

BLE HID / Lua / Gamepad / OTA / 插件 / 云同步 / MQTT / 图形化拖拽（落点已预留，不丢）。

---

# 25. 第二阶段规划（保留 V1）

- BLE HID（NimBLE）
- Macro DSL（条件 / 循环 / 跳转）
- 插件系统（`app/services/plugin/`，热加载）
- Redis 队列 + 多实例
- Alembic 持续迁移
- Docker / Nginx 生产部署
- MQTT bridge（`app/api/mqtt/`）
- AI 自动化（生成宏 / 异常分析）

---

# 26. 开发顺序建议（保留 V1）

## 第一阶段

1. ESP32 USB Keyboard 原型
2. ESP32 WS Client
3. FastAPI WS Server（`app/api/ws/`）
4. Vue 控制台扩展（沿用 `vue-project/`）
5. Action 协议（V2 envelope）
6. Queue（memory backend）+ AckTracker
7. MySQL（新增表）+ Alembic baseline
8. JWT + 设备归属权限
9. colorlog → action_logs 异步钩子
10. Redis（切换为 RedisBackend）

## 第二阶段

BLE HID / Macro Engine / Device Group / Route System / Plugin System / MQTT / OTA。

---

# 27. 最终目标（保留 V1）

> 一个可扩展、模块化、多设备、多用户的 HID Gateway Platform。

能力：USB HID、BLE HID、多客户端、多协议、自动化输入、云控制、插件扩展、企业级日志与权限体系——**全部不删减**，本版仅给出在 `py_web` 仓库中的清晰落点。
