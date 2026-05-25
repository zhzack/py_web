"""公共工具：颜色、端口检测、进程清理、项目根。"""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PORT = int(os.environ.get("APP_PORT", "8000"))
COMPOSE_SERVICE = os.environ.get("COMPOSE_SERVICE", "app")
IMAGE_NAME = os.environ.get("IMAGE_NAME", "hid-gateway:latest")

IS_WIN = sys.platform == "win32"


def _color(code: str, msg: str) -> str:
    if IS_WIN and "ANSICON" not in os.environ:
        try:
            os.system("")  # 触发 ANSI 支持
        except Exception:
            pass
    return f"\033[{code}m{msg}\033[0m"


def red(msg: str): print(_color("31", msg))
def grn(msg: str): print(_color("32", msg))
def yel(msg: str): print(_color("33", msg))
def cyn(msg: str): print(_color("36", msg))


def port_in_use(port: int) -> bool:
    """端口已被占用返回 True。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        s.bind(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def port_pids(port: int) -> list[int]:
    """返回监听 port 的 PID 列表（Windows 用 netstat，Linux 用 ss/lsof）。"""
    pids: set[int] = set()
    if IS_WIN:
        try:
            out = subprocess.check_output(["netstat", "-ano"], text=True, errors="ignore")
        except Exception:
            return []
        for line in out.splitlines():
            if re.search(rf"[:\.]{port}\s", line) and "LISTEN" in line.upper():
                m = re.search(r"(\d+)\s*$", line.strip())
                if m:
                    pids.add(int(m.group(1)))
    else:
        if shutil.which("ss"):
            try:
                out = subprocess.check_output(
                    ["ss", "-ltnp", f"sport = :{port}"], text=True, errors="ignore"
                )
                for m in re.finditer(r"pid=(\d+)", out):
                    pids.add(int(m.group(1)))
            except Exception:
                pass
        elif shutil.which("lsof"):
            try:
                out = subprocess.check_output(
                    ["lsof", "-iTCP", f"-i:{port}", "-sTCP:LISTEN", "-t"],
                    text=True, errors="ignore",
                )
                for line in out.splitlines():
                    if line.strip().isdigit():
                        pids.add(int(line.strip()))
            except Exception:
                pass
    return sorted(pids)


def kill_pid(pid: int) -> bool:
    """强制结束进程。"""
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.kill(pid, 9)
        return True
    except Exception:
        return False


# 进程名包含这些关键词时，禁止 kill —— 避免误杀 Docker Desktop / WSL / 系统服务
_KILL_BLOCKLIST = re.compile(
    r"docker|vpnkit|wsl|com\.docker|svchost|services\.exe|System",
    re.IGNORECASE,
)
_KILL_ALLOWLIST = re.compile(r"python|uvicorn|node", re.IGNORECASE)


def pid_name(pid: int) -> str:
    """返回进程映像名。"""
    try:
        if IS_WIN:
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
                text=True, errors="ignore",
            ).strip()
            if out:
                return out.split('","')[0].lstrip('"')
        else:
            with open(f"/proc/{pid}/comm") as f:
                return f.read().strip()
    except Exception:
        pass
    return "unknown"


def safe_kill_pid(pid: int) -> bool:
    """只 kill python/uvicorn/node 类应用进程，拒绝 kill docker/系统进程。"""
    name = pid_name(pid)
    if _KILL_BLOCKLIST.search(name):
        red(f"  !! 拒绝 kill PID={pid} name={name} (受保护进程)")
        return False
    if not _KILL_ALLOWLIST.search(name):
        red(f"  !! 跳过 PID={pid} name={name} (非应用进程，需手动处理)")
        return False
    yel(f"  -> kill PID={pid} name={name}")
    return kill_pid(pid)


def require_docker():
    if not shutil.which("docker"):
        red("docker 未安装或不在 PATH")
        sys.exit(1)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    cyn(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=str(cwd or PROJECT_ROOT), check=check).returncode
