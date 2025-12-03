import logging
import subprocess

logger = logging.getLogger(__name__)


def _run_cmd(cmd: list[str], dry_run: bool):
    if dry_run:
        logger.info("[dry-run] firewall cmd: %s", " ".join(cmd))
        return {"dry_run": True, "cmd": cmd}
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"dry_run": False, "cmd": cmd, "stdout": res.stdout}
    except subprocess.CalledProcessError as e:
        logger.error("firewall command failed: %s", e.stderr)
        return {"dry_run": False, "cmd": cmd, "stderr": e.stderr, "returncode": e.returncode}


def block_ip(ip: str, dry_run: bool = True):
    # iptables: drop input from given IP
    cmd = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
    return _run_cmd(cmd, dry_run)


def throttle_ip(ip: str, dry_run: bool = True):
    # rate-limit packets from IP
    cmd = ["iptables", "-A", "INPUT", "-s", ip, "-m", "limit", "--limit", "5/minute", "-j", "ACCEPT"]
    return _run_cmd(cmd, dry_run)


def quarantine_ip(ip: str, dry_run: bool = True):
    """
    Stronger isolation: drop both inbound and outbound traffic for the IP.
    """
    cmds = [
        ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
        ["iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"],
    ]
    results = []
    for cmd in cmds:
        results.append(_run_cmd(cmd, dry_run))
    return results
