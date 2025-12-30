# app/core/log_config.py
LOG_PIPELINE = {
    "default": {
        "level": "INFO",
        "callbacks": ["console", "file"],
    },
    "error": {
        "level": "ERROR",
        "callbacks": ["file", "http", "alert"],
    },
    "debug": {
        "level": "DEBUG",
        "callbacks": ["console"],
    },
}
