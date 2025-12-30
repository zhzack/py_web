import threading
import subprocess
from app.services.script_config import ScriptConfig
from app.services.log_bus import log_bus
import asyncio


def run_script_async(config: ScriptConfig, execution_id: str):
    """
    异步执行脚本，推送 stdout/stderr 到 log_bus
    """
    def target():
        cmd = []
        suffix = config.script_path.suffix.lower()

        if suffix == ".py":
            cmd = [config.interpreter or "python", str(config.script_path)]
        elif suffix == ".sh":
            cmd = [config.interpreter or "bash", str(config.script_path)]
        elif suffix in (".bat", ".cmd"):
            cmd = [str(config.script_path)]
        else:
            raise RuntimeError(f"Unsupported script type: {suffix}")

        if config.args:
            cmd.extend(config.args)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(config.workdir),
            env={**subprocess.os.environ, **config.env},
            text=True,
            bufsize=1,
        )

        # 实时推送日志
        for line in proc.stdout:
            asyncio.run(log_bus.publish(execution_id, line.rstrip()))
        proc.stdout.close()
        proc.wait()

    threading.Thread(target=target, daemon=True).start()
