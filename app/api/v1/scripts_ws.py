from fastapi import WebSocket, APIRouter
from app.services.log_bus import log_bus

router = APIRouter()


@router.websocket("/ws/{execution_id}")
async def script_logs(ws: WebSocket, execution_id: str):
    await ws.accept()
    async for line in log_bus.subscribe(execution_id):
        await ws.send_text(line)
