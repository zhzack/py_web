#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT="$SCRIPT_DIR/../.."
ENV_FILE="$PROJECT_ROOT/.env"

source <(grep -v '^#' "$ENV_FILE" | sed 's/^/export /')
CONTAINER_NAME="py_web_mysql"

SCHEMA_SAVE="$PROJECT_ROOT/deploy/sql/init_schema.sql"

echo "🔹 导出数据库表结构，不含数据"
docker exec "$CONTAINER_NAME" \
mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" \
-d --add-drop-database --add-drop-table "$MYSQL_DB" > "$SCHEMA_SAVE"

echo "✅ 表结构已保存至：$SCHEMA_SAVE"