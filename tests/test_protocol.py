from app.core.protocol import build_task_from_router_payload
from app.models.task import TaskMode


def test_build_task_from_router_payload() -> None:
    payload = {
        "project": "mental_math",
        "mode": "task",
        "task_name": "research_competitors",
        "user_intent": "帮我做 mental math 的竞品调研，并生成一份报告",
        "requires_approval": False,
        "params": {"output_format": "markdown"},
        "rationale": "用户明确要求生成研究报告，属于可执行任务。",
    }

    task = build_task_from_router_payload(payload)

    assert task.project == "mental_math"
    assert task.mode == TaskMode.task
    assert task.task_name == "research_competitors"
    assert task.params["output_format"] == "markdown"
