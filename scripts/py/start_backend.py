"""本地直接跑后端 (uvicorn)，启动前检查端口。

用法:
    python scripts/start_backend.py
    python scripts/start_backend.py --kill           # 端口被占就杀
    python scripts/start_backend.py --port 8001
    python scripts/start_backend.py --no-reload
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts.py._common import APP_PORT, PROJECT_ROOT, cyn, grn, kill_pid, port_in_use, port_pids, red, safe_kill_pid, yel  # noqa: E402


def _port_owned_by_docker(port: int) -> bool:
    import shutil
    if not shutil.which("docker"):
        return False
    try:
        import subprocess
        out = subprocess.check_output(
            ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.Names}}"],
            text=True, errors="ignore", timeout=3,
        )
        return bool(out.strip())
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=APP_PORT)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--kill", action="store_true", help="端口被占用时强杀")
    ap.add_argument("--no-reload", action="store_true")
    args = ap.parse_args()

    if port_in_use(args.port):
        pids = port_pids(args.port)
        yel(f"端口 {args.port} 已被占用 (PID: {pids or '?'})")
        if _port_owned_by_docker(args.port):
            red("端口被 docker 容器占用，请先：docker compose stop app")
            sys.exit(1)
        if args.kill and pids:
            for pid in pids:
                safe_kill_pid(pid)
            time.sleep(1)
            if port_in_use(args.port):
                red("端口仍被占用，请手动停止后再起")
                sys.exit(1)
        else:
            red("加 --kill 自动结束，或换端口 --port 8001")
            sys.exit(1)

    cmd = [sys.executable, "-m", "uvicorn", "app.main:app",
           "--host", args.host, "--port", str(args.port)]
    if not args.no_reload:
        cmd.append("--reload")

    cyn(f"==> 启动 uvicorn  http://{args.host}:{args.port}")
    os.chdir(PROJECT_ROOT)
    if sys.platform == "win32":
        import subprocess
        try:
            sys.exit(subprocess.call(cmd))
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
