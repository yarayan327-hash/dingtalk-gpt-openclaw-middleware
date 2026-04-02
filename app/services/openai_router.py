from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from app.core.config import get_settings
from app.core.protocol import ROUTER_SCHEMA, build_task_from_router_payload
from app.models.task import OrchestratedTask


class OpenAIRouterService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def _load_router_prompt(self) -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "router_system_prompt.txt"
        return prompt_path.read_text(encoding="utf-8")

    def route(self, user_text: str) -> OrchestratedTask:
        system_prompt = self._load_router_prompt()

        response = self.client.responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.openai_reasoning_effort},
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": ROUTER_SCHEMA["name"],
                    "schema": ROUTER_SCHEMA["schema"],
                    "strict": ROUTER_SCHEMA["strict"],
                }
            },
        )

        raw_text = response.output_text
        payload = json.loads(raw_text)
        task = build_task_from_router_payload(payload)

        # Safety normalization layer

        if task.mode.value == "skill":
            # If GPT didn't specify a target for a skill-like task, default to capability discovery
            if not task.target:
                task.target = "find-skills"

        if task.mode.value == "agent":
            # agent mode can legitimately use a descriptive target name even if not yet provisioned
            if not task.target:
                task.target = "main"

        if task.mode.value == "system":
            task.params.setdefault("path", ".")
            task.params.setdefault("command", "pwd && ls -la")

        return task

    def answer(self, user_text: str, task: OrchestratedTask) -> str:
        response = self.client.responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.openai_reasoning_effort},
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are the reply brain for a DingTalk assistant. "
                        "Answer clearly, naturally, and helpfully. "
                        "Use concise Chinese when the user writes in Chinese."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )
        return response.output_text.strip()
