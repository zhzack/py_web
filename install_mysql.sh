#!/usr/bin/env bash

set -e

# ===== 配置区 =====

MYSQL_ROOT_PASSWORD="RootStrongPassword"
DEV_USER="dev"
DEV_PASSWORD="DevPassword"
BIND_ADDRESS="0.0.0.0"  # 0.0.0.0 表示所有网络可访问

# ===================

echo "==> Updating system"
sudo apt update

echo "==> Installing MySQL"
sudo apt install -y mysql-server

echo "==> Ensuring MySQL service is stopped before configuration"
sudo service mysql stop || true

# WSL / Linux 容器兼容：确保 socket 目录存在
echo "==> Ensuring /var/run/mysqld exists"
sudo mkdir -p /var/run/mysqld
sudo chown mysql:mysql /var/run/mysqld

# ===== 检查 root 是否能正常登录 =====
ROOT_CAN_LOGIN=$(sudo mysql -e "SELECT 1;" 2>/dev/null && echo "yes" || echo "no")

if [ "$ROOT_CAN_LOGIN" != "yes" ]; then
    echo "==> Root cannot login normally, starting MySQL in skip-grant-tables mode"
    sudo mysqld_safe --skip-grant-tables --skip-networking &
    SLEEP_COUNT=0
    until mysql -e "SELECT 1;" >/dev/null 2>&1; do
        sleep 1
        SLEEP_COUNT=$((SLEEP_COUNT+1))
        if [ $SLEEP_COUNT -gt 10 ]; then
            echo "Error: MySQL skip-grant-tables did not start"
            exit 1
        fi
    done

    # ===== 修改部分：移除了 EXIT; =====
    echo "==> Resetting root password using ALTER USER"
    mysql <<EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';
FLUSH PRIVILEGES;
EOF
    # =======================================

    echo "==> Stopping skip-grant-tables instance"
    sudo pkill mysqld
fi

# ===== 正常启动 MySQL =====
echo "==> Starting MySQL service"
sudo service mysql start

# ===== 配置 bind-address =====
echo "==> Configuring bind-address to $BIND_ADDRESS"
sudo sed -i "s/^bind-address.*/bind-address = ${BIND_ADDRESS}/" \
    /etc/mysql/mysql.conf.d/mysqld.cnf
sudo service mysql restart

# ===== 创建开发用户 =====
echo "==> Creating dev user"
sudo mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" <<EOF
CREATE USER IF NOT EXISTS '${DEV_USER}'@'%' IDENTIFIED BY '${DEV_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${DEV_USER}'@'%';
FLUSH PRIVILEGES;
EOF

# ===== 显示用户信息 =====
echo "==> MySQL users:"
sudo mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "SELECT user, host, plugin FROM mysql.user;"

echo "==> MySQL installation & initialization complete"
echo "Root password: ${MYSQL_ROOT_PASSWORD}"
echo "Dev user: ${DEV_USER}, password: ${DEV_PASSWORD}"
