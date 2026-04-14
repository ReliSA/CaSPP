"""
Top menu.
"""
from PyQt6.QtWidgets import QMenuBar, QMenu, QWidget
from PyQt6.QtGui import QAction

from core.constants import UIConstants

class TopMenuBar(QMenuBar):
    """Handles top menu bar actions."""

    def __init__(self, parent: QWidget =None) -> None:
        """
        Initializes top menu bar.
        
        Args:
            parent: Parent element
        """
        super().__init__(parent)

        # File menu setup
        self.menu_file = QMenu(UIConstants.TOP_BAR_FILE_MENU_NAME, self)
        
        self.action_open_file = QAction(UIConstants.OPEN_FILE_ACTION_NAME, self)
        self.action_open_file.setShortcut(UIConstants.OPEN_FILE_ACTION_SHORTCUT)
        
        self.action_save_file = QAction(UIConstants.SAVE_FILE_ACTION_NAME, self)
        self.action_save_file.setShortcut(UIConstants.SAVE_FILE_ACTION_SHORTCUT)
        
        self.action_open_folder = QAction(UIConstants.OPEN_FOLDER_ACTION_NAME)
        self.action_open_folder.setShortcut(UIConstants.OPEN_FOLDER_ACTION_SHORTCUT)

        self.action_open_explorer = QAction(UIConstants.OPEN_EXPLORER_ACTION_NAME, self)
        self.action_open_explorer.setShortcut(UIConstants.OPEN_EXPLORER_ACTION_SHORTCUT)
        
        self.action_live_preview = QAction(UIConstants.SHOW_LIVE_PREVIEW_ACTION_NAME, self)
        self.action_live_preview.setShortcut(UIConstants.SHOW_LIVE_PREVIEW_ACTION_SHORTCUT)
        
        self.action_show_analyzer = QAction(UIConstants.SHOW_ANALYZER_OUTPUT_ACTION_NAME, self)
        self.action_show_analyzer.setShortcut(UIConstants.SHOW_ANALYZER_OUTPUT_ACTION_SHORTCUT)

        # Adding Actions to the File Menu
        self.menu_file.addAction(self.action_open_file)
        self.menu_file.addAction(self.action_save_file)
        self.menu_file.addAction(self.action_open_folder)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_open_explorer)
        self.menu_file.addAction(self.action_live_preview)
        self.menu_file.addAction(self.action_show_analyzer)

        # Git Menu setup
        self.menu_git = QMenu(UIConstants.TOP_BAR_GIT_MENU_NAME, self)
        
        self.action_status = QAction(UIConstants.STATUS_ACTION_NAME, self)
        self.action_status.setShortcut(UIConstants.STATUS_ACTION_SHORTCUT)
        
        self.action_fetch = QAction(UIConstants.FETCH_ACTION_NAME, self)
        self.action_fetch.setShortcut(UIConstants.FETCH_ACTION_SHORTCUT)
        
        self.action_pull = QAction(UIConstants.PULL_ACTION_NAME, self)
        self.action_pull.setShortcut(UIConstants.PULL_ACTION_SHORTCUT)
        
        self.action_push = QAction(UIConstants.PUSH_ACTION_NAME, self)
        self.action_push.setShortcut(UIConstants.PUSH_ACTION_SHORTCUT)

        # Adding Actions to the Git Menu
        self.menu_git.addAction(self.action_status)
        self.menu_git.addAction(self.action_fetch)
        self.menu_git.addAction(self.action_pull)
        self.menu_git.addAction(self.action_push)

        # Attaching menus to the top bar
        self.addMenu(self.menu_file)
        self.addMenu(self.menu_git)