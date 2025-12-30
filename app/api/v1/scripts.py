from fastapi import APIRouter
from fastapi import WebSocket, HTTPException
from uuid import uuid4
from pathlib import Path
from app.services.script_config import ScriptConfig
from app.services.script_runner import run_script_async
from app.services.log_bus import log_bus
from app.core.logger.logger import logger
router = APIRouter()

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "resource" / "scripts"
logger.info(f"SCRIPTS_DIR: {SCRIPTS_DIR}")  
# 列出脚本


@router.get("/list")
def list_scripts():
    return {"scripts": [f.name for f in SCRIPTS_DIR.glob("*") if f.is_file()]}

# 列出配置文件


@router.get("/configs")
def list_configs(script: str):
    cfg_dir = SCRIPTS_DIR / script
    if not cfg_dir.exists():
        return {"configs": []}
    return {"configs": [f.name for f in cfg_dir.glob("*.yaml")]}

# 获取参数


@router.get("/params")
def get_params(script: str, config: str):
    # 简化：默认参数
    return {"params": [{"name": "count", "default": 5}, {"name": "delay", "default": 1}]}

# 运行脚本


@router.post("/run")
def run_script(script: str, config_name: str, args: list[str] = []):
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        raise HTTPException(404, "Script not found")

    config = ScriptConfig(
        script_path=script_path,
        workdir=script_path.parent,
        interpreter=None,
        args=args,
        env={}
    )

    execution_id = str(uuid4())
    run_script_async(config, execution_id)
    return {"execution_id": execution_id}

# WebSocket 推送日志


@router.websocket("/ws/{execution_id}")
async def ws_logs(ws: WebSocket, execution_id: str):
    await ws.accept()
    async for line in log_bus.subscribe(execution_id):
        await ws.send_text(line)
