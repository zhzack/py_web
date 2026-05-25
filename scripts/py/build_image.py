"""构建 docker 镜像 (hid-gateway:latest)。

用法:
    python scripts/build_image.py
    python scripts/build_image.py --no-cache
    python scripts/build_image.py --tag v1.0
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts.py._common import COMPOSE_SERVICE, IMAGE_NAME, cyn, grn, require_docker, run  # noqa: E402


def main():
    require_docker()
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--tag", help="额外打 tag，例如 v1.0")
    args = ap.parse_args()

    cmd = ["docker", "compose", "build"]
    if args.no_cache:
        cmd.append("--no-cache")
    cmd.append(COMPOSE_SERVICE)

    cyn("==> 构建镜像")
    run(cmd)

    if args.tag:
        cyn(f"==> 额外打 tag: {IMAGE_NAME} -> hid-gateway:{args.tag}")
        run(["docker", "tag", IMAGE_NAME, f"hid-gateway:{args.tag}"])

    grn("==> 完成")
    run(["docker", "images", "hid-gateway",
         "--format", "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}"], check=False)


if __name__ == "__main__":
    main()
