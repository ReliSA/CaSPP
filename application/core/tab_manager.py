from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QColor

from ui.components.tab_widget import TabWidget
from ui.components.md_scene import MarkdownScene
from core.constants import UIConstants

class TabState:
    """Represents the logical state and metadata of a single markdown editor tab."""

    def __init__(self, widget: TabWidget, file_path: Optional[str] = None) -> None:
        """Initializes the tab state with its associated widget and optional file path.

        Args:
            widget: The UI component (TabWidget) representing the tab.
            file_path: Optional path to the markdown file associated with this tab. Defaults to None for a new 'Untitled' tab.
        """
        self.widget = widget
        self.file_path = file_path
        self.base_title = Path(file_path).name if file_path else UIConstants.UNTITLED_TAB_NAME
        self.is_dirty = False


class TabManager:
    """Manages the creation, deletion, state tracking, and UI updates for markdown tabs."""

    def __init__(self, markdown_scene: MarkdownScene) -> None:
        """Initializes the tab manager, links the main UI scene, and creates a default tab.

        Args:
            markdown_scene: Markdown scene containing the tab widget layout, file explorer and markdown control panel.
        """
        self.scene = markdown_scene
        self.tabs_widget = markdown_scene.tabs
        self.tab_states: Dict[TabWidget, TabState] = {}
        
        self.on_editor_text_changed_callback = None
        self.on_preview_anchor_clicked_callback = None
        
        self.add_new_tab()

    def _update_tab_closability(self) -> None:
        """Shows or hides the close button to prevent closing the last empty tab.
        """
        if self.tabs_widget.count() > 1:
            self.tabs_widget.setTabsClosable(True)
        elif self.tabs_widget.count() == 1:
            state = self.get_current_state()
            if state and (state.file_path is not None or state.is_dirty):
                self.tabs_widget.setTabsClosable(True)
            else:
                self.tabs_widget.setTabsClosable(False)
        else:
            self.tabs_widget.setTabsClosable(False)

    def add_new_tab(self, file_path: Optional[str] = None) -> TabWidget:
        """Creates a new tab, applies current global UI settings, and tracks its state.

        Args:
            file_path: Optional path to a file to open in the new tab. Defaults to None.

        Returns:
            The newly created TabWidget instance.
        """
        tab = TabWidget()
        state = TabState(tab, file_path)
        self.tab_states[tab] = state
        
        tab.preview.setVisible(self.scene.live_preview_check_box.isChecked())
        tab.analyzer_list.setVisible(self.scene.analyzer_check_box.isChecked())

        tab.editor.textChanged.connect(self._handle_text_changed)
        tab.preview.anchorClicked.connect(self._handle_anchor_clicked)

        index = self.tabs_widget.addTab(tab, state.base_title)
        self.tabs_widget.setCurrentIndex(index)
        self._update_tab_closability()
        return tab

    def close_tab(self, index: int) -> None:
        """Closes the specified tab, cleans up its tracked state, and ensures one tab remains open.

        Args:
            index: The integer index of the tab to be closed.
        """
        tab = self.tabs_widget.widget(index)
        if tab in self.tab_states:
            del self.tab_states[tab]
        self.tabs_widget.removeTab(index)

        if self.tabs_widget.count() == 0:
            self.add_new_tab()
        else:
            self._update_tab_closability()

    def get_current_tab(self) -> Optional[TabWidget]:
        """Gets the currently active tab widget.

        Returns:
            The active TabWidget, or None if no tabs exist.
        """
        return self.tabs_widget.currentWidget()

    def get_current_state(self) -> Optional[TabState]:
        """Gets the state metadata object for the currently active tab.

        Returns:
            The TabState of the active tab, or None if no tabs exist.
        """
        tab = self.get_current_tab()
        return self.tab_states.get(tab) if tab else None

    def load_file_into_tab(self, file_path: str, content: str) -> None:
        """Loads file content by focusing an open tab, reusing an empty tab, or spawning a new one.

        Args:
            file_path: The path of the file being loaded.
            content: The text content to populate the editor with.
        """
        for tab, state in self.tab_states.items():
            if state.file_path == file_path:
                self.tabs_widget.setCurrentIndex(self.tabs_widget.indexOf(tab))
                tab.editor.setPlainText(content)
                return

        current_tab = self.get_current_tab()
        current_state = self.get_current_state()
        
        if current_tab and not current_state.file_path and not current_state.is_dirty and not current_tab.editor.toPlainText():
            tab, state = current_tab, current_state
        else:
            tab = self.add_new_tab()
            state = self.tab_states[tab]

        state.file_path = file_path
        tab.editor.setPlainText(content)
        self.set_active_tab_file(file_path)

    def get_editor_content(self) -> str:
        """Gets the raw text content from the currently active editor.

        Returns:
            A string containing the current markdown text.
        """
        tab = self.get_current_tab()
        return tab.editor.toPlainText() if tab else ""

    def set_active_tab_file(self, file_path: str) -> None:
        """Updates the active tab's state with a new file path and marks it as cleanly saved.

        Args:
            file_path: The new file path to associate with the currently active tab.
        """
        state = self.get_current_state()
        if state:
            state.file_path = file_path
            state.base_title = Path(file_path).name
            state.is_dirty = False
            self._refresh_tab_title(self.tabs_widget.currentIndex())
            self._update_tab_closability()

    def set_tab_dirty(self, dirty: bool) -> None:
        """Updates the active tab's dirty state and refreshes its title to reflect unsaved changes.

        Args:
            dirty: Boolean indicating whether the tab has unsaved modifications.
        """
        state = self.get_current_state()
        if state:
            state.is_dirty = dirty
            self._refresh_tab_title(self.tabs_widget.currentIndex())

    def _refresh_tab_title(self, index: int) -> None:
        """Updates the tab's display title, appending an asterisk if there are unsaved changes.

        Args:
            index: The integer index of the tab whose title needs to be refreshed.
        """
        tab = self.tabs_widget.widget(index)
        state = self.tab_states.get(tab)
        if state:
            title = state.base_title + (" *" if state.is_dirty else "")
            self.tabs_widget.setTabText(index, title)

    def _handle_text_changed(self):
        """Routes the internal editor text changed event to the external application callback.
        """
        if self.on_editor_text_changed_callback:
            self.on_editor_text_changed_callback()

    def _handle_anchor_clicked(self, url: QUrl) -> None:
        """Routes the preview link clicked event to the external application callback.

        Args:
            url: Clicked url in markdown preview.
        """
        if self.on_preview_anchor_clicked_callback:
            self.on_preview_anchor_clicked_callback(url)

    def set_loading(self) -> None:
        """Displays a loading indicator in the active tab's analyzer panel.
        """
        tab = self.get_current_tab()
        if tab:
            tab.analyzer_list.clear()
            tab.analyzer_list.addItem("Analyzing...")

    def set_analysis(self, report: str) -> None:
        """Displays the formatted analysis report in the active tab's analyzer panel.

        Args:
            report: The formatted string containing the analyzer output.
        """
        tab = self.get_current_tab()
        if not tab:
            return
            
        tab.analyzer_list.clear()
        if not report:
            tab.analyzer_list.addItem("No analysis output.")
            return
            
        for line in report.splitlines():
            item = QListWidgetItem(line)
            if "⚠️" in line or "(line" in line:
                item.setForeground(QColor("#D7BA7D"))
            elif "✅" in line:
                item.setForeground(QColor("#6A9955"))
            else:
                item.setForeground(QColor("#CCCCCC"))
                
            tab.analyzer_list.addItem(item)

    def set_error(self, message: str) -> None:
        """Displays an error message in the active tab's analyzer panel.

        Args:
            message: The specific error string to display to the user.
        """
        tab = self.get_current_tab()
        if tab:
            tab.analyzer_list.clear()
            tab.analyzer_list.addItem(f"Error: {message}")