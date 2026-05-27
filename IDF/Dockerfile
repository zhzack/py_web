# 基础镜像：官方 ESP-IDF v5.4 稳定版
FROM espressif/idf:release-v5.4

# 设置工作目录（容器内路径）
WORKDIR /project

# 赋予权限、设置环境（避免编译报错）
ENV HOME=/tmp
ENV PATH=/opt/esp/idf/tools:$PATH

# 默认编译命令
CMD ["idf.py", "build"]