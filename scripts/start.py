"""起服 (mysql + redis + app)，启动前检查 8000 端口。

用法:
    python scripts/start.py
    python scripts/start.py --kill          # 占用就杀
    python scripts/start.py --build         # 起之前先 build
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _common import APP_PORT, COMPOSE_SERVICE, cyn, grn, port_in_use, port_pids, red, require_docker, run, safe_kill_pid, yel  # noqa: E402


def is_port_taken_by_docker(port: int) -> bool:
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.Names}}"],
            text=True, errors="ignore",
        )
        return bool(out.strip())
    except Exception:
        return False


def wait_healthy(name: str = "py_web_app", timeout: int = 60) -> bool:
    for _ in range(timeout):
        try:
            out = subprocess.check_output(
                ["docker", "inspect", "-f", "{{.State.Health.Status}}", name],
                text=True, errors="ignore",
            ).strip()
            if out == "healthy":
                return True
        except subprocess.CalledProcessError:
            pass
        print(".", end="", flush=True)
        time.sleep(1)
    print()
    return False


def main():
    require_docker()
    ap = argparse.ArgumentParser()
    ap.add_argument("--kill", action="store_true", help="端口被占用时强杀")
    ap.add_argument("--build", action="store_true", help="启动前先 build")
    args = ap.parse_args()

    if port_in_use(APP_PORT):
        if is_port_taken_by_docker(APP_PORT):
            yel(f"端口 {APP_PORT} 已由 docker 容器占用，将由 compose 接管")
        else:
            pids = port_pids(APP_PORT)
            yel(f"端口 {APP_PORT} 被本机进程占用 (PID: {pids or '?'})")
            if args.kill and pids:
                for pid in pids:
                    safe_kill_pid(pid)
                time.sleep(1)
                if port_in_use(APP_PORT):
                    red("端口仍被占用，请手动停止后再起")
                    sys.exit(1)
            else:
                red("加 --kill 自动清理或手动停止后再起")
                sys.exit(1)

    if args.build:
        run(["docker", "compose", "build", COMPOSE_SERVICE])

    run(["docker", "compose", "up", "-d"])

    cyn("==> 等待 app healthy ...")
    if wait_healthy():
        grn(f"==> app 已 healthy  ->  http://127.0.0.1:{APP_PORT}")
    else:
        red("等待超时（60s），用 `docker compose logs app` 排查")
        sys.exit(1)


if __name__ == "__main__":
    main()
