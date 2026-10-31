# This file holds the application logger.

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FOLDER = Path(__file__).resolve().parents[2] / "logs"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
MAX_LOG_SIZE = 1024 * 1024
BACKUP_COUNT = 3


def get_logger(name):
    """Return a configured application logger."""
    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if getattr(logger, "_aab_configured", False):
        return logger

    formatter = logging.Formatter(LOG_FORMAT)

    app_handler = RotatingFileHandler(
        LOG_FOLDER / "app.log",
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        LOG_FOLDER / "error.log",
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    logger._aab_configured = True

    return logger
