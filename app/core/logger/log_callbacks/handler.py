# app/core/log_callbacks/handler.py
import logging


class CallbackHandler(logging.Handler):
    def __init__(self, callbacks):
        super().__init__()
        self.callbacks = callbacks

    def emit(self, record):
        for cb in self.callbacks:
            try:
                cb.handle(record)
            except Exception:
                # 日志失败 ≠ 业务失败
                pass
