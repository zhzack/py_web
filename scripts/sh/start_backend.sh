#!/usr/bin/env bash
# 本地直接跑后端 (uvicorn)，启动前先检查端口占用
# 用法:
#   ./scripts/start_backend.sh                # 端口被占用则退出
#   ./scripts/start_backend.sh --kill         # 端口被占用则杀掉占用进程
#   ./scripts/start_backend.sh --port 8001    # 自定义端口
set -euo pipefail
source "$(dirname "$0")/_common.sh"

KILL=0
RELOAD="--reload"
HOST="0.0.0.0"
PORT="$APP_PORT"

while [ $# -gt 0 ]; do
  case "$1" in
    --kill)     KILL=1; shift ;;
    --port)     PORT="$2"; shift 2 ;;
    --no-reload) RELOAD=""; shift ;;
    --host)     HOST="$2"; shift 2 ;;
    *) c_red "未知参数: $1"; exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"

if port_in_use "$PORT"; then
  pids=$(port_pids "$PORT")
  c_yel "端口 $PORT 已被占用 (PID: $pids)"
  # 如果占用方是 docker 容器（端口转发由 vpnkit/dockerd 完成），直接拒绝 kill
  if command -v docker >/dev/null 2>&1 && \
     docker ps --filter "publish=$PORT" --format '{{.Names}}' 2>/dev/null | grep -q .; then
    c_red "端口被 docker 容器占用，请先：docker compose stop app"
    exit 1
  fi
  if [ "$KILL" -eq 1 ] && [ -n "$pids" ]; then
    for pid in $pids; do
      safe_kill_pid "$pid" || true
    done
    sleep 1
    if port_in_use "$PORT"; then
      c_red "端口仍被占用，请手动停止后再起"
      exit 1
    fi
  else
    c_red "如需自动结束，请加 --kill；或换端口 --port 8001"
    exit 1
  fi
fi

c_cyn "==> 启动 uvicorn  http://$HOST:$PORT"
exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT" $RELOAD
