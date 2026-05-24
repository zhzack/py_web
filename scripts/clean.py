"""清理 docker 资源。

用法:
    python scripts/clean.py             # 删容器（保留镜像/数据卷）
    python scripts/clean.py --image     # 同时删 hid-gateway:latest
    python scripts/clean.py --volumes   # 同时删数据卷（数据丢失！）
    python scripts/clean.py --all       # 容器 + 镜像 + 数据卷
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _common import IMAGE_NAME, cyn, grn, red, require_docker, run, yel  # noqa: E402


def main():
    require_docker()
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", action="store_true")
    ap.add_argument("--volumes", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    del_img = args.image or args.all
    del_vol = args.volumes or args.all

    if del_vol:
        yel("!! 这将删除 MySQL/Redis 数据卷，数据库内容会全部丢失")
        if input("确认输入 yes： ").strip() != "yes":
            red("取消")
            sys.exit(1)
        run(["docker", "compose", "down", "-v"])
    else:
        run(["docker", "compose", "down"])

    if del_img:
        cyn(f"==> 删除镜像 {IMAGE_NAME}")
        run(["docker", "rmi", "-f", IMAGE_NAME], check=False)

    grn("==> 完成")


if __name__ == "__main__":
    main()
