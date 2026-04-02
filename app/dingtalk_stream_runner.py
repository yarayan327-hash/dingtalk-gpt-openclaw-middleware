import json
import logging
import os

from dingtalk_stream import AckMessage
import dingtalk_stream

from app.models.dingtalk import DingTalkInboundMessage
from app.services.orchestrator import OrchestratorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text(incoming_message) -> str:
    try:
        if incoming_message.text and incoming_message.text.content:
            return incoming_message.text.content.strip()
    except Exception:
        pass
    return ""


class ChatbotMessageHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self):
        super().__init__()
        self.orchestrator = OrchestratorService()

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        logger.info("received message: %s", callback.data)

        text = extract_text(incoming_message)
        if not text:
            return AckMessage.STATUS_OK, "OK"

        inbound = DingTalkInboundMessage(
            conversation_id=str(
                getattr(incoming_message, "conversation_id", None)
                or getattr(incoming_message, "conversationId", None)
                or "unknown"
            ),
            sender_id=str(
                getattr(incoming_message, "sender_staff_id", None)
                or getattr(incoming_message, "senderStaffId", None)
                or "unknown"
            ),
            sender_name=str(
                getattr(incoming_message, "sender_nick", None)
                or getattr(incoming_message, "senderNick", None)
                or "Unknown"
            ),
            text=text,
        )

        result = self.orchestrator.handle_message(inbound)
        reply_text = result.text

        self.reply_text(reply_text, incoming_message)
        return AckMessage.STATUS_OK, "OK"


def main():
    client_id = os.environ["DINGTALK_CLIENT_ID"]
    client_secret = os.environ["DINGTALK_CLIENT_SECRET"]

    credential = dingtalk_stream.Credential(client_id, client_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(
        dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
        ChatbotMessageHandler(),
    )
    client.start_forever()


if __name__ == "__main__":
    main()