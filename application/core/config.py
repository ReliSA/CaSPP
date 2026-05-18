"""
Configuration settings for the application.
"""
# standard library imports
import logging
from pathlib import Path

# local imports
from utils.constants import AppConstants, UIConstants

logger = logging.getLogger(__name__)


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
        """Find the Git repository root dynamically.

        Returns:
            The resolved path.
        """
        path = Path.cwd()

        for parent in [path] + list(path.parents):
            if (parent / ".git").exists():
                logger.debug("Resolved repository root: %s", parent)
                return parent

        logger.error("No .git directory found when walking up from %s", path)
        raise RuntimeError("No Git repository found.")

    @classmethod
    def get_default_markdown_path(cls) -> str:
        """Get the default markdown file path.

        Returns:
            The string result.
        """
        return str(cls.get_base_path() / cls.DEFAULT_MARKDOWN_FILE)
