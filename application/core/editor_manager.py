from PyQt6.QtCore import Qt
import markdown
from pymdownx import tilde, caret, mark, tasklist, emoji, superfences, highlight, saneheaders
from pymdownx.emoji import twemoji, to_alt

from core.tab_manager import TabManager
from core.constants import MarkdownPreviewConstants, EditorConstants

class EditorManager:
    """Handles actions done in the markdown editor."""

    def __init__(self, tab_manager: TabManager) -> None:
        """Initialize EditorManager with required collaborators.

        Args:
            tab_manager: The tab manager used by this component.
        """
        self.tab_manager = tab_manager

    def live_preview_check_box_state_changed(self, state: int) -> None:
        """Update visibility of the markdown preview.

        Args:
            state: New state of the checkbox.
        """
        is_visible = (state == Qt.CheckState.Checked.value)
        for tab in self.tab_manager.tab_states.keys():
            tab.preview.setVisible(is_visible)
            if is_visible:
                self._update_tab_preview(tab)
            
    def markdown_analyzer_check_box_state_changed(self, state: int) -> None:
        """Update visibility of the analyzer list.

        Args:
            state: New state of the checkbox.
        """
        is_visible = (state == Qt.CheckState.Checked.value)
        for tab in self.tab_manager.tab_states.keys():
            tab.analyzer_list.setVisible(is_visible)

    def update_live_preview(self) -> None:
        """Converts the current editor's markdown to HTML (used when typing).
        """
        self._update_tab_preview(self.tab_manager.get_current_tab())

    def _update_tab_preview(self, tab) -> None:
        """Converts the editor's markdown to HTML and updates the live preview panel.

        Args:
            tab: The tab widget to update.
        """
        tab = self.tab_manager.get_current_tab()

        if not tab or tab.preview.isHidden():
            return
              
        content = self.tab_manager.get_editor_content()
        
        html_content = markdown.markdown(
            content, 
            extensions=[
                'extra', 'sane_lists', 'pymdownx.tilde', 'pymdownx.caret',
                'pymdownx.mark', 'pymdownx.tasklist', 'pymdownx.emoji',
                'pymdownx.superfences', 'pymdownx.saneheaders',
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
           body, p, li, table, th, td {{
               font-size: {EditorConstants.FONT_SIZE}pt !important;
           }}
        </style>
        {html_content}
        """

        scroll_bar = tab.preview.verticalScrollBar()
        current_scroll_position = scroll_bar.value()
        
        tab.preview.setHtml(styled_html)

        scroll_bar.setValue(current_scroll_position)
