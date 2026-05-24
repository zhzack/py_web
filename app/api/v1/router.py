from fastapi import APIRouter
from .health import router as health_router
from .scripts import router as scripts_router
from .auth import router as auth_router
from .devices import router as devices_router
from .macros import router as macros_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(scripts_router, prefix="/scripts", tags=["scripts"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(devices_router, prefix="/devices", tags=["devices"])
router.include_router(macros_router, prefix="/macros", tags=["macros"])
