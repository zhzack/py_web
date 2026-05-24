"""查看日志。

用法:
    python scripts/logs.py             # 跟随 app
    python scripts/logs.py --all       # 跟随所有服务
    python scripts/logs.py --tail 200  # 只看最后 N 行（不 follow）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _common import COMPOSE_SERVICE, require_docker, run  # noqa: E402


def main():
    require_docker()
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="所有服务的日志")
    ap.add_argument("--tail", type=int, help="只看最后 N 行（不 follow）")
    args = ap.parse_args()

    cmd = ["docker", "compose", "logs"]
    if args.tail is None:
        cmd.extend(["-f", "--tail=100"])
    else:
        cmd.append(f"--tail={args.tail}")
    if not args.all:
        cmd.append(COMPOSE_SERVICE)

    try:
        run(cmd, check=False)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
