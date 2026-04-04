"""
Sidebar.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap

from core.constants import AssetsConstants

class SidebarMenu(QWidget):
    """Handles sidebar menu ui actions."""

    def __init__(self) -> None:
        """
        Initializes sidebar menu.
        """
        super().__init__()
        
        # Setup app sidebar
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.btn_md = QPushButton()
        self.btn_md.setIcon(QIcon(QPixmap(AssetsConstants.SIDEBAR_MARKDOWN_SCENE_ICON_PATH)))
        
        self.btn_git = QPushButton()
        self.btn_git.setIcon(QIcon(QPixmap(AssetsConstants.SIDEBAR_GIT_SCENE_ICON_PATH)))

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.btn_md)
        self.layout.addWidget(self.btn_git)
        self.layout.addItem(spacer)