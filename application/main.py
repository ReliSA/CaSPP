"""
ASWI - Markdown Analyzer Application

A PyQt6 application for analyzing consistency of markdown files and checking link validity.
"""

# standard library imports
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# local imports
from core.application import Application
from utils.constants import AppConstants, LogConstants


def setup_logging() -> None:
    """Configure root logging: rotating file next to the repo and stdout."""
    log_path = Path(__file__).resolve().parent.parent / AppConstants.DEFAULT_LOG_FILE
    level_name = LogConstants.DEFAULT_LOG_LEVEL.upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = logging.Formatter(LogConstants.LOG_FORMAT, LogConstants.LOG_DATE_FORMAT)
    max_bytes = LogConstants.MAX_LOG_FILE_SIZE_MB * 1024 * 1024

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=LogConstants.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root.addHandler(file_handler)

    logging.getLogger(__name__).info(
        "Logging to %s (level=%s)",
        log_path,
        level_name,
    )


def main() -> int:
    """Main entry point for the application.

    Returns:
        The return value.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Markdown Analyzer application")
        app = Application()
        result = app.run()
        logger.info("Application finished")
        return result
    except Exception as e:
        logger.exception("Error starting application")
        return 1


if __name__ == "__main__":
    sys.exit(main())