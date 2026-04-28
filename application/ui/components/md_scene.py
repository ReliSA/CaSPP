"""
Markdown scene.
"""
from pathlib import Path
from typing import Dict, Iterable

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QCheckBox, QSpacerItem, QSizePolicy, QLabel, QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

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

        # Main layout splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.main_splitter)

        # File explorer setup
        self.file_explorer_widget = QWidget()
        
        self.file_explorer_layout = QVBoxLayout(self.file_explorer_widget)
        self.file_explorer_layout.setContentsMargins(0, 0, 0, 0)
        self.file_explorer_layout.setSpacing(0)

        # File explorer control layout setup 
        self.file_explorer_control_layout = QHBoxLayout()
        self.file_explorer_control_layout.setContentsMargins(10, 5, 5, 5)
        
        self.explorer_label = QLabel(UIConstants.EXPLORER_LABEL)
        spacer_exp = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.close_explorer_button = QPushButton()
        self.close_explorer_button.setIcon(QIcon(AssetsConstants.CLOSE_FILE_EXPLORER_ICON_PATH))

        self.file_explorer_control_layout.addWidget(self.explorer_label)
        self.file_explorer_control_layout.addItem(spacer_exp)
        self.file_explorer_control_layout.addWidget(self.close_explorer_button)

        # File explorer tree setup 
        self.file_tree_widget = QTreeWidget()
        self.file_tree_widget.setHeaderHidden(True)

        # Adding header and tree to explorer layout
        self.file_explorer_layout.addLayout(self.file_explorer_control_layout)
        self.file_explorer_layout.addWidget(self.file_tree_widget)

        # Adding left side to main splitter
        self.main_splitter.addWidget(self.file_explorer_widget)

        # Markdown editor setup
        self.md_editor_widget = QWidget()
        self.md_scene_layout = QVBoxLayout(self.md_editor_widget)

        # Controll panel setup
        self.md_control_panel = QHBoxLayout()
        self.md_control_panel.setContentsMargins(-1, 0, -1, 0)

        self.open_explorer_button = QPushButton(UIConstants.OPEN_EXPLORER_BUTTON_LABEL)
        self.open_explorer_button.setVisible(False)

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
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setTabsClosable(True)
        
        self.md_scene_layout.addWidget(self.tabs)
        self.layout.addWidget(self.md_editor_widget)
        
        self.md_scene_layout.addWidget(self.tabs)

        # Adding right side to the main splitter
        self.main_splitter.addWidget(self.md_editor_widget)
        self.main_splitter.setSizes([UIConstants.FILE_EXPLORER_INIT_WIDTH, UIConstants.FILE_EXPLORER_INIT_HEIGHT])

    def populate_explorer(self, root_directory: str, markdown_file_paths: Iterable[str]) -> int:
        """Populate explorer tree from markdown file paths provided by FileManager."""
        root_path = Path(root_directory)
        self.file_tree_widget.clear()

        folder_items: Dict[str, QTreeWidgetItem] = {}
        markdown_files_count = 0

        for file_path in sorted(markdown_file_paths):
            path_obj = Path(file_path)

            try:
                relative_parts = path_obj.relative_to(root_path).parts
            except ValueError:
                continue

            parent_item = self.file_tree_widget.invisibleRootItem()
            partial_folder = ""

            for folder_name in relative_parts[:-1]:
                partial_folder = f"{partial_folder}/{folder_name}" if partial_folder else folder_name
                if partial_folder not in folder_items:
                    folder_item = QTreeWidgetItem([folder_name])
                    folder_item.setFlags(folder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    folder_item.setIcon(0, QIcon(QPixmap(AssetsConstants.FOLDER_ICON_PATH)))
                    parent_item.addChild(folder_item)
                    folder_items[partial_folder] = folder_item
                parent_item = folder_items[partial_folder]

            file_item = QTreeWidgetItem([relative_parts[-1]])
            file_item.setData(0, Qt.ItemDataRole.UserRole, str(path_obj))
            file_item.setIcon(0, QIcon(QPixmap(AssetsConstants.MARKDOWN_FILE_ICON_PATH)))
            parent_item.addChild(file_item)
            markdown_files_count += 1

        self.file_tree_widget.expandAll()
        return markdown_files_count
