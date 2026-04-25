"""
Global error management.
"""
import sys
import traceback
from functools import wraps

from PyQt6.QtWidgets import QMessageBox

from ui.main_window import MainWindow
from utils.exceptions import BaseAppException 
from core.constants import ErrorConstants

class ErrorManager:
    """Handles global application exceptions and displays popups."""

    _instance = None

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize the ErrorManager and attach system hooks.

        Args:
            main_window: The main window of the application used as the parent for error popups.

        Returns:
            None.
        """
        ErrorManager._instance = self
        self.main_window = main_window
        self._setup_exception_handling()

    @classmethod
    def handle_slot_error(cls, error: Exception) -> None:
        """Globally accessible method for the decorator to trigger the popup.

        Args:
            error: The exception instance caught by the safe_slot decorator.

        Returns:
            None.
        """
        if cls._instance:
            cls._instance.show_error_popup(error)
        else:
            traceback.print_exc()

    def _setup_exception_handling(self) -> None:
        """Tell Python to send ALL unhandled errors to our custom UI handler.

        Returns:
            None.
        """
        sys.excepthook = self.handle_global_exception

    def handle_global_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """Catches the error, prints it to the console, and triggers the popup.

        Args:
            exc_type: The class of the exception.
            exc_value: The exception instance itself.
            exc_traceback: The traceback object containing the call stack.

        Returns:
            None.
        """

        # Ignore KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        traceback.print_exception(exc_type, exc_value, exc_traceback)

        self.show_error_popup(exc_value)

    def show_error_popup(self, error: Exception) -> None:
        """Displays a error popup based on custom exceptions.

        Args:
            title: The title text for the message box.
            error: The exception object containing the error details.

        Returns:
            None. Shows a critical QMessageBox.
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
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorManager.handle_slot_error(e)
    return wrapper