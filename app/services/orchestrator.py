cat > /Users/jin/Desktop/dingtalk-gpt-openclaw-middleware/app/services/dingtalk_service.py <<'PY'
from app.models.dingtalk import DingTalkOutboundMessage
from app.models.task import OrchestratedTask


class DingTalkService:
    def format_reply_result(
        self,
        conversation_id: str,
        answer_text: str,
        task: OrchestratedTask,
    ) -> DingTalkOutboundMessage:
        advice_block = ""
        if task.system_advice.value != "none":
            advice_block = (
                "\n\n---\n"
                f"系统建议：{task.system_advice.value}\n"
                f"原因：{task.system_advice_reason}"
            )

        return DingTalkOutboundMessage(
            conversation_id=conversation_id,
            text=f"{answer_text}{advice_block}",
        )

    def _truncate(self, text: str, limit: int = 3500) -> str:
        text = text.strip()
        if len(text) <= limit:
            return text
        return text[:limit] + "\n\n[内容已截断]"

    def format_execution_result(
        self,
        conversation_id: str,
        task: OrchestratedTask,
        result: dict,
    ) -> DingTalkOutboundMessage:
        ok = result.get("ok", False)
        exit_code = result.get("exitCode")
        stdout = (result.get("stdout", "") or "").strip()
        stderr = (result.get("stderr", "") or "").strip()

        title_map = {
            "system": "⚙️ System 执行结果",
            "skill": "🧩 Skill 执行结果",
            "agent": "🤖 Agent 执行结果",
        }
        title = title_map.get(task.mode.value, "执行结果")

        lines = [
            title,
            f"模式：{task.mode.value}",
            f"目标：{task.target or '-'}",
            f"任务：{task.task_name}",
            f"状态：{'success' if ok else 'failed'}",
            f"exitCode：{exit_code}",
        ]

        command = result.get("command")
        if command:
            lines += ["", f"执行命令：{command}"]

        if stdout:
            lines += ["", "输出：", self._truncate(stdout)]

        if stderr:
            lines += ["", "错误：", self._truncate(stderr, limit=1200)]

        if task.system_advice.value != "none":
            lines += [
                "",
                "---",
                f"系统建议：{task.system_advice.value}",
                f"原因：{task.system_advice_reason}",
            ]

        return DingTalkOutboundMessage(
            conversation_id=conversation_id,
            text="\n".join(lines),
        )

    def format_failure(
        self,
        conversation_id: str,
        message: str,
    ) -> DingTalkOutboundMessage:
        return DingTalkOutboundMessage(
            conversation_id=conversation_id,
            text=f"❌ 执行失败\n{message}",
        )
PY
