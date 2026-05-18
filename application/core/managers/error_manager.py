"""
UI popup manager.
"""
import logging
from PyQt6.QtWidgets import QMessageBox

from ui.main_window import MainWindow

logger = logging.getLogger(__name__)


class ErrorManager:
    """Provides methods for displaying UI dialogs."""

    _instance = None

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize the manager.

        Args:
            main_window: The application's main window.
        """
        ErrorManager._instance = self
        self.main_window = main_window

    @classmethod
    def show_error(cls, title: str, message: str) -> None:
        """Displays a critical error popup (Red X)."""
        if cls._instance:
            QMessageBox.critical(cls._instance.main_window, title, message)
        else:
            logger.error("Error popup [%s]: %s", title, message)

    @classmethod
    def show_warning(cls, title: str, message: str) -> None:
        """Displays a warning popup (Yellow Triangle)."""
        if cls._instance:
            QMessageBox.warning(cls._instance.main_window, title, message)
        else:
            logger.warning("Warning popup [%s]: %s", title, message)

    @classmethod
    def show_info(cls, title: str, message: str) -> None:
        """Displays an information popup (Blue 'i')."""
        if cls._instance:
            QMessageBox.information(cls._instance.main_window, title, message)
        else:
            logger.info("Info popup [%s]: %s", title, message)

    @classmethod
    def ask_save_discard_cancel(cls, title: str, message: str) -> str:
        """Asks the user to Save, Discard, or Cancel.

        Args:
            title: The title of the dialog window.
            message: The main text warning to display to the user.

        Returns:
            A string indicating the user's choice: 'save', 'discard', or 'cancel'.
        """
        if not cls._instance:
            return "discard"

        box = QMessageBox(cls._instance.main_window)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.setStandardButtons(
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        box.setDefaultButton(QMessageBox.StandardButton.Save)

        result = box.exec()
        if result == QMessageBox.StandardButton.Save:
            return "save"
        elif result == QMessageBox.StandardButton.Discard:
            return "discard"
        return "cancel"

    @classmethod
    def ask_yes_no(cls, title: str, message: str) -> bool:
        """Asks a Yes/No question.

        Args:
            title: The title of the dialog window.
            message: The main text warning to display to the user.

        Returns:
            True if the user clicked Yes, False if the user clicked No or closed the dialog.
        """
        if not cls._instance:
            return False

        box = QMessageBox(cls._instance.main_window)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.No)

        return box.exec() == QMessageBox.StandardButton.Yes