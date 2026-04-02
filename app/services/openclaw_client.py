from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.models.task import OrchestratedTask


class OpenClawClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def system_run(self, task: OrchestratedTask) -> dict:
        command = task.params.get("command", "")
        cwd = task.params.get("path") or "/home/admin/.openclaw/workspace"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.openclaw_bridge_token}",
        }

        payload = {
            "command": command,
            "cwd": cwd,
        }

        with httpx.Client(timeout=180) as client:
            response = client.post(
                self.settings.openclaw_bridge_url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()
