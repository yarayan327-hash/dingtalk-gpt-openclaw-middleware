from app.models.task import OrchestratedTask, SystemAdvice, TaskMode


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
            "target": {"type": "string"},
            "task_name": {"type": "string"},
            "user_intent": {"type": "string"},
            "requires_approval": {"type": "boolean"},
            "params": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "topic": {"type": ["string", "null"]},
                    "output_format": {"type": ["string", "null"]},
                    "language": {"type": ["string", "null"]},
                    "audience": {"type": ["string", "null"]},
                    "deliverable_type": {"type": ["string", "null"]},
                    "scope": {"type": ["string", "null"]},
                    "command": {"type": ["string", "null"]},
                    "path": {"type": ["string", "null"]},
                    "skill_name": {"type": ["string", "null"]},
                    "agent_name": {"type": ["string", "null"]},
                },
                "required": [
                    "topic",
                    "output_format",
                    "language",
                    "audience",
                    "deliverable_type",
                    "scope",
                    "command",
                    "path",
                    "skill_name",
                    "agent_name",
                ],
            },
            "rationale": {"type": "string"},
            "system_advice": {
                "type": "string",
                "enum": [advice.value for advice in SystemAdvice],
            },
            "system_advice_reason": {"type": "string"},
        },
        "required": [
            "project",
            "mode",
            "target",
            "task_name",
            "user_intent",
            "requires_approval",
            "params",
            "rationale",
            "system_advice",
            "system_advice_reason",
        ],
    },
}


def build_task_from_router_payload(payload: dict) -> OrchestratedTask:
    cleaned = {
        **payload,
        "params": {k: v for k, v in payload.get("params", {}).items() if v is not None},
    }
    return OrchestratedTask(**cleaned)
