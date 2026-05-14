"""
Git scene.
"""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QListWidget,
    QPlainTextEdit,
)
from PyQt6.QtGui import QIcon

from utils.constants import UIConstants, AssetsConstants, GitConstants

class GitScene(QWidget):
    """Handles git scene ui actions."""

    def __init__(self) -> None:
        """Initializes git scene.
        """
        super().__init__()
        
        # Git scene main vertical layout
        self.layout = QVBoxLayout(self)

        # Git control panel setup
        self.control_layout = QHBoxLayout()

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.control_layout.addItem(spacer)

        self.btn_status = QPushButton(UIConstants.STATUS_BUTTON_LABEL)
        self.btn_status.setIcon(QIcon(AssetsConstants.STATUS_BUTTON_ICON_PATH))

        self.btn_fetch = QPushButton(UIConstants.FETCH_BUTTON_LABEL)
        self.btn_fetch.setIcon(QIcon(AssetsConstants.FETCH_BUTTON_ICON_PATH))

        self.btn_pull = QPushButton(UIConstants.PULL_BUTTON_LABEL)
        self.btn_pull.setIcon(QIcon(AssetsConstants.PULL_BUTTON_ICON_PATH))

        self.btn_push = QPushButton(UIConstants.PUSH_BUTTON_LABEL)
        self.btn_push.setIcon(QIcon(AssetsConstants.PUSH_BUTTON_ICON_PATH))

        self.btn_export_staged = QPushButton(UIConstants.EXPORT_STAGED_BUTTON_LABEL)

        self.control_layout.addWidget(self.btn_status)
        self.control_layout.addWidget(self.btn_fetch)
        self.control_layout.addWidget(self.btn_pull)
        self.control_layout.addWidget(self.btn_push)
        self.control_layout.addWidget(self.btn_export_staged)

        # Adding control panel the main layout
        self.layout.addLayout(self.control_layout)

        # Changed file list setup
        self.list_git_files = QListWidget()
        self.list_git_files.setObjectName(UIConstants.GIT_CONSOLE_UI_ID)

        # Adding chnaged file list to the main layout
        self.layout.addWidget(self.list_git_files)

        # Git commit message setup
        self.commit_message_input = QPlainTextEdit()
        self.commit_message_input.setObjectName(UIConstants.GIT_COMMIT_UI_ID)
        self.commit_message_input.setPlaceholderText(GitConstants.GIT_COMMIT_PLACEHOLDER_TEXT)
        self.commit_message_input.setFixedHeight(UIConstants.GIT_COMMIT_MESSAGE_INPUT_HEIGHT)
        self.layout.addWidget(self.commit_message_input)
        
        # Adding git commint message to the main layout
        self.layout.addWidget(self.commit_message_input)

    def set_output(self, message: str) -> None:
        """Replace git output list with new message lines.

        Args:
            message: The message to display or use for the operation.
        """
        self.list_git_files.clear()
        lines = message.splitlines() if message else ["No output."]
        self.list_git_files.addItems(lines)

    def append_output(self, message: str) -> None:
        """Append a single git output line.

        Args:
            message: The message to display or use for the operation.
        """
        self.list_git_files.addItem(message)

    def set_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable git action buttons.

        Args:
            enabled: Whether the option should be enabled.
        """
        self.btn_status.setEnabled(enabled)
        self.btn_fetch.setEnabled(enabled)
        self.btn_pull.setEnabled(enabled)
        self.btn_push.setEnabled(enabled)
        self.btn_export_staged.setEnabled(enabled)
        self.commit_message_input.setEnabled(enabled)