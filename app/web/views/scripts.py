from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.core.logger.logger import logger
from app.core.templates import templates

router = APIRouter()


BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPT_DIR = BASE_DIR / "resource" / "script"


ALLOWED_SUFFIX = {".py", ".sh", ".bat"}


@router.get("/scripts", response_class=HTMLResponse)
def list_scripts(request: Request):
    scripts = []

    if SCRIPT_DIR.exists():
        for p in SCRIPT_DIR.iterdir():
            if p.is_file() and p.suffix in ALLOWED_SUFFIX:
                scripts.append({
                    "name": p.name,
                    "suffix": p.suffix,
                })

    return templates.TemplateResponse(
        "scripts.html",
        {
            "request": request,
            "scripts": scripts,
        }
    )
