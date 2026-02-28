"""
Custom exceptions for the application.

This module defines all custom exceptions used throughout the application
to provide better error handling and more specific error messages.
"""
from typing import Optional


class BaseAppException(Exception):
    """
    Base exception for all application-specific exceptions.
    
    Provides a common interface for all custom exceptions with
    optional error codes and user-friendly messages.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 user_message: Optional[str] = None):
        """
        Initialize base exception.
        
        Args:
            message: Technical error message for developers/logs
            error_code: Optional error code for categorization
            user_message: Optional user-friendly message for UI display
        """
        super().__init__(message)
        self.error_code = error_code
        self.user_message = user_message or message


# Git-related exceptions
class GitException(BaseAppException):
    """Base exception for git-related errors."""
    pass


class GitRepositoryNotFoundError(GitException):
    """Raised when no git repository is found."""
    
    def __init__(self, path: Optional[str] = None):
        message = f"No git repository found at: {path}" if path else "No git repository found"
        super().__init__(
            message=message,
            error_code="GIT_REPO_NOT_FOUND",
            user_message="Git repository not found. Make sure you're in a valid git repository."
        )


class GitLibraryNotAvailableError(GitException):
    """Raised when GitPython library is not available."""
    
    def __init__(self):
        super().__init__(
            message="GitPython library not available",
            error_code="GIT_LIB_UNAVAILABLE",
            user_message="Git functionality is not available. Please install GitPython library."
        )


class GitOperationError(GitException):
    """Raised when a git operation fails."""
    
    def __init__(self, operation: str, cause: Optional[Exception] = None):
        message = f"Git {operation} operation failed"
        if cause:
            message += f": {str(cause)}"
        
        super().__init__(
            message=message,
            error_code="GIT_OPERATION_FAILED",
            user_message=f"Git {operation} failed. Please check your repository status."
        )


class GitRemoteError(GitException):
    """Raised when remote operations fail."""
    
    def __init__(self, remote_name: str, operation: str, cause: Optional[Exception] = None):
        message = f"Remote '{remote_name}' {operation} failed"
        if cause:
            message += f": {str(cause)}"
            
        super().__init__(
            message=message,
            error_code="GIT_REMOTE_ERROR",
            user_message=f"Failed to {operation} from remote '{remote_name}'. Check network connection."
        )


class GitBranchError(GitException):
    """Raised when branch operations fail."""
    
    def __init__(self, branch_name: str, operation: str):
        super().__init__(
            message=f"Branch '{branch_name}' {operation} failed",
            error_code="GIT_BRANCH_ERROR",
            user_message=f"Branch operation failed for '{branch_name}'"
        )


class GitDirtyWorkingTreeError(GitException):
    """Raised when working tree has uncommitted changes."""
    
    def __init__(self, operation: str):
        super().__init__(
            message=f"Cannot {operation}: working tree has uncommitted changes",
            error_code="GIT_DIRTY_TREE",
            user_message=f"Cannot {operation}. Please commit or stash your changes first."
        )


# File-related exceptions
class FileException(BaseAppException):
    """Base exception for file-related errors."""
    pass


class FileNotFoundError(FileException):
    """Raised when a file is not found."""
    
    def __init__(self, file_path: str):
        super().__init__(
            message=f"File not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            user_message=f"The file '{file_path}' could not be found."
        )


class FileAccessError(FileException):
    """Raised when file access is denied or fails."""
    
    def __init__(self, file_path: str, operation: str, cause: Optional[Exception] = None):
        message = f"Failed to {operation} file: {file_path}"
        if cause:
            message += f" ({str(cause)})"
            
        super().__init__(
            message=message,
            error_code="FILE_ACCESS_ERROR",
            user_message=f"Cannot {operation} file '{file_path}'. Check file permissions."
        )


class InvalidFileFormatError(FileException):
    """Raised when file format is invalid."""
    
    def __init__(self, file_path: str, expected_format: str):
        super().__init__(
            message=f"Invalid file format for {file_path}. Expected: {expected_format}",
            error_code="INVALID_FILE_FORMAT",
            user_message=f"Invalid file format. Expected {expected_format} file."
        )


# Analysis-related exceptions
class AnalysisException(BaseAppException):
    """Base exception for analysis-related errors."""
    pass


class MarkdownParsingError(AnalysisException):
    """Raised when markdown parsing fails."""
    
    def __init__(self, file_path: str, cause: Optional[Exception] = None):
        message = f"Failed to parse markdown file: {file_path}"
        if cause:
            message += f" ({str(cause)})"
            
        super().__init__(
            message=message,
            error_code="MARKDOWN_PARSE_ERROR",
            user_message=f"Failed to analyze markdown file '{file_path}'"
        )


# Configuration exceptions
class ConfigurationException(BaseAppException):
    """Base exception for configuration-related errors."""
    pass


class InvalidConfigurationError(ConfigurationException):
    """Raised when configuration is invalid."""
    
    def __init__(self, setting: str, value: str):
        super().__init__(
            message=f"Invalid configuration for '{setting}': {value}",
            error_code="INVALID_CONFIG",
            user_message=f"Configuration error: invalid value for {setting}"
        )


# Validation exceptions
class ValidationException(BaseAppException):
    """Base exception for validation errors."""
    pass


class InvalidInputError(ValidationException):
    """Raised when input validation fails."""
    
    def __init__(self, parameter: str, value: str, reason: str):
        super().__init__(
            message=f"Invalid {parameter}: {value} ({reason})",
            error_code="INVALID_INPUT",
            user_message=f"Invalid {parameter}: {reason}"
        )


class EmptyInputError(ValidationException):
    """Raised when required input is empty."""
    
    def __init__(self, parameter: str):
        super().__init__(
            message=f"Required parameter '{parameter}' cannot be empty",
            error_code="EMPTY_INPUT",
            user_message=f"{parameter.title()} cannot be empty"
        )


# Threading exceptions
class ThreadException(BaseAppException):
    """Base exception for threading-related errors."""
    pass


class ThreadOperationError(ThreadException):
    """Raised when thread operations fail."""
    
    def __init__(self, operation: str, cause: Optional[Exception] = None):
        message = f"Thread {operation} failed"
        if cause:
            message += f": {str(cause)}"
            
        super().__init__(
            message=message,
            error_code="THREAD_ERROR",
            user_message=f"Background operation failed: {operation}"
        )


# UI exceptions  
class UIException(BaseAppException):
    """Base exception for UI-related errors."""
    pass


class WidgetInitializationError(UIException):
    """Raised when widget initialization fails."""
    
    def __init__(self, widget_name: str, cause: Optional[Exception] = None):
        message = f"Failed to initialize widget: {widget_name}"
        if cause:
            message += f" ({str(cause)})"
            
        super().__init__(
            message=message,
            error_code="WIDGET_INIT_ERROR",
            user_message=f"Failed to initialize {widget_name}"
        )
