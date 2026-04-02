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

    def answer(self, user_text: str, task: OrchestratedTask) -> str:
        system_prompt = (
            "你是业务主脑。你的职责是直接完成 reply 模式任务。"
            "回答要清晰、具体、可执行。"
            "默认使用中文。"
            "不要输出你是如何路由的。"
        )

        context = {
            "project": task.project,
            "task_name": task.task_name,
            "user_intent": task.user_intent,
            "params": task.params,
            "system_advice": task.system_advice.value,
            "system_advice_reason": task.system_advice_reason,
        }

        response = self.client.responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.openai_reasoning_effort},
            instructions=system_prompt,
            input=(
                f"用户原始请求：{user_text}\n\n"
                f"路由上下文：{json.dumps(context, ensure_ascii=False)}\n\n"
                "请直接给出最终回复内容。"
            ),
        )
        return response.output_text.strip()