"""端到端冒烟测试：
1. 注册用户 alice
2. 登录拿 JWT
3. 模拟 ESP32 连接 /ws/device 并发送 register
4. 用 JWT 调 POST /api/v2/action 给 esp32_test 发 keyboard_tap
5. 模拟设备回 ack
6. 检查响应 + action_logs 数据
"""
import asyncio
import json
import sys
import time
import uuid

import httpx
import websockets

BASE = "http://127.0.0.1:8000"
WS_DEVICE = "ws://127.0.0.1:8000/ws/device"


async def run():
    async with httpx.AsyncClient(base_url=BASE, timeout=10) as cli:
        # 注册（已存在则忽略）
        r = await cli.post("/api/v1/auth/register", json={
            "username": "alice", "password": "secret123", "role": "user",
        })
        print("register:", r.status_code, r.text[:200])

        # 登录
        r = await cli.post(
            "/api/v1/auth/login",
            data={"username": "alice", "password": "secret123"},
        )
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        print("login OK token=", token[:20], "...")
        auth = {"Authorization": f"Bearer {token}"}

        # me
        r = await cli.get("/api/v1/auth/me", headers=auth)
        print("me:", r.json())

        # 创建设备
        r = await cli.post(
            "/api/v1/devices",
            headers=auth,
            json={"device_uuid": "esp32_test", "name": "Smoke Test ESP32",
                  "capabilities": ["usb_keyboard"]},
        )
        print("create device:", r.status_code, r.text[:200])

        # 启动模拟 ESP32：连 WS 并 register
        device_ready = asyncio.Event()

        async def device_loop():
            async with websockets.connect(WS_DEVICE) as ws:
                await ws.send(json.dumps({
                    "header": {
                        "msg_id": str(uuid.uuid4()),
                        "type": "register",
                        "device_id": "esp32_test",
                        "timestamp": int(time.time()),
                    },
                    "payload": {
                        "device_id": "esp32_test",
                        "name": "sim-esp32",
                        "capabilities": ["usb_keyboard", "usb_mouse"],
                    },
                }))
                # 服务端回 register ack
                raw = await ws.recv()
                print("  [dev] got register ack:", raw[:200])
                device_ready.set()

                # 接 action 并回 ack
                while True:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=8)
                    except asyncio.TimeoutError:
                        return
                    env = json.loads(raw)
                    h = env.get("header", {})
                    if h.get("type") == "action":
                        print(f"  [dev] action received: {env['payload']}")
                        # 回 ack
                        await ws.send(json.dumps({
                            "header": {
                                "msg_id": str(uuid.uuid4()),
                                "ref_msg_id": h["msg_id"],
                                "type": "ack",
                                "timestamp": int(time.time()),
                            },
                            "payload": {"status": "ok", "exec_time_ms": 7},
                        }))

        dev_task = asyncio.create_task(device_loop())
        await asyncio.wait_for(device_ready.wait(), timeout=5)

        # 下发 action
        r = await cli.post(
            "/api/v2/action",
            headers=auth,
            json={
                "device_id": "esp32_test",
                "payload": {"type": "keyboard_tap", "key": "KEY_A"},
                "timeout_ms": 3000,
            },
        )
        print("action:", r.status_code, r.json())

        # logs
        r = await cli.get("/api/v2/logs?limit=5", headers=auth)
        print("logs:", json.dumps(r.json(), indent=2, ensure_ascii=False))

        # online
        r = await cli.get("/api/v1/devices/online", headers=auth)
        print("online:", r.json())

        dev_task.cancel()
        try:
            await dev_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(run())
