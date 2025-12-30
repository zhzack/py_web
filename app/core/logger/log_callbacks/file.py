# app/core/log_callbacks/file.py
import logging
import os
from logging.handlers import RotatingFileHandler
from .base import LogCallback


class FileCallback(LogCallback):
    def __init__(self, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, "app.log")

        self.logger = logging.getLogger("file-callback")
        self.logger.setLevel(logging.DEBUG)

        handler = RotatingFileHandler(
            path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
            )
        )
        self.logger.addHandler(handler)

    def handle(self, record):
        self.logger.handle(record)
