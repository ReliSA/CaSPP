from PyQt6.QtCore import Qt

from core.tab_manager import TabManager

class EditorManager:
    """Handles actions done in the markdown editor."""

    def __init__(self, tab_manager: TabManager) -> None:
        """Initialize EditorManager with required collaborators.

        Args:
            markdown_scene: Markdown scene containing ui components for markdown file editation.
        """
        self.tab_manager = tab_manager

    def live_preview_check_box_state_changed(self, state: int) -> None:
        """Update visibility of the markdown preview.

        Args:
            state: New state of the checkbox.

        Returns:
            None.
        """
        is_visible = (state == Qt.CheckState.Checked.value)
        for tab in self.tab_manager.tab_states.keys():
            tab.preview.setVisible(is_visible)
        

    def markdown_analyzer_check_box_state_changed(self, state: int) -> None:
        """Update visibility of the analyzer list.

        Args:
            state:  New state of the checkbox.

        Returns:
            None.
        """
        is_visible = (state == Qt.CheckState.Checked.value)
        for tab in self.tab_manager.tab_states.keys():
            tab.analyzer_list.setVisible(is_visible)