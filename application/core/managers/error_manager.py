"""
Global error management.
"""
import logging
import sys
import traceback
from functools import wraps

from PyQt6.QtWidgets import QMessageBox

from ui.main_window import MainWindow
from utils.exceptions import BaseAppException 
from utils.constants import ErrorConstants

logger = logging.getLogger(__name__)


class ErrorManager:
    """Handles global application exceptions and displays popups."""

    _instance = None

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize the ErrorManager and attach system hooks.

        Args:
            main_window: The main window of the application used as the parent for error popups.
        """
        ErrorManager._instance = self
        self.main_window = main_window
        self._setup_exception_handling()

    @classmethod
    def handle_slot_error(cls, error: Exception) -> None:
        """Globally accessible method for the decorator to trigger the popup.

        Args:
            error: The exception instance caught by the safe_slot decorator.
        """
        if cls._instance:
            if isinstance(error, BaseAppException):
                logger.warning("Handled application error in Qt slot: %s", error)
            else:
                tb = getattr(error, "__traceback__", None)
                logger.error(
                    "Unhandled exception in Qt slot",
                    exc_info=(type(error), error, tb) if tb else True,
                )
            cls._instance.show_error_popup(error)
        else:
            tb = getattr(error, "__traceback__", None)
            logger.error(
                "Slot error (no ErrorManager instance): %s",
                error,
                exc_info=(type(error), error, tb) if tb else None,
            )

    def _setup_exception_handling(self) -> None:
        """Tell Python to send ALL unhandled errors to our custom UI handler.
        """
        sys.excepthook = self.handle_global_exception

    def handle_global_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """Catches the error, prints it to the console, and triggers the popup.

        Args:
            exc_type: The class of the exception.
            exc_value: The exception instance itself.
            exc_traceback: The traceback object containing the call stack.
        """

        # Ignore KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

        self.show_error_popup(exc_value)

    def show_error_popup(self, error: Exception) -> None:
        """Displays a error popup based on custom exceptions.

        Args:
            error: The exception object containing the error details.
        """
        title = ErrorConstants.DEFAULT_ERROR_TITLE
        user_message = ErrorConstants.DEFAULT_ERROR_MESSAGE

        if isinstance(error, BaseAppException):
            user_message = error.user_message
            title = getattr(error, 'title', title)
        else:
            user_message += f"\n\nDetails: {str(error)}"

        QMessageBox.critical(self.main_window, title, user_message)

def safe_slot(func):
    """Decorator to catch exceptions in PyQt slots and route them to the UI popup.

    Args:
        func: The slot function or method to be wrapped.

    Returns:
        The wrapped function which intercepts exceptions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Run the wrapped function and route exceptions to the error manager.

        Args:
            *args: The args value.
            **kwargs: The kwargs value.

        Returns:
            The return value.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorManager.handle_slot_error(e)
    return wrapper