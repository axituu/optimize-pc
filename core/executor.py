import subprocess
from typing import Callable, Optional


def run_ps(
    command: str,
    log_callback: Optional[Callable[[str], None]] = None,
    timeout: int = 90,
) -> dict:
    """
    Run a PowerShell command and return a result dict.

    Returns:
        {"success": bool, "stdout": str, "stderr": str, "returncode": int}
    """
    full_cmd = [
        "powershell",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        command,
    ]
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback(f"[TIMEOUT] Command timed out after {timeout}s")
        return {"success": False, "stdout": "", "stderr": "Timeout", "returncode": -1}
    except Exception as e:
        if log_callback:
            log_callback(f"[ERROR] Failed to launch PowerShell: {e}")
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    entry = {
        "success": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }

    if log_callback:
        status = "OK" if entry["success"] else "FAIL"
        short_cmd = command.strip().replace("\n", " ")[:100]
        log_callback(f"[{status}] {short_cmd}")
        if entry["stderr"] and not entry["success"]:
            log_callback(f"       {entry['stderr'][:150]}")

    return entry


def run_ps_query(command: str) -> str:
    """Silent query — returns stdout or empty string on failure."""
    result = run_ps(command)
    return result["stdout"] if result["success"] else ""
