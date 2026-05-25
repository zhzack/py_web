#!/bin/bash
set -e

# 自动定位项目根目录（脚本在 scripts/mysql，向上两级）
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT="$SCRIPT_DIR/../.."
ENV_FILE="$PROJECT_ROOT/.env"

# 加载 .env 配置
source <(grep -v '^#' "$ENV_FILE" | sed 's/^/export /')

# 容器名
CONTAINER_NAME="py_web_mysql"

# 备份目录（项目根目录下的 backups）
BACKUP_DIR="$PROJECT_ROOT/backups"
mkdir -p "$BACKUP_DIR"

# 备份文件
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

# 执行备份
echo "🔹 正在备份数据库：$MYSQL_DB"
docker exec "$CONTAINER_NAME" \
  mysqldump --default-character-set=utf8mb4 --set-charset \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" > "$BACKUP_FILE"

echo "✅ 备份完成：$BACKUP_FILE"