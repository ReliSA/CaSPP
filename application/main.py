"""
ASWI - Markdown Analyzer Application

A PyQt6 application for analyzing consistency of markdown files and checking link validity.
"""
import sys
from core.application import Application


def main():
    """Main entry point for the application."""
    try:
        app = Application()
        return app.run()
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())