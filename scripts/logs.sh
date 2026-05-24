#!/usr/bin/env bash
# 查看 app 日志
# 用法:
#   ./scripts/logs.sh              # 跟随 app
#   ./scripts/logs.sh --all        # 跟随 mysql + redis + app
#   ./scripts/logs.sh --tail 200   # 只看最后 200 行（不 follow）
set -euo pipefail
source "$(dirname "$0")/_common.sh"
require_docker

TARGET="$COMPOSE_SERVICE"
FOLLOW="-f"
TAIL="--tail=100"

while [ $# -gt 0 ]; do
  case "$1" in
    --all)   TARGET=""; shift ;;
    --tail)  TAIL="--tail=$2"; FOLLOW=""; shift 2 ;;
    *) c_red "未知参数: $1"; exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"
docker compose logs $FOLLOW $TAIL $TARGET
