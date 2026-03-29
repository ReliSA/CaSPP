"""
Application constants and configuration values.

This module contains all magic values and constants used throughout the application
to improve maintainability and reduce hardcoded values.
"""
import re
from typing import List, Set

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
    CATALOGUE_PATH = "catalogue"


# UI-related constants
class UIConstants:
    """Constants for user interface."""
    
    # Window dimensions
    MIN_WINDOW_WIDTH = 500
    MIN_WINDOW_HEIGHT = 500
    DEFAULT_WINDOW_WIDTH = 800
    DEFAULT_WINDOW_HEIGHT = 600
    
    # Panel dimensions
    ANALYSIS_PANEL_MAX_HEIGHT = 200
    ANALYSIS_PANEL_MIN_HEIGHT = 100
    
    # Message box limits
    MAX_ERROR_MESSAGE_LENGTH = 500
    
    # Timeouts (milliseconds)
    DEFAULT_TIMEOUT_MS = 30000
    PROGRESS_UPDATE_INTERVAL_MS = 100


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

class LoaderConstants:
    """Constants for template and document loading."""
    # Heading line:  ### Some text
    RE_HEADING = re.compile(r'^(#{1,6})\s+(.+)$')

    # Markdown link anywhere in a string:  [label](url)
    RE_LINK = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')

    # Italic placeholder wrapping the *whole* remaining text, or inline:  *Name*
    RE_ITALIC = re.compile(r'\*([^*]+)\*')

    # Optional marker in template headings:  *(optional)* or (optional)
    RE_OPTIONAL = re.compile(r'\s*\*?\(optional\)\*?', re.IGNORECASE)

    # H1 prefix before a colon:  "Category: …" or "Project Methodology: …"
    RE_H1_PREFIX = re.compile(r'^([A-Za-z][A-Za-z ]+?):\s*(.*)$')

    # Table separator row:  |---|---|
    RE_TABLE_SEP = re.compile(r'^\|[-:\s|]+\|$')

    # Bullet / unordered list item:  - … or * …
    RE_BULLET = re.compile(r'^[-*]\s+')

    # Parenthesised bullet prefix:  - (+) …  or  - (-) …
    RE_BULLET_PREFIX = re.compile(r'^[-*]\s+(\([^)]+\))')

    # Exact link-style list prefix:  - [Label](url): …
    RE_EXACT_LIST_PREFIX = re.compile(r'^[-*]\s+(\[[^\]]+\]\([^)]+\):)')

    # Horizontal rule:  ---  ___  ***  (optionally wrapped in asterisks in templates)
    RE_HR_TEMPLATE = re.compile(r'^\*?(---|___|\*\*\*)\*?$')
    RE_HR_DOCUMENT = re.compile(r'^(---|___|\*\*\*)$')

    # Footnote definition:  [^1]: …  (optionally wrapped in asterisks in templates)
    RE_FOOTNOTE_TEMPLATE = re.compile(r'^\*?\[\^[^\]]+\]:')
    RE_FOOTNOTE_DOCUMENT = re.compile(r'^\[\^[^\]]+\]:')

    # Image:  ![alt](url)
    RE_IMAGE = re.compile(r'^!\[')

    # Breadcrumb line guard — italic-only lines are template instructions, not breadcrumbs
    RE_ITALIC_ONLY = re.compile(r'^\*[^*].*[^*]\*$|^\*[^*]\*$')

    # Content-type string constants — single source of truth for the vocabulary
    # used in both ContentRules.expected_types and ContentInfo.found_types.
    CT_TEXT = 'text'
    CT_BULLET_LIST = 'bullet_list'
    CT_TABLE = 'table'
    CT_HORIZONTAL_RULE = 'horizontal_rule'
    CT_FOOTNOTE = 'footnote'
    CT_LINKS = 'links'
    CT_IMAGE = 'image'

    # Settings for alphabetical grouping
    ALPHABET_LABELS: List[str] = ["0-9"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    ALPHABET_SET: Set[str] = set(ALPHABET_LABELS)
    MIN_ALPHABET_RUN = 5

    # Minimum number of breadcrumb items to trigger breadcrumb analysis — avoids false positives from short lists of links
    BREADCRUMBS_MIN_LENGTH = 2

