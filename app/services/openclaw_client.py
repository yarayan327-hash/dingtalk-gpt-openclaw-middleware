from __future__ import annotations

import json
import shlex

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
            f"printf '%s' {json.dumps(json.dumps(payload))} > /tmp/skill_input.json && "
            f"echo '[SIMULATED SKILL RUN]' && "
            f"echo 'skill={skill_name}' && "
            f"cat /tmp/skill_input.json"
        )
        return self._post_bridge(command=command, cwd=".")

    def _agent_fallback(self, task: OrchestratedTask, requested_agent: str, reason: str) -> dict:
        payload = {
            "task_name": task.task_name,
            "user_intent": task.user_intent,
            "params": task.params,
        }

        command = (
            f"printf '%s' {json.dumps(json.dumps(payload))} > /tmp/agent_input.json && "
            f"echo '[SIMULATED AGENT FALLBACK]' && "
            f"echo 'requested_agent={requested_agent}' && "
            f"echo 'actual_agent=main' && "
            f"echo 'reason={reason}' && "
            f"cat /tmp/agent_input.json"
        )
        result = self._post_bridge(command=command, cwd=".")
        result["requested_agent"] = requested_agent
        result["actual_agent"] = "main"
        result["fallback"] = True
        result["fallback_reason"] = reason
        return result

    def agent_run(self, task: OrchestratedTask) -> dict:
        requested_agent = task.target or task.params.get("agent_name", "") or "main"
        actual_agent = "main"

        message = task.user_intent.strip() or task.task_name
        quoted_agent = shlex.quote(actual_agent)
        quoted_message = shlex.quote(message)

        command = (
            f"openclaw agent "
            f"--agent {quoted_agent} "
            f"--message {quoted_message} "
            f"--thinking low "
            f"--timeout 90 "
            f"--json"
        )

        try:
            result = self._post_bridge(command=command, cwd=".")
            result["requested_agent"] = requested_agent
            result["actual_agent"] = actual_agent
            result["fallback"] = False
            return result
        except Exception as exc:
            return self._agent_fallback(
                task=task,
                requested_agent=requested_agent,
                reason=str(exc),
            )
