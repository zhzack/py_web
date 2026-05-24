#!/usr/bin/env bash
# 构建 docker 镜像 (hid-gateway:latest)，含前端
# 用法:
#   ./scripts/build_image.sh                  # docker compose build
#   ./scripts/build_image.sh --no-cache       # 不使用缓存
#   ./scripts/build_image.sh --tag v1.0       # 额外打 tag
set -euo pipefail
source "$(dirname "$0")/_common.sh"
require_docker

EXTRA=""
TAG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --no-cache) EXTRA="$EXTRA --no-cache"; shift ;;
    --tag)      TAG="$2"; shift 2 ;;
    *) c_red "未知参数: $1"; exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"
c_cyn "==> docker compose build $COMPOSE_SERVICE $EXTRA"
docker compose build $EXTRA "$COMPOSE_SERVICE"

if [ -n "$TAG" ]; then
  c_cyn "==> 额外打 tag: $IMAGE_NAME -> hid-gateway:$TAG"
  docker tag "$IMAGE_NAME" "hid-gateway:$TAG"
fi

c_grn "==> 完成"
docker images hid-gateway --format 'table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}'
