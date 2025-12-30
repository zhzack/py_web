from pathlib import Path
from fastapi.templating import Jinja2Templates
# 项目根目录（py_web）
BASE_DIR = Path(__file__).resolve().parent.parent

# 静态资源
STATIC_DIR = BASE_DIR / "resource" / "static"
SCRIPT_DIR = BASE_DIR / "resource" / "script"
TEMPLATES_DIR = BASE_DIR / "templates"

# 日志目录
LOG_DIR = BASE_DIR.parent / "logs"
EXECUTION_LOG_DIR = LOG_DIR / "executions"

EXECUTION_LOG_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
