from fastapi import APIRouter
from .dev_tools import router as dev_tools_router

router = APIRouter()
router.include_router(dev_tools_router, tags=["dev"])
