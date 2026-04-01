from app.models.task import OrchestratedTask, TaskMode


ROUTER_SCHEMA: dict = {
    "name": "middleware_router",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "project": {
                "type": "string"
            },
            "mode": {
                "type": "string",
                "enum": [mode.value for mode in TaskMode],
            },
            "task_name": {
                "type": "string"
            },
            "user_intent": {
                "type": "string"
            },
            "requires_approval": {
                "type": "boolean"
            },
            "params": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "topic": {"type": ["string", "null"]},
                    "output_format": {"type": ["string", "null"]},
                    "language": {"type": ["string", "null"]},
                    "audience": {"type": ["string", "null"]},
                    "deliverable_type": {"type": ["string", "null"]},
                    "scope": {"type": ["string", "null"]}
                },
                "required": [
                    "topic",
                    "output_format",
                    "language",
                    "audience",
                    "deliverable_type",
                    "scope"
                ]
            },
            "rationale": {
                "type": "string"
            },
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
