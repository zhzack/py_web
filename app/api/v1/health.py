from fastapi import APIRouter
from app.services.ping_service import *
from app.core.logger.logger import logger
from app.core.templates import LOG_DIR


from uuid import uuid4
from app.core.logger.execution_logger import create_execution_logger

router = APIRouter()


@router.get("")
def health_check():
    return ping()


@router.get("/ping")
def health_check():
    return ping2()


@router.get("/run-script")
async def run_script():
    execution_id = f"exec_{uuid4().hex[:8]}"
    exec_logger = create_execution_logger(execution_id)

    exec_logger.info("脚本开始执行")

    try:
        exec_logger.info("步骤 1：准备环境")
        exec_logger.info("步骤 2：执行脚本逻辑")
        exec_logger.info("步骤 3：清理资源")
        exec_logger.info("脚本执行成功")
        status = "success"
    except Exception as e:
        exec_logger.exception("脚本执行失败")
        status = "failed"
    logger.info(f"脚本执行完成，ID：{execution_id}，状态：{status}")
    #  f"LOG_DIR/{execution_id}.log"
    logger.info(f"日志文件位置：{LOG_DIR}/{execution_id}.log")
    return {
        "execution_id": execution_id,
        "status": status,
        "log_file": f"{LOG_DIR}/{execution_id}.log",
    }



