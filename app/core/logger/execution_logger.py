# app/core/execution_logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def create_execution_logger(execution_id: str):
    """
    为一次脚本执行创建独立 logger
    """
    log_dir = "logs/executions"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{execution_id}.log")

    logger_name = f"execution.{execution_id}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # 防止重复 handler
    if logger.handlers:
        return logger

    handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 是否向上传播到 app logger（可选）
    logger.propagate = False

    return logger
