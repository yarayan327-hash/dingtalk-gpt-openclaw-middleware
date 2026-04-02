cat > /Users/jin/Desktop/dingtalk-gpt-openclaw-middleware/app/services/openclaw_client.py <<'PY'
from __future__ import annotations

import json

import httpx

from app.core.config import get_settings
from app.models.task import OrchestratedTask


class OpenClawClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _post_bridge(self, command: str, cwd: str = ".") -> dict:
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

    def system_run(self, task: OrchestratedTask) -> dict:
        command = task.params.get("command", "")
        cwd = task.params.get("path") or "."
        return self._post_bridge(command=command, cwd=cwd)

    def skill_run(self, task: OrchestratedTask) -> dict:
        skill_name = task.target or task.params.get("skill_name", "")
        if not skill_name:
            raise ValueError("missing skill_name for skill mode")

        payload = {
            "task_name": task.task_name,
            "user_intent": task.user_intent,
            "params": task.params,
        }

        command = (
            f"cd /home/admin/.openclaw/workspace && "
            f"printf '%s' {json.dumps(json.dumps(payload))} > /tmp/skill_input.json && "
            f"echo '[SIMULATED SKILL RUN]' && "
            f"echo 'skill={skill_name}' && "
            f"cat /tmp/skill_input.json"
        )
        return self._post_bridge(command=command, cwd=".")

    def agent_run(self, task: OrchestratedTask) -> dict:
        agent_name = task.target or task.params.get("agent_name", "")
        if not agent_name:
            raise ValueError("missing agent_name for agent mode")

        payload = {
            "task_name": task.task_name,
            "user_intent": task.user_intent,
            "params": task.params,
        }

        command = (
            f"cd /home/admin/.openclaw/workspace && "
            f"printf '%s' {json.dumps(json.dumps(payload))} > /tmp/agent_input.json && "
            f"echo '[SIMULATED AGENT RUN]' && "
            f"echo 'agent={agent_name}' && "
            f"cat /tmp/agent_input.json"
        )
        return self._post_bridge(command=command, cwd=".")
PY
