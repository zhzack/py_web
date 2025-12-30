# app/core/logger.py
import logging
from .log_callbacks.handler import CallbackHandler
from .log_callbacks.registry import CALLBACK_REGISTRY
from .log_config import LOG_PIPELINE

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

for conf in LOG_PIPELINE.values():
    callbacks = [CALLBACK_REGISTRY[name] for name in conf["callbacks"]]
    handler = CallbackHandler(callbacks)
    handler.setLevel(getattr(logging, conf["level"]))
    logger.addHandler(handler)
