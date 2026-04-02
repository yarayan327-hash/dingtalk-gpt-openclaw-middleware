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

    def format_execution_plan(
        self,
        conversation_id: str,
        task: OrchestratedTask,
    ) -> DingTalkOutboundMessage:
        lines = [
            f"已识别模式：{task.mode.value}",
            f"project：{task.project}",
            f"target：{task.target or '-'}",
            f"task_name：{task.task_name}",
            f"requires_approval：{task.requires_approval}",
            f"params：{task.params}",
            f"rationale：{task.rationale}",
            f"system_advice：{task.system_advice.value}",
            f"system_advice_reason：{task.system_advice_reason}",
            "",
            "当前说明：这条请求已被识别为需要 OpenClaw 出手的任务。",
        ]
        return DingTalkOutboundMessage(
            conversation_id=conversation_id,
            text="\n".join(lines),
        )

    def format_system_execution_result(
        self,
        conversation_id: str,
        task: OrchestratedTask,
        result: dict,
    ) -> DingTalkOutboundMessage:
        ok = result.get("ok", False)
        exit_code = result.get("exitCode")
        stdout = result.get("stdout", "") or ""
        stderr = result.get("stderr", "") or ""

        lines = [
            f"已执行：{task.params.get('command', '')}",
            f"状态：{'success' if ok else 'failed'}",
            f"exitCode：{exit_code}",
            "",
            "stdout:",
            stdout.strip() or "(empty)",
        ]

        if stderr.strip():
            lines += ["", "stderr:", stderr.strip()]

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