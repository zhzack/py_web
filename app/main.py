from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from app.core.logger.logger import logger
from app.api.router import api_router
from app.web.views.router import web_router
from app.core.templates import *

app = FastAPI(title="Minimal Web Demo")


# 允许开发阶段 Vue 热更新访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# # 挂载静态资源
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# API
app.include_router(api_router, prefix="/api")


BASE_DIR = Path(__file__).resolve().parent.parent
logger.info(f"挂载前端资源目录：{BASE_DIR / 'vue-project/dist'}")
app.mount("/", StaticFiles(directory=BASE_DIR /
          "vue-project/dist", html=True), name="vue-project")

# 页面
# app.include_router(web_router)
