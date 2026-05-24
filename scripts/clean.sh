#!/usr/bin/env bash
# 清理 docker 资源
# 默认：只停容器 + 删容器（保留镜像和数据卷）
# 用法:
#   ./scripts/clean.sh              # 删容器
#   ./scripts/clean.sh --image      # 同时删 hid-gateway:latest 镜像
#   ./scripts/clean.sh --volumes    # 同时删 mysql/redis 数据卷（数据会丢！）
#   ./scripts/clean.sh --all        # 容器 + 镜像 + 数据卷
set -euo pipefail
source "$(dirname "$0")/_common.sh"
require_docker

DEL_IMG=0
DEL_VOL=0

while [ $# -gt 0 ]; do
  case "$1" in
    --image)   DEL_IMG=1; shift ;;
    --volumes) DEL_VOL=1; shift ;;
    --all)     DEL_IMG=1; DEL_VOL=1; shift ;;
    *) c_red "未知参数: $1"; exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"

if [ "$DEL_VOL" -eq 1 ]; then
  c_yel "!! 这将删除 MySQL/Redis 数据卷，数据库内容会全部丢失"
  read -p "确认输入 yes： " ans
  if [ "$ans" != "yes" ]; then
    c_red "取消"
    exit 1
  fi
  c_cyn "==> docker compose down -v"
  docker compose down -v
else
  c_cyn "==> docker compose down"
  docker compose down
fi

if [ "$DEL_IMG" -eq 1 ]; then
  c_cyn "==> 删除镜像 $IMAGE_NAME"
  docker rmi -f "$IMAGE_NAME" 2>/dev/null || c_yel "镜像不存在或已被删除"
fi

c_grn "==> 完成"
