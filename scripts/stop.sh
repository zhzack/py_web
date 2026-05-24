#!/usr/bin/env bash
# 停止容器
# 用法:
#   ./scripts/stop.sh             # 停所有 compose 服务
#   ./scripts/stop.sh --app       # 只停 app
#   ./scripts/stop.sh --rm        # 停并 down（移除容器，保留数据卷）
set -euo pipefail
source "$(dirname "$0")/_common.sh"
require_docker

ONLY_APP=0
DOWN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --app) ONLY_APP=1; shift ;;
    --rm)  DOWN=1; shift ;;
    *) c_red "未知参数: $1"; exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"

if [ "$ONLY_APP" -eq 1 ]; then
  c_cyn "==> docker compose stop $COMPOSE_SERVICE"
  docker compose stop "$COMPOSE_SERVICE"
elif [ "$DOWN" -eq 1 ]; then
  c_cyn "==> docker compose down"
  docker compose down
else
  c_cyn "==> docker compose stop"
  docker compose stop
fi

c_grn "==> 完成"
docker compose ps
