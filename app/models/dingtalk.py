from pydantic import BaseModel, Field


class DingTalkInboundMessage(BaseModel):
    conversation_id: str = Field(..., description="Conversation or chat identifier")
    sender_id: str = Field(..., description="Sender unique identifier")
    sender_name: str = Field(..., description="Sender display name")
    text: str = Field(..., description="Plain text message from DingTalk")


class DingTalkOutboundMessage(BaseModel):
    conversation_id: str
    text: str
