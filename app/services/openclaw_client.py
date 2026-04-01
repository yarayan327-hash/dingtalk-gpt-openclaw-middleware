from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.models.task import OrchestratedTask


class OpenClawClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _health_url(self) -> str:
        return f"{self.settings.openclaw_base_url.rstrip('/')}/health"

    def _execute_url(self) -> str:
        full_url = getattr(self.settings, "openclaw_execute_url", "") or ""
        if full_url.strip():
            return full_url.strip()
        return f"{self.settings.openclaw_base_url.rstrip('/')}/execute"

    def healthcheck(self) -> dict[str, Any]:
        with httpx.Client(timeout=self.settings.openclaw_timeout_seconds) as client:
            response = client.get(self._health_url())
            response.raise_for_status()
            try:
                return response.json()
            except Exception:
                return {"ok": True, "raw_text": response.text}

    def execute(self, task: OrchestratedTask) -> dict[str, Any]:
        payload = {
            "project": task.project,
            "mode": task.mode.value,
            "task_name": task.task_name,
            "user_intent": task.user_intent,
            "requires_approval": task.requires_approval,
            "params": task.params,
            "rationale": task.rationale,
        }

        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }

        if self.settings.openclaw_api_key:
            headers["Authorization"] = f"Bearer {self.settings.openclaw_api_key}"

        with httpx.Client(timeout=self.settings.openclaw_timeout_seconds) as client:
            response = client.post(
                self._execute_url(),
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

            try:
                return response.json()
            except Exception:
                return {
                    "ok": True,
                    "status_code": response.status_code,
                    "raw_text": response.text,
                }
