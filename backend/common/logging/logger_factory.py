import logging

from .logging_config import configure_logging


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
