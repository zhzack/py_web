#!/usr/bin/env bash
# 公共函数库：颜色输出 / 端口检测 / 项目根
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PORT="${APP_PORT:-8000}"
COMPOSE_SERVICE="${COMPOSE_SERVICE:-app}"
IMAGE_NAME="${IMAGE_NAME:-hid-gateway:latest}"

c_red()   { printf "\033[31m%s\033[0m\n" "$*"; }
c_grn()   { printf "\033[32m%s\033[0m\n" "$*"; }
c_yel()   { printf "\033[33m%s\033[0m\n" "$*"; }
c_cyn()   { printf "\033[36m%s\033[0m\n" "$*"; }

# 返回 0 表示端口已被占用
port_in_use() {
  local port="$1"
  if command -v netstat >/dev/null 2>&1; then
    netstat -ano 2>/dev/null | grep -E "[:.]${port} " | grep -qi LISTEN
  elif command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | grep -q ":${port} "
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
  else
    return 1
  fi
}

# 打印占用 port 的 PID（Windows 用 netstat 抓最后一列）
port_pids() {
  local port="$1"
  if command -v netstat >/dev/null 2>&1; then
    netstat -ano 2>/dev/null | grep -E "[:.]${port} " | grep -i LISTEN | awk '{print $NF}' | sort -u
  fi
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    c_red "docker 未安装或不在 PATH"
    exit 1
  fi
}

# 进程名包含这些关键词时，禁止 kill —— 避免误杀 Docker Desktop / WSL / 系统服务
KILL_BLOCKLIST_RE='docker|vpnkit|wsl|com\.docker|System|svchost|services\.exe'

# 给定 PID，返回进程映像名（Windows 走 tasklist，Linux 走 /proc）
pid_name() {
  local pid="$1"
  if command -v tasklist >/dev/null 2>&1; then
    tasklist //FI "PID eq $pid" //NH //FO CSV 2>/dev/null \
      | head -1 | awk -F'","' '{gsub(/"/, "", $1); print $1}'
  elif [ -r "/proc/$pid/comm" ]; then
    cat "/proc/$pid/comm"
  fi
}

# 仅当进程是 python / uvicorn / node 时才允许 kill
safe_kill_pid() {
  local pid="$1"
  local name
  name="$(pid_name "$pid" || echo unknown)"
  if echo "$name" | grep -Eqi "$KILL_BLOCKLIST_RE"; then
    c_red "  !! 拒绝 kill PID=$pid name=$name (受保护进程)"
    return 1
  fi
  if echo "$name" | grep -Eqi 'python|uvicorn|node'; then
    c_yel "  -> kill PID=$pid name=$name"
    if command -v taskkill >/dev/null 2>&1; then
      taskkill //PID "$pid" //F >/dev/null 2>&1 || true
    else
      kill -9 "$pid" 2>/dev/null || true
    fi
    return 0
  fi
  c_red "  !! 跳过 PID=$pid name=$name (非应用进程，需手动处理)"
  return 1
}
