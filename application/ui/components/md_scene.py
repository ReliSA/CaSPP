"""
Markdown scene.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPlainTextEdit, QTextBrowser, QListWidget, QTabWidget, QPushButton, QCheckBox, QSpacerItem, QSizePolicy, QLabel, QTreeWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from core.constants import UIConstants, AssetsConstants

class MarkdownScene(QWidget):
    """Handles markdown scene ui actions."""

    def __init__(self) -> None:
        """
        Initializes markdown scene.
        """
        super().__init__()
        
        # Markdown scene setup
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # File explorer setup
        self.file_explorer_widget = QWidget()
        self.file_explorer_widget.setMaximumSize(QSize(206, 16777215))
        
        self.file_explorer_layout = QVBoxLayout(self.file_explorer_widget)
        self.file_explorer_layout.setContentsMargins(1, -1, 1, -1)
        self.file_explorer_layout.setSpacing(6)

        # File explorer control layout setup 
        self.file_explorer_control_layout = QHBoxLayout()
        self.file_explorer_control_layout.setContentsMargins(0, -1, 0, -1)
        
        self.explorer_label = QLabel(UIConstants.EXPLORER_LABEL)
        spacer_exp = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.close_explorer_button = QPushButton()
        self.close_explorer_button.setIcon(QIcon(AssetsConstants.CLOSE_FILE_EXPLORER_ICON_PATH))

        self.file_explorer_control_layout.addWidget(self.explorer_label)
        self.file_explorer_control_layout.addItem(spacer_exp)
        self.file_explorer_control_layout.addWidget(self.close_explorer_button)

        # File explorer tree setup 
        self.file_tree_widget = QTreeWidget()
        self.file_tree_widget.setHeaderLabels(["1"])

        # Adding header and tree to explorer layout
        self.file_explorer_layout.addLayout(self.file_explorer_control_layout)
        self.file_explorer_layout.addWidget(self.file_tree_widget)

        # Adding left side to main layout
        self.layout.addWidget(self.file_explorer_widget)

        # Markdown editor setup
        self.md_editor_widget = QWidget()
        self.md_scene_layout = QVBoxLayout(self.md_editor_widget)

        # Controll panel setup
        self.md_control_panel = QHBoxLayout()
        self.md_control_panel.setContentsMargins(-1, 0, -1, 0)

        self.open_explorer_button = QPushButton(UIConstants.OPEN_EXPLORER_BUTTON_LABEL)
        spacer_md = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.save_changes_button = QPushButton(UIConstants.SAVE_CHANGES_BUTTON_LABEL)
        self.live_preview_check_box = QCheckBox(UIConstants.LIVE_PREVIEW_CHECK_BOX_LABEL)
        self.analyzer_check_box = QCheckBox(UIConstants.ANALYZER_CHECK_BOX_LABEL)

        self.md_control_panel.addWidget(self.open_explorer_button)
        self.md_control_panel.addItem(spacer_md)
        self.md_control_panel.addWidget(self.save_changes_button)
        self.md_control_panel.addWidget(self.live_preview_check_box)
        self.md_control_panel.addWidget(self.analyzer_check_box)

        self.md_scene_layout.addLayout(self.md_control_panel)

        # Tab setup
        self.tabs = QTabWidget()
        
        self.tab_1 = QWidget()
        self.tab_1_layout = QHBoxLayout(self.tab_1)

        self.vert_splitter = QSplitter(Qt.Orientation.Vertical)
        self.horiz_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.editor = QPlainTextEdit()
        self.preview = QTextBrowser()
        self.horiz_splitter.addWidget(self.editor)
        self.horiz_splitter.addWidget(self.preview)

        self.analyzer_list = QListWidget()

        self.vert_splitter.addWidget(self.horiz_splitter)
        self.vert_splitter.addWidget(self.analyzer_list)

        self.tab_1_layout.addWidget(self.vert_splitter)
        self.tabs.addTab(self.tab_1, "Tab 1")

        self.empty_tab = QWidget()
        self.tabs.addTab(self.empty_tab, "Tab 2")

        self.md_scene_layout.addWidget(self.tabs)

        # Adding right side to the main layout
        self.layout.addWidget(self.md_editor_widget)