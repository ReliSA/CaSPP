"""
Application constants and configuration values.

This module contains all magic values and constants used throughout the application
to improve maintainability and reduce hardcoded values.
"""

# Git-related constants
class GitConstants:
    """Constants for git operations."""
    
    DEFAULT_REMOTE_NAME = "origin"
    DEFAULT_BRANCH_HEAD = "HEAD"
    MAX_COMMIT_MESSAGE_LENGTH = 500
    MIN_COMMIT_MESSAGE_LENGTH = 1
    
    # Git status change types
    CHANGE_TYPE_MODIFIED = 'M'
    CHANGE_TYPE_ADDED = 'A'
    CHANGE_TYPE_DELETED = 'D'
    
    # Default commit message
    DEFAULT_COMMIT_MESSAGE = "Update analysis"
    
    # Display constants
    LOG_MESSAGE_TRUNCATE = 50
    COMMIT_HASH_DISPLAY_LENGTH = 8


# File-related constants
class FileConstants:
    """Constants for file operations."""
    
    MARKDOWN_EXTENSIONS = ['.md', '.markdown']
    MAX_FILE_SIZE_MB = 50
    ENCODING_UTF8 = 'utf-8'
    
    # File dialog filters
    MARKDOWN_FILTER = "Markdown Files (*.md *.markdown);;All Files (*)"
    
    # Common markdown filenames
    COMMON_MARKDOWN_FILES = ["README.md", "index.md", "main.md", "introduction.md"]
    ALL_FILES_FILTER = "All Files (*)"

    TEMPLATES_PATH = "templates"


# UI-related constants
class UIConstants:
    """Constants for user interface."""
    
    # Window dimensions
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    DEFAULT_WINDOW_WIDTH = 1000
    DEFAULT_WINDOW_HEIGHT = 700
    
    # Panel dimensions
    ANALYSIS_PANEL_MAX_HEIGHT = 200
    ANALYSIS_PANEL_MIN_HEIGHT = 100
    
    # Message box limits
    MAX_ERROR_MESSAGE_LENGTH = 500
    
    # Timeouts (milliseconds)
    DEFAULT_TIMEOUT_MS = 30000
    PROGRESS_UPDATE_INTERVAL_MS = 100

    # Window title
    APP_WINDOW_TITLE = "Markdown Analyzer"

    # Top bar item names
    TOP_BAR_FILE_MENU_NAME = "File"
    TOP_BAR_GIT_MENU_NAME = "Git"

    # File menu action names
    OPEN_FILE_ACTION_NAME = "Open File"
    SAVE_FILE_ACTION_NAME = "Save File"
    OPEN_EXPLORER_ACTION_NAME = "Open Explorer"
    SHOW_LIVE_PREVIEW_ACTION_NAME = "Show Live Preview"
    SHOW_ANALYZER_OUTPUT_ACTION_NAME = "Show Analyzer Output"

    # Git menu action names
    STATUS_ACTION_NAME = "Status"
    FETCH_ACTION_NAME = "Fetch"
    PULL_ACTION_NAME = "Pull"
    PUSH_ACTION_NAME = "Push"

    # File menu action shortcuts
    OPEN_FILE_ACTION_SHORTCUT = "Ctrl+O"
    SAVE_FILE_ACTION_SHORTCUT = "Ctrl+S"
    OPEN_EXPLORER_ACTION_SHORTCUT = "Ctrl+E"
    SHOW_LIVE_PREVIEW_ACTION_SHORTCUT = "Ctrl+P"
    SHOW_ANALYZER_OUTPUT_ACTION_SHORTCUT = "Ctrl+A"

    # Git menu action shortcuts
    STATUS_ACTION_SHORTCUT = "Ctrl+Shift+S"
    FETCH_ACTION_SHORTCUT = "Ctrl+Shift+F"
    PULL_ACTION_SHORTCUT = "Ctrl+Shift+L"
    PUSH_ACTION_SHORTCUT = "Ctrl+Shift+P"

    # Markdown scene element constants
    EXPLORER_LABEL = "Explorer"
    OPEN_EXPLORER_BUTTON_LABEL = "Open Explorer"
    SAVE_CHANGES_BUTTON_LABEL = "Save Changes"
    LIVE_PREVIEW_CHECK_BOX_LABEL = "Live Preview"
    ANALYZER_CHECK_BOX_LABEL = "Analyzer"

    # Git scene element constants
    STATUS_BUTTON_LABEL = "Status"
    FETCH_BUTTON_LABEL = "Fetch"
    PULL_BUTTON_LABEL = "Pull"
    PUSH_BUTTON_LABEL = "Push"


class AssetsConstants:
    """Constants for asstest."""

    # Sidebar icon paths
    SIDEBAR_MARKDOWN_SCENE_ICON_PATH = "application/ui/assets/icons/LucideFolderOpen.svg"
    SIDEBAR_GIT_SCENE_ICON_PATH = "application/ui/assets/icons/LucideGithub.svg"

    # Markdonw scene icon paths
    CLOSE_FILE_EXPLORER_ICON_PATH = "application/ui/assets/icons/LucideX.svg"

    # Git scene icon paths
    STATUS_BUTTON_ICON_PATH = "application/ui/assets/icons/LucideBarChartBig.svg"
    FETCH_BUTTON_ICON_PATH = "application/ui/assets/icons/LucideRefreshCw.svg"
    PULL_BUTTON_ICON_PATH = "application/ui/assets/icons/LucideArrowDownToLine.svg"
    PUSH_BUTTON_ICON_PATH = "application/ui/assets/icons/LucideArrowUpFromLine.svg"


# Application constants
class AppConstants:
    """General application constants."""
    
    APP_NAME = "Markdown Analyzer"
    VERSION = "1.0.0"
    ORGANIZATION = "ASWI"
    
    # Default files
    DEFAULT_MARKDOWN_FILE = "README.md"
    DEFAULT_LOG_FILE = "app.log"
    
    # Analysis limits
    MAX_LINKS_TO_ANALYZE = 1000
    MAX_HEADING_DEPTH = 6


# Logging constants
class LogConstants:
    """Constants for logging configuration."""
    
    DEFAULT_LOG_LEVEL = "INFO"
    MAX_LOG_FILE_SIZE_MB = 10
    LOG_BACKUP_COUNT = 3
    
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Network constants
class NetworkConstants:
    """Constants for network operations."""
    
    DEFAULT_TIMEOUT_SECONDS = 30
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1


# Validation constants
class ValidationConstants:
    """Constants for input validation."""
    
    # Path validation
    MAX_PATH_LENGTH = 260  # Windows limitation
    INVALID_PATH_CHARS = '<>:"|?*'
    
    # Message validation
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 500
    
    # URL validation
    VALID_URL_SCHEMES = ['http', 'https', 'ftp', 'ftps']
    MAX_URL_LENGTH = 2048

class FileMatcherConstants:
    """Constants for FileMatcher"""
    CATALOGUE_PARENT_FOLDER = "catalogue"
    MIN_PATH_PARTS = 2
    PARENT_DIR_INDEX = -2

