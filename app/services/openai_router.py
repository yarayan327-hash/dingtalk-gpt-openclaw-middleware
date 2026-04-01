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
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "router_system_prompt.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def route(self, text: str) -> OrchestratedTask:
        response = self.client.responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.openai_reasoning_effort},
            instructions=self.system_prompt,
            input=text,
            text={
                "format": {
                    "type": "json_schema",
                    "name": ROUTER_SCHEMA["name"],
                    "strict": ROUTER_SCHEMA["strict"],
                    "schema": ROUTER_SCHEMA["schema"],
                }
            },
        )
        payload = json.loads(response.output_text)
        return build_task_from_router_payload(payload)
