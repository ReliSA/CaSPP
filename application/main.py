"""
ASWI - Markdown Analyzer Application

A PyQt6 application for analyzing consistency of markdown files and checking link validity.
"""
import sys
import logging
from core.application import Application


def setup_logging():
    """Set up application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for the application."""
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
        print(f"Error starting application: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())