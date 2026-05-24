from fastapi import APIRouter
from .vehicles import router as vehicles_router
from .actions import router as actions_router

router = APIRouter()
router.include_router(vehicles_router, prefix="/vehicles", tags=["v2-vehicles"])
router.include_router(actions_router, tags=["v2-actions"])
