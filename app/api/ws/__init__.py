from fastapi import APIRouter
from .device import router as device_router
from .client import router as client_router

ws_router = APIRouter()
ws_router.include_router(device_router, tags=["ws"])
ws_router.include_router(client_router, tags=["ws"])
