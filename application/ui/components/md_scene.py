"""
Markdown scene.
"""
from pathlib import Path
from typing import Dict, Tuple

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPlainTextEdit, QTextBrowser, QListWidget, QTabWidget, QPushButton, QCheckBox, QSpacerItem, QSizePolicy, QLabel, QTreeWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidgetItem

from core.constants import UIConstants, AssetsConstants, FileConstants

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
        self.file_tree_widget.setHeaderHidden(True)

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
        self._tab_base_title = "Untitled"
        self._tab_dirty = False
        
        self.tab_1 = QWidget()
        self.tab_1_layout = QHBoxLayout(self.tab_1)

        self.vert_splitter = QSplitter(Qt.Orientation.Vertical)
        self.horiz_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.editor = QPlainTextEdit()
        self.preview = QTextBrowser()
        self.preview.setVisible(False)

        self.horiz_splitter.addWidget(self.editor)
        self.horiz_splitter.addWidget(self.preview)

        self.analyzer_list = QListWidget()
        self.analyzer_list.setVisible(False)

        self.vert_splitter.addWidget(self.horiz_splitter)
        self.vert_splitter.addWidget(self.analyzer_list)

        self.tab_1_layout.addWidget(self.vert_splitter)
        self.tabs.addTab(self.tab_1, self._tab_base_title)

        self.empty_tab = QWidget()
        self.tabs.addTab(self.empty_tab, "Tab 2")

        self.md_scene_layout.addWidget(self.tabs)

        # Adding right side to the main layout
        self.layout.addWidget(self.md_editor_widget)

    def load_file(self, file_path: str) -> bool:
        """Load a markdown file into the editor."""
        try:
            with open(file_path, 'r', encoding=FileConstants.ENCODING_UTF8, errors="replace") as file:
                self.editor.setPlainText(file.read())
            return True
        except (OSError, UnicodeDecodeError):
            return False

    def set_loading(self) -> None:
        """Display loading state in analyzer output list."""
        self.analyzer_list.clear()
        self.analyzer_list.addItem("Analyzing...")

    def set_analysis(self, report: str) -> None:
        """Display analyzer report in analyzer output list."""
        self.analyzer_list.clear()
        lines = report.splitlines() if report else ["No analysis output."]
        self.analyzer_list.addItems(lines)

    def set_error(self, message: str) -> None:
        """Display error in analyzer output list."""
        self.analyzer_list.clear()
        self.analyzer_list.addItem(f"Error: {message}")

    def get_editor_content(self) -> str:
        """Return current markdown editor content."""
        return self.editor.toPlainText()

    def set_active_tab_file(self, file_path: str) -> None:
        """Set the active markdown tab title based on file name."""
        self._tab_base_title = Path(file_path).name
        self._tab_dirty = False
        self._refresh_active_tab_title()

    def set_tab_dirty(self, dirty: bool) -> None:
        """Mark active markdown tab as dirty or clean."""
        self._tab_dirty = dirty
        self._refresh_active_tab_title()

    def _refresh_active_tab_title(self) -> None:
        """Refresh tab title with optional unsaved marker."""
        title = self._tab_base_title + (" *" if self._tab_dirty else "")
        self.tabs.setTabText(0, title)

    def populate_explorer(self, root_directory: str, markdown_extensions: Tuple[str, ...]) -> int:
        """Populate explorer tree with markdown files from a directory."""
        root_path = Path(root_directory)
        self.file_tree_widget.clear()

        if not root_path.exists() or not root_path.is_dir():
            return 0

        folder_items: Dict[str, QTreeWidgetItem] = {}
        markdown_files_count = 0

        for file_path in sorted(root_path.rglob("*")):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in markdown_extensions:
                continue

            relative_parts = file_path.relative_to(root_path).parts
            parent_item = self.file_tree_widget.invisibleRootItem()
            partial_folder = ""

            for folder_name in relative_parts[:-1]:
                partial_folder = f"{partial_folder}/{folder_name}" if partial_folder else folder_name
                if partial_folder not in folder_items:
                    folder_item = QTreeWidgetItem([folder_name])
                    folder_item.setFlags(folder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    parent_item.addChild(folder_item)
                    folder_items[partial_folder] = folder_item
                parent_item = folder_items[partial_folder]

            file_item = QTreeWidgetItem([relative_parts[-1]])
            file_item.setData(0, Qt.ItemDataRole.UserRole, str(file_path))
            parent_item.addChild(file_item)
            markdown_files_count += 1

        self.file_tree_widget.expandAll()
        return markdown_files_count
