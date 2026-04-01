from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import setup_logging

logger = setup_logging()
app = FastAPI(title="DingTalk GPT OpenClaw Middleware")
app.include_router(router)
