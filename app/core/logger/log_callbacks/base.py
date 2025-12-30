# app/core/log_callbacks/base.py
from abc import ABC, abstractmethod
from logging import LogRecord


class LogCallback(ABC):
    @abstractmethod
    def handle(self, record: LogRecord):
        pass
