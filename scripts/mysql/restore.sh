#!/bin/bash
set -e

# 自动定位项目根目录
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT="$SCRIPT_DIR/../.."
ENV_FILE="$PROJECT_ROOT/.env"

# 加载 .env 配置
source <(grep -v '^#' "$ENV_FILE" | sed 's/^/export /')

CONTAINER_NAME="py_web_mysql"

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法：./restore.sh 备份文件路径"
    echo "例：./restore.sh ../../backups/backup_20250908.sql"
    exit 1
fi

BACKUP_FILE="$1"

# 执行恢复
echo "🔹 正在恢复：$BACKUP_FILE"
cat "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" \
  mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB"

echo "✅ 恢复完成：$BACKUP_FILE"
