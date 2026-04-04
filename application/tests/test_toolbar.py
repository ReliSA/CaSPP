#!/usr/bin/env python3
"""
Test script to verify the toolbar functionality.
"""
import sys
import os
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from core.application import Application

def main():
    """Test the application with the new toolbar."""
    try:
        print("Starting Markdown Analyzer with Toolbar...")
        app = Application()
        return app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
