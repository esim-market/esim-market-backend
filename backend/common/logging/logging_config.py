import logging
import logging.handlers
import os
import sys
from pathlib import Path


class MaxLevelFilter(logging.Filter):
    def __init__(self, maximum: int):
        super().__init__(); self.maximum = maximum

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.maximum


def configure_logging() -> None:
    root = logging.getLogger()
    if getattr(root, "_esim_market_configured", False): return
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s [pid=%(process)d] %(message)s")
    stdout = logging.StreamHandler(sys.stdout); stdout.setLevel(logging.DEBUG); stdout.addFilter(MaxLevelFilter(logging.WARNING)); stdout.setFormatter(formatter)
    stderr = logging.StreamHandler(sys.stderr); stderr.setLevel(logging.ERROR); stderr.setFormatter(formatter)
    root.setLevel(level); root.addHandler(stdout); root.addHandler(stderr)
    if os.getenv("LOG_FILE_ENABLED", "false").lower() in {"1", "true", "yes"}:
        path = Path(os.getenv("LOG_FILE_PATH", "/home/backend/logs/esim-market-backend.log"))
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(path, maxBytes=int(os.getenv("LOG_FILE_MAX_BYTES", "10485760")), backupCount=int(os.getenv("LOG_FILE_BACKUP_COUNT", "5")))
            file_handler.setFormatter(formatter); root.addHandler(file_handler)
        except OSError:
            logging.getLogger(__name__).warning("Optional file logging could not be initialized")
    root._esim_market_configured = True
