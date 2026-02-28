"""
Configuration settings for the application.
"""
import os
from pathlib import Path

class Config:
    """Application configuration."""
    
    # Application settings
    APP_NAME = "Markdown Analyzer"
    VERSION = "1.0.0"
    
    # Window settings
    WINDOW_MIN_WIDTH = 500
    WINDOW_MIN_HEIGHT = 500
    WINDOW_DEFAULT_WIDTH = 800
    WINDOW_DEFAULT_HEIGHT = 600
    
    # File settings
    DEFAULT_MARKDOWN_FILE = "README.md"
    
    # UI settings
    ANALYSIS_PANEL_MAX_HEIGHT = 200
    
    @classmethod
    def get_base_path(cls) -> Path:
        """Get the base path of the project (parent of application directory)."""
        return Path(__file__).parent.parent.parent
    
    @classmethod
    def get_default_markdown_path(cls) -> str:
        """Get the default markdown file path."""
        return str(cls.get_base_path() / cls.DEFAULT_MARKDOWN_FILE)
