from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.api.ws import ws_router
from app.core.config.config import settings
from app.core.logger.logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# CORS：从 .env 加载，回退到 vite/cra 默认端口
cors_origins = settings.BACKEND_CORS_ORIGINS or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API
app.include_router(api_router, prefix="/api")

# WebSocket（与 REST 同根，但不挂 /api 前缀，符合设计文档）
app.include_router(ws_router)

# Vue 构建产物挂载
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "vue-project" / "dist"
if FRONTEND_DIST.exists():
    logger.info(f"挂载前端资源目录：{FRONTEND_DIST}")
    # 仅挂载 assets/ 等静态资源；index.html 由 SPA fallback 处理
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="vue-assets",
    )

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(FRONTEND_DIST / "favicon.ico")

    # SPA fallback：所有非 /api、/ws 路径都返回 index.html
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str, request: Request):
        # 已被前面的路由匹配的不会进这里；只兜底前端 history 路径
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    logger.warning(f"前端构建目录不存在，跳过挂载：{FRONTEND_DIST}")


@app.on_event("startup")
async def on_startup():
    logger.info(
        f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} 启动"
        f" | DB={settings.MYSQL_DB} | Queue={settings.QUEUE_BACKEND}"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
