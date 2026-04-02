import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

NODE_ID = os.environ.get("OPENCLAW_NODE_ID", "")
BRIDGE_TOKEN = os.environ.get("OPENCLAW_BRIDGE_TOKEN", "")
DEFAULT_CWD = os.environ.get("OPENCLAW_DEFAULT_CWD", "/home/admin/.openclaw/workspace")
ALLOWED_ROOT = Path(DEFAULT_CWD).resolve()

SAFE_PREFIXES = {
    "pwd",
    "ls",
    "find",
    "cat",
    "head",
    "tail",
}

DENY_SNIPPETS = [
    " rm ",
    "rm -",
    " rm\n",
    "shutdown",
    "reboot",
    "mkfs",
    ":(){",
    "curl ",
    "wget ",
    "| sh",
    "| bash",
    "> /dev/",
]


class SystemRunRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    node_id: Optional[str] = None
    timeout_seconds: Optional[int] = 120


def normalize_cwd(raw_cwd: Optional[str]) -> str:
    if raw_cwd is None:
        return str(ALLOWED_ROOT)

    raw_cwd = raw_cwd.strip()
    if raw_cwd == "" or raw_cwd == ".":
        return str(ALLOWED_ROOT)

    candidate = Path(raw_cwd)
    if not candidate.is_absolute():
        candidate = ALLOWED_ROOT / candidate

    resolved = candidate.resolve()
    try:
        resolved.relative_to(ALLOWED_ROOT)
    except ValueError:
        raise HTTPException(status_code=400, detail="cwd out of allowed range")

    return str(resolved)


def validate_command(command: str) -> None:
    normalized = f" {command.strip()} "

    for snippet in DENY_SNIPPETS:
        if snippet in normalized:
            raise HTTPException(status_code=400, detail=f"dangerous command blocked: {snippet.strip()}")

    first_segment = command.strip().split("&&")[0].strip()
    if not first_segment:
        raise HTTPException(status_code=400, detail="empty command")

    try:
        first_token = shlex.split(first_segment)[0]
    except Exception:
        raise HTTPException(status_code=400, detail="invalid command syntax")

    if first_token not in SAFE_PREFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"command not in allowlist: {first_token}",
        )


@app.get("/health")
def health():
    return {"ok": True, "status": "live", "allowed_root": str(ALLOWED_ROOT)}


@app.post("/system-run")
def system_run(
    payload: SystemRunRequest,
    authorization: Optional[str] = Header(default=None),
):
    expected = f"Bearer {BRIDGE_TOKEN}"
    if BRIDGE_TOKEN and authorization != expected:
        raise HTTPException(status_code=401, detail="unauthorized")

    node_id = payload.node_id or NODE_ID
    if not node_id:
        raise HTTPException(status_code=400, detail="missing node_id")

    command = payload.command.strip()
    validate_command(command)
    cwd = normalize_cwd(payload.cwd)

    try:
        proc = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            timeout=payload.timeout_seconds or 120,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "success": False,
            "timedOut": True,
            "exitCode": None,
            "stdout": "",
            "stderr": "timeout",
            "command": command,
            "cwd": cwd,
            "node_id": node_id,
        }

    return {
        "ok": proc.returncode == 0,
        "success": proc.returncode == 0,
        "timedOut": False,
        "exitCode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": command,
        "cwd": cwd,
        "node_id": node_id,
    }