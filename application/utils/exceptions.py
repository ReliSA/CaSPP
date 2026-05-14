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
                 user_message: Optional[str] = None, title: str = "Application Error") -> None:
        """Initialize base exception.

        Args:
            message: Technical error message for developers/logs.
            error_code: Optional error code for categorization.
            user_message: Optional user-friendly message for UI display.
            title: Optional title for the UI popup dialog.
        """
        super().__init__(message)
        self.error_code = error_code
        self.user_message = user_message or message
        self.title = title


# Git-related exceptions
class GitException(BaseAppException):
    """Base exception for git-related errors."""
    pass


class GitRepositoryNotFoundError(GitException):
    """Raised when no git repository is found."""

    def __init__(self, path: Optional[str] = None) -> None:
        """Initialize the object with required collaborators.

        Args:
            path: The path to process.
        """
        message = f"No git repository found at: {path}" if path else "No git repository found"
        super().__init__(
            message=message,
            error_code="GIT_REPO_NOT_FOUND",
            user_message="Git repository not found. Make sure you're in a valid git repository."
        )


class GitLibraryNotAvailableError(GitException):
    """Raised when GitPython library is not available."""

    def __init__(self) -> None:
        """Initialize the object with required collaborators.
        """
        super().__init__(
            message="GitPython library not available",
            error_code="GIT_LIB_UNAVAILABLE",
            user_message="Git functionality is not available. Please install GitPython library."
        )


# File-related exceptions
class FileException(BaseAppException):
    """Base exception for file-related errors."""
    pass


class FileNotFoundError(FileException):
    """Raised when a file is not found."""

    def __init__(self, file_path: str) -> None:
        """Initialize the object with required collaborators.

        Args:
            file_path: The file path to process.
        """
        super().__init__(
            message=f"File not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            user_message=f"The file '{file_path}' could not be found.",
            title="File Not Found"
        )


class FileAccessError(FileException):
    """Raised when file access is denied or fails."""

    def __init__(self, file_path: str, operation: str, cause: Optional[Exception] = None) -> None:
        """Initialize the object with required collaborators.

        Args:
            file_path: The file path to process.
            operation: The git operation name.
            cause: The cause value.
        """
        message = f"Failed to {operation} file: {file_path}"
        if cause:
            message += f" ({str(cause)})"
            
        super().__init__(
            message=message,
            error_code="FILE_ACCESS_ERROR",
            user_message=f"Cannot {operation} file '{file_path}'. Check file permissions."
        )


class FileReadError(FileException):
    """Raised when reading a file fails."""

    def __init__(self, file_path: str, cause: str) -> None:
        """Initialize the object with required collaborators.

        Args:
            file_path: The file path to process.
            cause: The cause value.
        """
        super().__init__(
            message=f"Failed to read file: {file_path} - {cause}",
            error_code="FILE_READ_ERROR",
            user_message=f"Could not read file '{file_path}'. {cause}"
        )


class FileWriteError(FileException):
    """Raised when writing to a file fails."""

    def __init__(self, file_path: str, cause: str) -> None:
        """Initialize the object with required collaborators.

        Args:
            file_path: The file path to process.
            cause: The cause value.
        """
        super().__init__(
            message=f"Failed to write file: {file_path} - {cause}",
            error_code="FILE_WRITE_ERROR",
            user_message=f"Could not write to file '{file_path}'. {cause}"
        )


class InvalidFileTypeError(FileException):
    """Raised when file type is not supported."""

    def __init__(self, file_path: str, expected_types: list) -> None:
        """Initialize the object with required collaborators.

        Args:
            file_path: The file path to process.
            expected_types: The expected types value.
        """
        types_str = ", ".join(expected_types)
        super().__init__(
            message=f"Invalid file type for {file_path}. Expected one of: {types_str}",
            error_code="INVALID_FILE_TYPE",
            user_message=f"Unsupported file type. Expected: {types_str}"
        )


class FileSizeError(FileException):
    """Raised when file size exceeds limits."""

    def __init__(self, file_path: str, actual_size: int, max_size: int) -> None:
        """Initialize the object with required collaborators.

        Args:
            file_path: The file path to process.
            actual_size: The actual size value.
            max_size: The max size value.
        """
        super().__init__(
            message=f"File {file_path} size {actual_size} bytes exceeds maximum {max_size} bytes",
            error_code="FILE_SIZE_ERROR",
            user_message=f"File is too large. Maximum size allowed: {max_size // (1024*1024)}MB"
        )


# Validation exceptions
class ValidationException(BaseAppException):
    """Base exception for validation errors."""
    pass


class InvalidInputError(ValidationException):
    """Raised when input validation fails."""

    def __init__(self, parameter: str, value: str, reason: str) -> None:
        """Initialize the object with required collaborators.

        Args:
            parameter: The parameter value.
            value: The value value.
            reason: The reason value.
        """
        super().__init__(
            message=f"Invalid {parameter}: {value} ({reason})",
            error_code="INVALID_INPUT",
            user_message=f"Invalid {parameter}: {reason}"
        )