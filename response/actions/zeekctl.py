import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def terminate_session(conn_id: str, dry_run: bool = True, zeekctl_path: str = "zeekctl"):
    """
    Terminate a Zeek session by conn_id using ZeekControl.
    Assumes a script on the Zeek side that reads conn_id and kills the session.
    """
    script_content = f"@load base/frameworks/notice\nlocal id = \"{conn_id}\";\n"
    script_file = Path("/tmp/terminate_session.zeek")
    script_file.write_text(script_content, encoding="utf-8")

    cmd = [zeekctl_path, "exec", "zeek", str(script_file)]
    if dry_run:
        logger.info("[dry-run] zeekctl cmd: %s", " ".join(cmd))
        return {"dry_run": True, "cmd": cmd, "script": str(script_file)}
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"dry_run": False, "cmd": cmd, "stdout": res.stdout}
    except subprocess.CalledProcessError as e:
        logger.error("zeekctl command failed: %s", e.stderr)
        return {"dry_run": False, "cmd": cmd, "stderr": e.stderr, "returncode": e.returncode}
