import json
import logging
from pathlib import Path
from datetime import datetime

from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    settings = get_settings()
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(settings.app_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


def append_json_log(filename: str, payload: dict) -> None:
    settings = get_settings()
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    full_path = Path(settings.log_dir) / filename
    with full_path.open("a", encoding="utf-8") as f:
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            **payload,
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
