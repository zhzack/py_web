# HID Gateway Platform

# ESP32-S3 固件详细设计文档（V1.1 — 与服务端 `py_web` 对齐版）

> 改造说明：固件本身所有 V1 模块（WiFi / WS / Protocol / Queue / Executor / HID / Heartbeat / Watchdog / 状态机 / 调试）**全部保留**，本版按当前服务端实际端点（`/ws/device`）、V2 envelope（msg_id / seq / routing / ack）、与 colorlog 链路对齐字段语义，并补齐 V1 中没明确写到的「NVS 配置项 / OTA 钩子 / 与 backend AckTracker 的握手细节」。

---

# 1. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | ESP32-S3 Firmware |
| 芯片 | ESP32-S3 N16R8 |
| SDK | ESP-IDF |
| 通信 | WebSocket Client → `ws://<host>:8000/ws/device` |
| 协议 | V2 envelope（见协议设计文档） |
| 输出 | USB HID（一期） / BLE HID（二期） |
| 架构 | FreeRTOS 多任务 + 事件驱动 |
| 对端 | `py_web` FastAPI（`app/api/ws/device.py`） |

---

# 2. 固件目标（V1 保留）

ESP32 固件作为系统执行端，负责：

- 连接 WiFi
- 连接 Backend WebSocket Server（`ws://server:8000/ws/device`）
- 接收 Action 指令（V2 envelope）
- 解析协议（cJSON）
- 执行 HID 输出（USB Keyboard / Mouse / 文本）
- 管理执行队列
- 状态上报（status / sync）
- 心跳 / 断线重连
- 幂等 + 序列号校验
- ACK 回报（带 `exec_time_ms`）

核心定位：

> 可靠的低延迟 HID 执行节点

---

# 3. 固件整体架构（V1 保留）

```text
WiFi Layer
   ↓
WebSocket Client
   ↓
Protocol Parser  (V2 envelope)
   ↓
Action Queue     (FreeRTOS Queue)
   ↓
Executor Engine
   ↓
HID Driver       (USB / BLE 抽象)
```

---

# 4. FreeRTOS 任务设计

固件采用多任务并行结构。

## 4.1 Task 列表（V1 保留 + heartbeat 显式化）

| Task | 功能 | 优先级 | Stack |
|---|---|---|---|
| wifi_task | WiFi 连接与维护 | 高 | 4 KB |
| ws_task | WebSocket 通信（收发） | 高 | 8 KB |
| protocol_task | V2 envelope 解析、幂等 / seq 检查 | 中高 | 6 KB |
| action_task | 队列调度 → executor | 高 | 6 KB |
| hid_task | USB HID 输出 | 高 | 4 KB |
| heartbeat_task | 心跳上报 + 状态汇总 | 低 | 2 KB |
| ota_task（预留） | OTA 升级（Phase 2） | 中 | 6 KB |

## 4.2 任务关系

```text
WS Task ──→ raw json queue ──→ Protocol Task ──→ Action Queue ──→ Executor Task ──→ HID Task
   ↑                                                                                    │
   └────────── ack/status/error envelope ←──────── (ACK 由 Executor 完成后回填) ─────────┘
```

---

# 5. WebSocket Client 设计

## 5.1 连接配置（与服务端对齐）

```c
// 与 app/api/ws/device.py 对齐
#define WS_URI_FMT  "ws://%s:%d/ws/device?token=%s"
```

- `host` / `port` / `token`：NVS 持久化
- `token`：注册阶段由用户在 Web 控制台生成的 device token（JWT 派生），写入设备 NVS

## 5.2 连接生命周期（V1 保留）

```text
INIT → WIFI_CONNECTED → WS_CONNECTING → REGISTER → ONLINE → HEARTBEAT → (DISCONNECT) → RECONNECT
```

## 5.3 自动重连策略

- 指数退避：1s → 2s → 4s → 8s → 16s → 30s（封顶）
- WiFi 断开 → 自动恢复后立即触发 ws 重连
- 重连成功后**重新 register**

---

# 6. 协议解析模块（升级到 V2 envelope）

## 6.1 输入数据结构

```json
{
  "header": {
    "msg_id": "uuid",
    "seq": 10001,
    "timestamp": 1710000000,
    "type": "action",
    "device_id": "esp32_001",
    "priority": 0
  },
  "routing": { "target_devices": ["esp32_001"] },
  "payload": { "type": "keyboard_tap", "key": "KEY_A" }
}
```

> 兼容性：若 header 缺失（旧 V1 帧），固件自动补 `msg_id = uuid`、`type=action` 后继续处理。

## 6.2 Parser 职责

- cJSON 解析
- 校验 header / payload 必填字段
- 幂等检查（msg_id LRU 100）
- seq 检查（严格模式下丢弃旧 seq）
- 转换为内部 `action_msg_t` 投递 Action Queue

## 6.3 内部结构

```c
typedef struct {
    char     type[32];     // keyboard_tap / mouse_move / text / macro / delay / ...
    char     key[16];
    int32_t  x, y;
    int32_t  delay_ms;
    char     text[128];    // 文本输入；超长则分片
    int      interval_ms;  // 文本输入字符间隔
} action_t;

typedef struct {
    char     msg_id[37];   // uuid 36 + NUL
    uint32_t seq;
    action_t action;
    uint32_t recv_tick;
} action_msg_t;
```

---

# 7. Action Queue 系统

## 7.1 队列实现
```c
QueueHandle_t action_queue;  // FreeRTOS Queue
```

## 7.2 特性（V1 保留 + 显式）
- FIFO
- 长度 64~256（NVS 可配，默认 128）
- 写满策略可配：`drop_oldest` / `reject_new`，默认 `drop_oldest` 并回 `error E003 queue full`
- 写入由 protocol_task，消费由 action_task

---

# 8. Action Executor 引擎

## 8.1 职责
- 从队列获取 action
- switch type → handler
- 调用 HID 抽象层
- 测量 `exec_time_ms`
- **构造 ACK envelope 投递 ws_task**

## 8.2 执行流程
```text
Fetch Action → Switch(type) → Execute Handler → HID Send
           ↓
     exec_time_ms
           ↓
     Build ACK Envelope → ws_send_queue
```

## 8.3 ACK 构造（与服务端 AckTracker 对齐）
```json
{
  "header": { "type": "ack", "msg_id": "<self_uuid>", "ref_msg_id": "<recv_msg_id>", "timestamp": 1710000000 },
  "payload": { "status": "ok", "exec_time_ms": 12 }
}
```

失败时 `status="failed"` + `payload.error = { code, message }`。

## 8.4 支持 Action（V1 保留）

| 类型 | 支持 |
|---|---|
| keyboard_tap | ✔ |
| keyboard_down | ✔ |
| keyboard_up | ✔ |
| mouse_move | ✔ |
| mouse_click | ✔ |
| delay | ✔ |
| text | ✔（逐字符发送，使用 `interval_ms`） |
| macro | ✔（多步顺序执行，支持中断帧） |

---

# 9. USB HID 模块（TinyUSB，V1 保留）

## 9.1 HID 类型
- Keyboard
- Mouse

## 9.2 Keyboard
```c
void hid_keyboard_press(uint8_t keycode);
void hid_keyboard_release(uint8_t keycode);
```

## 9.3 Mouse
```c
void hid_mouse_move(int x, int y);
void hid_mouse_click(uint8_t button);
```

## 9.4 文本输入

逐字符转 keycode：
```text
text → keycode mapping table → tap loop（按 interval_ms 节奏）
```

Mapping 表覆盖 ASCII + 常用 shift 组合，UTF-8 非 ASCII 字符返回 `E004 invalid action`。

---

# 10. HID 抽象层设计（V1 保留）

## 10.1 统一接口
```c
typedef struct {
    void (*keyboard_tap)(int key);
    void (*keyboard_down)(int key);
    void (*keyboard_up)(int key);
    void (*mouse_move)(int x, int y);
    void (*mouse_click)(int button);
} hid_driver_t;
```

## 10.2 设计目标
- 可替换 USB / BLE
- 上层不感知底层实现
- 支持未来 Gamepad / 多目标合成

---

# 11. WiFi 管理模块（V1 保留）

## 11.1 功能
- 自动连接 AP
- 掉线重连
- 状态上报到 ws（`status` 帧的 `wifi_rssi`）

## 11.2 状态机
```text
DISCONNECTED → CONNECTING → CONNECTED → (FAILED → RETRY)
```

## 11.3 配网
- 一期：NVS 预置 SSID / PASSWORD
- 二期：SmartConfig / BLE 配网

---

# 12. 心跳机制（与服务端 30s 离线判定对齐）

## 12.1 心跳内容（V2 envelope 化）
```json
{
  "header": { "type": "heartbeat", "msg_id": "uuid", "device_id": "esp32_001", "timestamp": 1710000000 },
  "payload": { "uptime": 12345, "wifi_rssi": -55, "queue_len": 3, "load": 0.12 }
}
```

## 12.2 周期
- 10 秒一次（与服务端 `device_registry` 30s 超时一致）

## 12.3 超时
- 30 秒未收到服务端任何帧 → 主动断开 → 重连

---

# 13. 内存与性能设计（V1 保留）

## 13.1 PSRAM 用途
- Action buffer
- JSON 解析缓冲（cJSON 工作区）
- Macro steps 暂存

## 13.2 Stack 分配

见 §4.1。

---

# 14. 错误处理系统（与服务端错误码对齐）

## 14.1 错误类型

| code | 描述 |
|---|---|
| E001 | JSON parse error |
| E002 | device offline（自检：USB 未挂载） |
| E003 | queue full |
| E004 | invalid action |
| E005 | unauthorized（token 校验失败） |
| E006 | retry exhausted（本地重发 hid 失败） |

## 14.2 错误帧
```json
{
  "header": { "type": "error", "ref_msg_id": "<orig>", "msg_id": "<uuid>" },
  "payload": { "code": "E004", "message": "invalid action" }
}
```

## 14.3 恢复策略
- WS 错误：自动重连
- 队列满：丢最旧并回 E003
- HID 异常：feed watchdog + 局部 reset

---

# 15. Watchdog 设计（V1 保留）

- 启用 ESP-IDF Task WDT
- `ws_task` / `action_task` 必须周期 feed
- 守护进程 5s 未 feed → 复位

---

# 16. 状态管理

## 16.1 Device State
```c
typedef enum {
    STATE_INIT,
    STATE_WIFI_OK,
    STATE_WS_OK,
    STATE_REGISTERED,
    STATE_ONLINE,
    STATE_ERROR
} device_state_t;
```

## 16.2 状态上报

状态变化时主动 send `status` envelope；周期 heartbeat 也带状态。

---

# 17. NVS 配置项（新增，对齐服务端配置）

| Key | 说明 | 示例 |
|---|---|---|
| `wifi_ssid` | WiFi SSID | `MyAP` |
| `wifi_pass` | WiFi 密码 | — |
| `server_host` | 后端 IP / 域名 | `192.168.1.10` |
| `server_port` | 后端端口 | `8000` |
| `device_id` | 设备唯一 ID | `esp32_001` |
| `device_token` | JWT 设备 token | — |
| `strict_seq` | 严格 seq 模式 | `0` / `1` |
| `queue_size` | Action 队列长度 | `128` |
| `queue_policy` | 满策略 | `drop_oldest` / `reject_new` |

---

# 18. 调试系统

## 18.1 日志输出
- UART log
- `ESP_LOGI / ESP_LOGW / ESP_LOGE`
- 与服务端 colorlog 风格对齐（前缀 `[wifi]` `[ws]` `[proto]` `[exec]` `[hid]`），便于跨端 grep

## 18.2 Protocol Debug
打印：raw json / parsed action / exec result / ack。

## 18.3 远端调试帧（新增）
服务端可发 `type="dev_cmd"`（仅 `app/api/dev/` 下发），允许临时打开/关闭 verbose log；不进入主流程。

---

# 19. 性能目标（V1 保留）

| 项目 | 目标 |
|---|---|
| action latency | < 20ms LAN |
| queue delay | < 5ms |
| reconnect time | < 3s |

---

# 20. MVP 固件范围（V1 保留）

必须实现：

- WiFi 连接
- WebSocket Client（`/ws/device`）
- V2 envelope 解析（兼容旧 V1 帧）
- Action Queue
- USB Keyboard / Mouse / 文本
- ACK + 失败上报
- 基础重连
- heartbeat（带 status）
- msg_id 幂等去重
- token 鉴权

---

# 21. 后续扩展（V1 全部保留）

## Phase 2
- BLE HID
- Gamepad
- Macro engine（条件 / 循环）
- OTA（HTTPS + 签名校验）
- 严格 seq 模式开关 UI

## Phase 3
- Lua scripting（脚本化宏）
- Plugin system
- Multi-device routing（设备间互转）
- 边缘 AI（手势 → 输入映射）

---

# 22. 总结

ESP32 固件是整个系统的执行核心，其设计目标是：

> 稳定、低延迟、可扩展的 HID 执行节点

核心原则（V1 全部保留）：

- 队列解耦
- 状态机驱动
- 驱动抽象（USB/BLE 可换）
- 高可靠性优先（watchdog + retry + 幂等）
- **与服务端协议字段、错误码、心跳周期严格对齐**（本版新增显式约束）
