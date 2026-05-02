from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QPlainTextEdit, QTextBrowser, QListWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.components.markdown_highlighter import MarkdownHighlighter
from ui.components.markdown_editor_widget import MarkdownEditorWidget

class TabWidget(QWidget):
    """A single tab holding its own editor, preview, and analyzer list."""
    
    def __init__(self, parent: QWidget = None) -> None:
        """Initializes top menu bar.

        Args:
            parent: Parent element.
        """
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.vert_splitter = QSplitter(Qt.Orientation.Vertical)
        self.horiz_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Setup editor
        self.editor = MarkdownEditorWidget()
        
        # Attach the highlighter to the editor
        self.highlighter = MarkdownHighlighter(self.editor.document())
        
        # Setup preview
        self.preview = QTextBrowser()
        self.preview.setVisible(False)

        self.preview.setOpenExternalLinks(False)
        self.preview.setOpenLinks(False)

        self.horiz_splitter.addWidget(self.editor)
        self.horiz_splitter.addWidget(self.preview)

        # Setup analyzation report
        self.analyzer_list = QListWidget()
        self.analyzer_list.setVisible(False)

        self.vert_splitter.addWidget(self.horiz_splitter)
        self.vert_splitter.addWidget(self.analyzer_list)

        # Add to tab layout
        self.layout.addWidget(self.vert_splitter)