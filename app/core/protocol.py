from app.models.task import OrchestratedTask, TaskMode


ROUTER_SCHEMA: dict = {
    "name": "middleware_router",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "project": {"type": "string"},
            "mode": {
                "type": "string",
                "enum": [mode.value for mode in TaskMode],
            },
            "task_name": {"type": "string"},
            "user_intent": {"type": "string"},
            "requires_approval": {"type": "boolean"},
            "params": {
                "type": "object",
                "additionalProperties": True,
            },
            "rationale": {"type": "string"},
        },
        "required": [
            "project",
            "mode",
            "task_name",
            "user_intent",
            "requires_approval",
            "params",
            "rationale",
        ],
    },
}


def build_task_from_router_payload(payload: dict) -> OrchestratedTask:
    return OrchestratedTask(**payload)
