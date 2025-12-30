# app/core/log_callbacks/alert.py
from .base import LogCallback


class AlertCallback(LogCallback):
    def handle(self, record):
        if record.levelname in ("ERROR", "CRITICAL"):
            print("🚨 ALERT:", record.getMessage())
