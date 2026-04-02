"""
Git scene.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QListWidget
from PyQt6.QtGui import QIcon

from core.constants import UIConstants, AssetsConstants

class GitScene(QWidget):
    """Handles git scene ui actions."""

    def __init__(self) -> None:
        """
        Initializes git scene.
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

        self.control_layout.addWidget(self.btn_status)
        self.control_layout.addWidget(self.btn_fetch)
        self.control_layout.addWidget(self.btn_pull)
        self.control_layout.addWidget(self.btn_push)

        # Adding control panel the main layout
        self.layout.addLayout(self.control_layout)

        # Changed file list setup
        self.list_git_files = QListWidget()
        
        self.list_git_files.addItem("main.py (Modified)")
        self.list_git_files.addItem("components/md_scene.py (Added)")

        # Adding chnaged file list to the main layout
        self.layout.addWidget(self.list_git_files)