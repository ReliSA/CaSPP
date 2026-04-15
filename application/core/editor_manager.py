from PyQt6.QtCore import Qt
import markdown
from pymdownx import tilde, caret, mark, tasklist, emoji, superfences, highlight
from pymdownx.emoji import twemoji, to_alt

from core.tab_manager import TabManager
from core.constants import MarkdownPreviewConstants

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
        
        self.update_live_preview()

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
        self.update_live_preview()

    def update_live_preview(self) -> None:
        """Converts the editor's markdown to HTML and updates the live preview panel.
        
        Returns:
            None.
        """
        if not self.markdown_scene.preview.isVisible():
            return
            
        content = self.markdown_scene.get_editor_content()
        
        html_content = markdown.markdown(
            content, 
            extensions=[
                'extra', 'sane_lists', 'pymdownx.tilde', 'pymdownx.caret',
                'pymdownx.mark', 'pymdownx.tasklist', 'pymdownx.emoji',
                'pymdownx.superfences',
                'pymdownx.highlight'
            ],
            extension_configs={
                'pymdownx.emoji': {
                    'emoji_index': twemoji,
                    'emoji_generator': to_alt
                }
            }
        )
        styled_html = f"""
        <style>
           {MarkdownPreviewConstants.DEFAULT_CSS}
        </style>
        {html_content}
        """
        
        self.markdown_scene.preview.setHtml(styled_html)
