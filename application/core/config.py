"""
Configuration settings for the application.
"""
import os
from pathlib import Path
from .constants import AppConstants, UIConstants

class Config:
    """Application configuration."""
    
    # Application settings
    APP_NAME = AppConstants.APP_NAME
    VERSION = AppConstants.VERSION
    
    # Window settings
    WINDOW_MIN_WIDTH = UIConstants.MIN_WINDOW_WIDTH
    WINDOW_MIN_HEIGHT = UIConstants.MIN_WINDOW_HEIGHT
    WINDOW_DEFAULT_WIDTH = UIConstants.DEFAULT_WINDOW_WIDTH
    WINDOW_DEFAULT_HEIGHT = UIConstants.DEFAULT_WINDOW_HEIGHT
    
    # File settings
    DEFAULT_MARKDOWN_FILE = AppConstants.DEFAULT_MARKDOWN_FILE
    
    # UI settings
    ANALYSIS_PANEL_MAX_HEIGHT = UIConstants.ANALYSIS_PANEL_MAX_HEIGHT
    
    @classmethod
    def get_base_path(cls) -> Path:
        """Get the base path of the project (parent of application directory)."""
        return Path(__file__).parent.parent.parent
    
    @classmethod
    def get_default_markdown_path(cls) -> str:
        """Get the default markdown file path."""
        return str(cls.get_base_path() / cls.DEFAULT_MARKDOWN_FILE)
