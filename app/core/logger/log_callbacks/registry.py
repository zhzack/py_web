# app/core/log_callbacks/registry.py
from .console import ConsoleCallback
from .file import FileCallback
from .http import HttpCallback
from .alert import AlertCallback

CALLBACK_REGISTRY = {
    "console": ConsoleCallback(),
    "file": FileCallback(),
    "http": HttpCallback("http://127.0.0.1:9000/logs"),
    "alert": AlertCallback(),
}
