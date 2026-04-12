from PyQt6.QtCore import Qt

from ui.components.md_scene import MarkdownScene

class EditorManager:
    """Handles actions done in the markdown editor."""

    def __init__(self, markdown_scene: MarkdownScene) -> None:
        """Initialize EditorManager with required collaborators.

        Args:
            markdown_scene: Markdown scene containing ui components for markdown file editation.
        """
        self.markdown_scene = markdown_scene

    def live_preview_check_box_state_changed(self, state: int) -> None:
        """Update visibility of the markdown preview.

        Args:
            state: New state of the checkbox.

        Returns:
            None.
        """
        is_visible = (state == Qt.CheckState.Checked.value)
        self.markdown_scene.preview.setVisible(is_visible)
        

    def markdown_analyzer_check_box_state_changed(self, state: int) -> None:
        """Update visibility of the analyzer list.

        Args:
            state:  New state of the checkbox.

        Returns:
            None.
        """
        is_visible = (state == Qt.CheckState.Checked.value)
        self.markdown_scene.analyzer_list.setVisible(is_visible)