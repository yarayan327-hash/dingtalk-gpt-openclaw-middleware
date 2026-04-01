from app.core.logging import append_json_log
from app.models.task import OrchestratedTask, TaskExecutionResult


class TaskStore:
    def save_task(self, task: OrchestratedTask) -> None:
        append_json_log("tasks.jsonl", task.model_dump())

    def save_result(self, result: TaskExecutionResult) -> None:
        append_json_log("results.jsonl", result.model_dump())
