"""ESP32 设备模拟器。

常驻运行，与真实硬件协议等价：
  1. WS 连接 ws://127.0.0.1:8000/ws/device
  2. register（device_id / capabilities）
  3. heartbeat 每 10s
  4. 收 action envelope → 在终端「执行」（打印）→ 回 ACK
  5. 断线自动重连（指数退避，封顶 30s）
  6. msg_id 去重（最近 100 条）

用法：
    python tests/sim_device.py                       # 默认 esp32_sim_001
    python tests/sim_device.py esp32_sim_002         # 指定 device_id
    python tests/sim_device.py esp32_sim_003 --host 192.168.1.10 --port 8000

可同时开多个进程模拟多设备。
"""
import argparse
import asyncio
import json
import sys
import time
import uuid
from collections import deque

import websockets
from websockets.exceptions import ConnectionClosed

# Windows 控制台 cp936 默认无法打印 emoji；强制 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Windows 控制台 cp936 默认无法打印 emoji；强制 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------- 配置 ----------------
DEFAULT_DEVICE_ID = "esp32_sim_001"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
HEARTBEAT_SEC = 10
CAPABILITIES = ["usb_keyboard", "usb_mouse"]


class SimDevice:
    def __init__(self, device_id: str, host: str, port: int):
        self.device_id = device_id
        self.url = f"ws://{host}:{port}/ws/device"
        self.start_ts = time.time()
        self.seen_ids: deque[str] = deque(maxlen=100)
        self.ws = None

    def _log(self, msg: str):
        print(f"[{self.device_id}] {msg}", flush=True)

    def _envelope(self, msg_type: str, payload: dict, ref_msg_id: str | None = None) -> dict:
        header = {
            "msg_id": str(uuid.uuid4()),
            "type": msg_type,
            "device_id": self.device_id,
            "timestamp": int(time.time()),
            "source": "sim",
        }
        if ref_msg_id:
            header["ref_msg_id"] = ref_msg_id
        return {"header": header, "routing": {}, "payload": payload}

    async def _send(self, env: dict):
        await self.ws.send(json.dumps(env))

    # ----- 动作 "执行" 模拟 -----
    def _execute(self, payload: dict) -> tuple[bool, int, str | None]:
        t = payload.get("type", "unknown")
        if t == "keyboard_tap":
            self._log(f"  ⌨️  tap {payload.get('key')}")
        elif t == "keyboard_down":
            self._log(f"  ⌨️  hold {payload.get('key')}")
        elif t == "keyboard_up":
            self._log(f"  ⌨️  release {payload.get('key')}")
        elif t == "text":
            self._log(f"  📝  type {payload.get('content')!r} interval={payload.get('interval_ms', 0)}ms")
        elif t == "mouse_move":
            self._log(f"  🖱️  move dx={payload.get('x', 0)} dy={payload.get('y', 0)}")
        elif t == "mouse_click":
            self._log(f"  🖱️  click button={payload.get('button', 1)}")
        elif t == "delay":
            self._log(f"  ⏱️  delay {payload.get('delay_ms', 0)}ms")
        elif t == "macro":
            self._log(f"  🎬  macro {len(payload.get('steps', []))} steps")
            for step in payload.get("steps", []):
                self._execute(step)
        else:
            return False, 0, f"unsupported type: {t}"
        # 模拟 5~15ms 执行耗时
        return True, 8, None

    # ----- 主循环 -----
    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(HEARTBEAT_SEC)
            try:
                await self._send(self._envelope("heartbeat", {
                    "uptime": int(time.time() - self.start_ts),
                    "queue_len": 0,
                }))
            except ConnectionClosed:
                return

    async def _recv_loop(self):
        async for raw in self.ws:
            try:
                env = json.loads(raw)
            except json.JSONDecodeError:
                self._log(f"  ❌ bad json: {raw[:200]}")
                continue

            header = env.get("header", {})
            mtype = header.get("type")
            msg_id = header.get("msg_id")
            payload = env.get("payload", {}) or {}

            if mtype == "ack":
                # 服务端对我们 register 的 ack
                self._log(f"  ✅ register ack: {payload}")
                continue

            if mtype == "action":
                if msg_id in self.seen_ids:
                    self._log(f"  ⚠️  dup msg_id={msg_id[:8]}…, ignored")
                    continue
                self.seen_ids.append(msg_id)
                self._log(f"⬇ action msg_id={msg_id[:8]}… {payload}")
                ok, exec_ms, err = self._execute(payload)
                if ok:
                    await self._send(self._envelope(
                        "ack", {"status": "ok", "exec_time_ms": exec_ms},
                        ref_msg_id=msg_id,
                    ))
                else:
                    await self._send(self._envelope(
                        "ack",
                        {"status": "failed", "exec_time_ms": 0,
                         "error": {"code": "E004", "message": err}},
                        ref_msg_id=msg_id,
                    ))
                continue

            self._log(f"  ❓ unknown type={mtype}")

    async def run_once(self):
        self._log(f"connecting {self.url} ...")
        async with websockets.connect(self.url, ping_interval=None) as ws:
            self.ws = ws
            self._log("connected, sending register")
            await self._send(self._envelope("register", {
                "device_id": self.device_id,
                "name": f"sim-{self.device_id}",
                "capabilities": CAPABILITIES,
            }))
            hb_task = asyncio.create_task(self._heartbeat_loop())
            try:
                await self._recv_loop()
            finally:
                hb_task.cancel()

    async def run_forever(self):
        backoff = 1
        while True:
            try:
                await self.run_once()
                # 服务端主动关连接，正常重连
                self._log("connection closed by server, reconnecting...")
                backoff = 1
            except (OSError, ConnectionClosed) as e:
                self._log(f"network error: {e}; retry in {backoff}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
            except KeyboardInterrupt:
                self._log("interrupted, bye")
                return
            except Exception as e:
                self._log(f"unexpected error: {e!r}; retry in {backoff}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)


def main():
    parser = argparse.ArgumentParser(description="ESP32 device simulator")
    parser.add_argument("device_id", nargs="?", default=DEFAULT_DEVICE_ID)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    dev = SimDevice(args.device_id, args.host, args.port)
    try:
        asyncio.run(dev.run_forever())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
