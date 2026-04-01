from app.models.dingtalk import DingTalkOutboundMessage
from app.models.task import TaskExecutionResult, OrchestratedTask


class DingTalkService:
    def format_chat_reply(self, conversation_id: str, task: OrchestratedTask) -> DingTalkOutboundMessage:
        return DingTalkOutboundMessage(
            conversation_id=conversation_id,
            text=(
                f"已识别为 {task.mode.value} 模式。\n"
                f"project={task.project}\n"
                f"task_name={task.task_name}\n"
                f"params={task.params}"
            ),
        )

    def format_task_result(self, conversation_id: str, result: TaskExecutionResult) -> DingTalkOutboundMessage:
        lines = [
            f"任务状态：{result.status.value}",
            f"摘要：{result.summary}",
        ]
        if result.output_text:
            lines.append(f"输出：{result.output_text}")
        if result.artifact_path:
            lines.append(f"产物：{result.artifact_path}")
        return DingTalkOutboundMessage(conversation_id=conversation_id, text="\n".join(lines))
