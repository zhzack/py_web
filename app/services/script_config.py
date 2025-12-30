from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Optional


class ScriptConfig(BaseModel):
    script_path: Path        # 脚本文件路径
    workdir: Path            # 脚本工作目录
    interpreter: Optional[str] = None  # python / bash 等
    args: List[str] = []     # 参数列表
    env: Dict[str, str] = {}  # 环境变量
