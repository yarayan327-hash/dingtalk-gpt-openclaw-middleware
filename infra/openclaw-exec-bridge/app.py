import os
import subprocess
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

NODE_ID = os.environ.get("OPENCLAW_NODE_ID", "")
BRIDGE_TOKEN = os.environ.get("OPENCLAW_BRIDGE_TOKEN", "")
DEFAULT_CWD = os.environ.get("OPENCLAW_DEFAULT_CWD", "/home/admin/.openclaw/workspace")


class SystemRunRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    node_id: Optional[str] = None
    timeout_seconds: Optional[int] = 120


@app.get("/health")
def health():
    return {"ok": True, "status": "live"}


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

    cwd = payload.cwd or DEFAULT_CWD

    try:
        proc = subprocess.run(
            payload.command,
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
        }

    return {
        "ok": proc.returncode == 0,
        "success": proc.returncode == 0,
        "timedOut": False,
        "exitCode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": payload.command,
        "cwd": cwd,
        "node_id": node_id,
    }
