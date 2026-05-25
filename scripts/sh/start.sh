#!/usr/bin/env bash
# 起服 (mysql + redis + app)，先确认 8000 / 3306 / 6379 端口
# 用法:
#   ./scripts/start.sh                # 检查端口，被占用则报错退出
#   ./scripts/start.sh --kill         # 占用就杀
#   ./scripts/start.sh --build        # 起之前先 build
set -euo pipefail
source "$(dirname "$0")/_common.sh"
require_docker

KILL=0
BUILD=0

while [ $# -gt 0 ]; do
  case "$1" in
    --kill)  KILL=1; shift ;;
    --build) BUILD=1; shift ;;
    *) c_red "未知参数: $1"; exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"

# 仅检查 app 端口；mysql/redis 容器已经 healthy 也算，不重复检查
for port in "$APP_PORT"; do
  if port_in_use "$port"; then
    pids=$(port_pids "$port")
    # 如果占用方就是我们自己的容器，不算冲突
    if docker ps --filter "publish=$port" --format '{{.Names}}' | grep -q .; then
      c_yel "端口 $port 已由 docker 容器占用，将由 compose 接管"
      continue
    fi
    c_yel "端口 $port 被本机进程占用 (PID: $pids)"
    if [ "$KILL" -eq 1 ] && [ -n "$pids" ]; then
      for pid in $pids; do
        safe_kill_pid "$pid" || true
      done
      sleep 1
    else
      c_red "加 --kill 自动清理或手动停止后再起"
      exit 1
    fi
  fi
done

if [ "$BUILD" -eq 1 ]; then
  c_cyn "==> docker compose build $COMPOSE_SERVICE"
  docker compose build "$COMPOSE_SERVICE"
fi

c_cyn "==> docker compose up -d"
docker compose up -d

c_cyn "==> 等待 app healthy ..."
for i in $(seq 1 60); do
  st=$(docker inspect -f '{{.State.Health.Status}}' py_web_app 2>/dev/null || echo "")
  if [ "$st" = "healthy" ]; then
    c_grn "==> app 已 healthy  ->  http://127.0.0.1:$APP_PORT"
    exit 0
  fi
  printf '.'
  sleep 1
done
c_red "等待超时（60s），用 docker compose logs app 排查"
exit 1
