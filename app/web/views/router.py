from fastapi import APIRouter
from app.web.views.home import router as home_router
from app.web.views.scripts import router as scripts_router

web_router = APIRouter()
web_router.include_router(home_router)
web_router.include_router(scripts_router, tags=["scripts"])
