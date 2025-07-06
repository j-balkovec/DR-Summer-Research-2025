# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: sets up a basic logger for console/file logging

# == sys path ==
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import logging
from logging.handlers import RotatingFileHandler

from pipeline.config.settings import (LOG_DIR, LOG_FILE, MAX_BYTES, BACKUP_COUNT)

def get_logger(name=__name__, file_logging=True) -> logging.Logger:
    # pre: None
    # post: returns a logger instance
    # desc: Sets up a logger with console and optional file logging

    # name: str -> instance fetched by name (new one), else static

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # to avoid double logging

    if not logger.handlers:

        # console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

        # file
        if file_logging:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            fh = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
            fh.setLevel(logging.DEBUG)
            fh_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            fh.setFormatter(fh_formatter)
            logger.addHandler(fh)

    return logger
