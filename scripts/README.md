# scripts/

项目常用脚本，sh 和 py 两套等价实现。

> sh 在 Git Bash / WSL / Linux / macOS 通用；py 用纯标准库，跨平台。

## 一览表

| 场景 | shell | python | 说明 |
|---|---|---|---|
| 构建前端 | `./scripts/build_frontend.sh` | `python scripts/build_frontend.py` | `vue-project/dist` 产物 |
| 本地起后端 | `./scripts/start_backend.sh` | `python scripts/start_backend.py` | uvicorn + --reload，启动前查端口 |
| 构建镜像 | `./scripts/build_image.sh` | `python scripts/build_image.py` | `docker compose build`，产出 `hid-gateway:latest` |
| 起服务 | `./scripts/start.sh` | `python scripts/start.py` | 检查 8000 → `compose up -d` → 等 healthy |
| 停服务 | `./scripts/stop.sh` | `python scripts/stop.py` | `compose stop` 或 `down` |
| 看日志 | `./scripts/logs.sh` | `python scripts/logs.py` | 默认跟随 app |
| 清理 | `./scripts/clean.sh` | `python scripts/clean.py` | down / 删镜像 / 删数据卷 |

## 常用参数

### start_backend / start_backend.py
```bash
./scripts/start_backend.sh             # 端口被占就报错退出
./scripts/start_backend.sh --kill      # 端口被占就杀掉占用进程
./scripts/start_backend.sh --port 8001
./scripts/start_backend.sh --no-reload
```

### start.sh / start.py
```bash
./scripts/start.sh           # compose up -d
./scripts/start.sh --kill    # 占用 8000 的本机进程直接杀
./scripts/start.sh --build   # 起前先 build
```

### stop.sh / stop.py
```bash
./scripts/stop.sh            # 停所有服务
./scripts/stop.sh --app      # 只停 app
./scripts/stop.sh --rm       # 删容器（保留卷）
```

### build_image.sh / build_image.py
```bash
./scripts/build_image.sh
./scripts/build_image.sh --no-cache
./scripts/build_image.sh --tag v1.0    # 同时打 hid-gateway:v1.0
```

### logs.sh / logs.py
```bash
./scripts/logs.sh             # 跟随 app
./scripts/logs.sh --all       # 跟随 mysql + redis + app
./scripts/logs.sh --tail 200  # 不 follow，只看 200 行
```

### clean.sh / clean.py
```bash
./scripts/clean.sh             # 停 + 删容器
./scripts/clean.sh --image     # + 删 hid-gateway:latest 镜像
./scripts/clean.sh --volumes   # + 删数据卷（数据库内容丢失！）
./scripts/clean.sh --all       # 容器 + 镜像 + 数据卷
```

## 环境变量

| 变量 | 默认 | 含义 |
|---|---|---|
| `APP_PORT` | `8000` | 后端端口 |
| `COMPOSE_SERVICE` | `app` | compose 中的服务名 |
| `IMAGE_NAME` | `hid-gateway:latest` | 镜像 tag |

## 典型流程

**首次启动：**
```bash
./scripts/build_image.sh
./scripts/start.sh
# 浏览器打开 http://127.0.0.1:8000/
```

**改代码后：**
```bash
./scripts/stop.sh --app
./scripts/build_image.sh        # 后端 / 前端代码改了
./scripts/start.sh
```

**本地纯 python 调试（不走 docker）：**
```bash
docker compose up -d mysql redis   # 只起数据库
./scripts/start_backend.sh --kill  # 本机跑 uvicorn
```

**完全清空，从零再来：**
```bash
./scripts/clean.sh --all
```
