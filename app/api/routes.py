from fastapi import APIRouter

from app.models.dingtalk import DingTalkInboundMessage
from app.services.orchestrator import OrchestratorService

router = APIRouter()
orchestrator = OrchestratorService()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/api/v1/dingtalk/messages")
def receive_dingtalk_message(payload: DingTalkInboundMessage) -> dict:
    outbound = orchestrator.handle_message(payload)
    return outbound.model_dump()
