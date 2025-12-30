# app/core/log_callbacks/http.py
from fastapi import Request
from .base import LogCallback


class HttpCallback(LogCallback):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def handle(self, record):
        try:
            Request.post(
                self.endpoint,
                json={
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                },
                timeout=1,
            )
        except Exception:
            pass
