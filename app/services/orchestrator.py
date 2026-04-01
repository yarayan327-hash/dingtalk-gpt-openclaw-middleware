from app.models.dingtalk import DingTalkInboundMessage, DingTalkOutboundMessage
from app.models.task import TaskMode, TaskExecutionResult, TaskStatus
from app.services.dingtalk_service import DingTalkService
from app.services.openai_router import OpenAIRouterService
from app.services.openclaw_client import OpenClawClient
from app.services.task_store import TaskStore


class OrchestratorService:
    def __init__(self) -> None:
        self.router = OpenAIRouterService()
        self.openclaw = OpenClawClient()
        self.dingtalk = DingTalkService()
        self.store = TaskStore()

    def handle_message(self, inbound: DingTalkInboundMessage) -> DingTalkOutboundMessage:
        task = self.router.route(inbound.text)
        self.store.save_task(task)

        if task.mode in {TaskMode.chat, TaskMode.query, TaskMode.engineering, TaskMode.approval}:
            return self.dingtalk.format_chat_reply(inbound.conversation_id, task)

        result = self.openclaw.execute(task)
        self.store.save_result(result)
        return self.dingtalk.format_task_result(inbound.conversation_id, result)

    def simulate_task_result(self, task_id: str) -> TaskExecutionResult:
        return TaskExecutionResult(
            task_id=task_id,
            status=TaskStatus.done,
            summary="Simulated result",
            output_text="This is a simulated task result.",
            raw={"simulated": True},
        )
