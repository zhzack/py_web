"""停止容器。

用法:
    python scripts/stop.py            # 停所有 compose 服务
    python scripts/stop.py --app      # 只停 app
    python scripts/stop.py --rm       # 停并 down（移除容器，保留数据卷）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts.py._common import COMPOSE_SERVICE, cyn, grn, require_docker, run  # noqa: E402


def main():
    require_docker()
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", action="store_true", help="只停 app 服务")
    ap.add_argument("--rm", action="store_true", help="docker compose down")
    args = ap.parse_args()

    if args.app:
        run(["docker", "compose", "stop", COMPOSE_SERVICE])
    elif args.rm:
        run(["docker", "compose", "down"])
    else:
        run(["docker", "compose", "stop"])

    grn("==> 完成")
    run(["docker", "compose", "ps"], check=False)


if __name__ == "__main__":
    main()
