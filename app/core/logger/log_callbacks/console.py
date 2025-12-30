# app/core/log_callbacks/console.py
import logging
import sys
from colorlog import ColoredFormatter
from .base import LogCallback


class ConsoleCallback(LogCallback):
    def __init__(self):
        self.logger = logging.getLogger("console-callback")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            ColoredFormatter(
                "%(log_color)s[%(levelname)s] %(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            )
        )
        self.logger.addHandler(handler)

    def handle(self, record):
        self.logger.handle(record)
