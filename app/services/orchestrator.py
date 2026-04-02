from app.models.dingtalk import DingTalkInboundMessage, DingTalkOutboundMessage
from app.models.task import TaskMode
from app.services.dingtalk_service import DingTalkService
from app.services.openai_router import OpenAIRouterService
from app.services.openclaw_client import OpenClawClient
from app.services.task_store import TaskStore


class OrchestratorService:
    def __init__(self) -> None:
        self.router = OpenAIRouterService()
        self.dingtalk = DingTalkService()
        self.store = TaskStore()
        self.openclaw = OpenClawClient()

    def handle_message(self, inbound: DingTalkInboundMessage) -> DingTalkOutboundMessage:
        try:
            task = self.router.route(inbound.text)
            self.store.save_task(task)

            if task.mode == TaskMode.reply:
                answer = self.router.answer(inbound.text, task)
                return self.dingtalk.format_reply_result(
                    inbound.conversation_id,
                    answer,
                    task,
                )

            if task.mode == TaskMode.system:
                result = self.openclaw.system_run(task)
                return self.dingtalk.format_execution_result(
                    inbound.conversation_id,
                    task,
                    result,
                )

            if task.mode == TaskMode.skill:
                if task.target == "find-skills":
                    result = self.openclaw.find_skills(task)
                else:
                    result = self.openclaw.skill_run(task)

                return self.dingtalk.format_execution_result(
                    inbound.conversation_id,
                    task,
                    result,
                )

            if task.mode == TaskMode.agent:
                result = self.openclaw.agent_run(task)
                return self.dingtalk.format_execution_result(
                    inbound.conversation_id,
                    task,
                    result,
                )

            return self.dingtalk.format_failure(
                inbound.conversation_id,
                f"unsupported mode: {task.mode.value}",
            )

        except Exception as exc:
            return self.dingtalk.format_failure(
                inbound.conversation_id,
                str(exc),
            )
