from typing import Any

import httpx

from app.core.config import get_settings
from app.models.task import OrchestratedTask, TaskExecutionResult, TaskStatus


class OpenClawClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def execute(self, task: OrchestratedTask) -> TaskExecutionResult:
        """
        当前保留为统一执行出口。
        你可以在这里对接本地 OpenClaw 服务、阿里云上的服务，或未来的工作流网关。
        """
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.settings.openclaw_api_key:
            headers["Authorization"] = f"Bearer {self.settings.openclaw_api_key}"

        payload: dict[str, Any] = task.model_dump()

        try:
            with httpx.Client(timeout=self.settings.openclaw_timeout_seconds) as client:
                response = client.post(
                    f"{self.settings.openclaw_base_url.rstrip('/')}/execute",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            return TaskExecutionResult(
                task_id=task.task_id,
                status=TaskStatus.done,
                summary=data.get("summary", "OpenClaw execution completed."),
                output_text=data.get("output_text"),
                artifact_path=data.get("artifact_path"),
                raw=data,
            )
        except Exception as exc:  # noqa: BLE001
            return TaskExecutionResult(
                task_id=task.task_id,
                status=TaskStatus.failed,
                summary=f"OpenClaw execution failed: {exc}",
                raw={"error": str(exc), "fallback": True},
            )
