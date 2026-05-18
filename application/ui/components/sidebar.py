"""
Sidebar.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy

from utils.constants import UIConstants

class SidebarMenu(QWidget):
    """Handles sidebar menu ui actions."""

    def __init__(self) -> None:
        """Initializes sidebar menu.
        """
        super().__init__()
        
        # Setup app sidebar
        self.setObjectName(UIConstants.SIDEBAR_UI_ID)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.btn_md = QPushButton()
        self.btn_md.setObjectName(UIConstants.SIDEBAR_MD_BTN_ID)
        self.btn_md.setCheckable(True)
        self.btn_md.setAutoExclusive(True)
        self.btn_md.setChecked(True)
        
        self.btn_git = QPushButton()
        self.btn_git.setObjectName(UIConstants.SIDEBAR_GIT_BTN_ID)
        self.btn_git.setCheckable(True)
        self.btn_git.setAutoExclusive(True)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.btn_md)
        self.layout.addWidget(self.btn_git)
        self.layout.addItem(spacer)