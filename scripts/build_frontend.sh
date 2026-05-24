#!/usr/bin/env bash
# 构建前端（vue-project）
# 用法: ./scripts/build_frontend.sh
set -euo pipefail
source "$(dirname "$0")/_common.sh"

cd "$PROJECT_ROOT/vue-project"

if [ ! -d node_modules ]; then
  c_cyn "==> 首次构建，安装依赖 npm ci"
  npm ci --no-audit --no-fund || npm install --no-audit --no-fund
fi

c_cyn "==> 编译 Vue 生产包"
npm run build

c_grn "==> 完成: $(realpath dist 2>/dev/null || pwd)/dist"
