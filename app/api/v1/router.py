from fastapi import APIRouter
from .health import router as health_router
from .scripts import router as scripts_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(scripts_router, prefix="/scripts", tags=["scripts"])
