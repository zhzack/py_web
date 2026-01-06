#!/usr/bin/env bash
set -e

echo "==> Stopping MySQL service"
sudo service mysql stop || true

echo "==> Uninstalling MySQL packages"
sudo apt purge -y mysql-server mysql-client mysql-common mysql-server-core-* mysql-client-core-*

echo "==> Removing residual files"
sudo rm -rf /etc/mysql
sudo rm -rf /var/lib/mysql
sudo rm -rf /var/log/mysql
sudo rm -rf /var/run/mysqld

# echo "==> Cleaning up apt cache"
# sudo apt autoremove -y
# sudo apt autoclean -y

echo "==> MySQL has been completely removed from the system."
