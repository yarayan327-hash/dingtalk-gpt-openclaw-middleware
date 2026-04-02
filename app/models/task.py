from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskMode(str, Enum):
    reply = "reply"
    agent = "agent"
    skill = "skill"
    system = "system"


class SystemAdvice(str, Enum):
    none = "none"
    create_agent = "create_agent"
    create_skill = "create_skill"
    debug_existing_flow = "debug_existing_flow"


class TaskStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class OrchestratedTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    project: str = Field(default="general")
    mode: TaskMode
    target: str = Field(default="")
    task_name: str
    user_intent: str
    requires_approval: bool = False
    params: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(default="")
    system_advice: SystemAdvice = SystemAdvice.none
    system_advice_reason: str = Field(default="")


class TaskExecutionResult(BaseModel):
    task_id: str
    status: TaskStatus
    summary: str
    output_text: str | None = None
    artifact_path: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)