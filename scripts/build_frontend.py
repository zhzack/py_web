"""构建前端：vue-project/dist。

用法:
    python scripts/build_frontend.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _common import PROJECT_ROOT, cyn, grn, red, run  # noqa: E402


def main():
    web = PROJECT_ROOT / "vue-project"
    if not web.exists():
        red(f"前端目录不存在: {web}")
        sys.exit(1)

    npm = shutil.which("npm")
    if not npm:
        red("npm 未安装或不在 PATH")
        sys.exit(1)

    if not (web / "node_modules").exists():
        cyn("==> 首次构建，安装依赖 (npm ci)")
        rc = run([npm, "ci", "--no-audit", "--no-fund"], cwd=web, check=False)
        if rc != 0:
            run([npm, "install", "--no-audit", "--no-fund"], cwd=web)

    cyn("==> 编译 Vue 生产包")
    run([npm, "run", "build"], cwd=web)

    grn(f"==> 完成: {web / 'dist'}")


if __name__ == "__main__":
    main()
