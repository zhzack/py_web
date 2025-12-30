#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
import socket

# ---------------- 配置 ----------------
APP_MODULE = "app.main:app"   # uvicorn app.main:app
HOST = "0.0.0.0"             # 绑定所有网卡，局域网可访问
PORT = 8000                   # 端口
USE_RELOAD = True             # 是否开启自动重载

# ---------------- 获取局域网IP ----------------


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接一个外部IP，不真的发数据
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# ---------------- 构造 uvicorn 命令 ----------------
cmd = [sys.executable, "-m", "uvicorn", APP_MODULE,
       "--host", HOST, "--port", str(PORT)]
if USE_RELOAD:
    cmd.append("--reload")

# ---------------- 打印信息 ----------------
local_ip = get_local_ip()
print(f"Starting FastAPI server...")
print(f"Local:    http://127.0.0.1:{PORT}")
print(f"Network:  http://{local_ip}:{PORT}")
print(f"Command:  {' '.join(cmd)}\n")

# ---------------- 启动 ----------------
try:
    if platform.system() == "Windows":
        # Windows 下直接 run
        subprocess.run(cmd)
    else:
        # Linux/Mac 下使用 exec 替换进程
        os.execvp(cmd[0], cmd)
except KeyboardInterrupt:
    print("\nServer stopped by user.")
