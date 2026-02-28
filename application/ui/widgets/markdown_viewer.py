"""
Markdown viewer widget for displaying markdown content.
"""
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import pyqtSignal
from typing import Optional


class MarkdownViewer(QWidget):
    """Custom widget for viewing markdown content."""
    
    # Signal emitted when file content changes
    content_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_file_path = None
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel("Markdown Content:")
        layout.addWidget(self.label)
        
        # Text edit
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        
        # Connect signals
        self.text_edit.textChanged.connect(self._on_text_changed)
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a markdown file and display its content.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.set_content(content)
                self._current_file_path = file_path
                return True
        except FileNotFoundError:
            self.set_error("Markdown file not found. Please check the file path.")
            return False
        except Exception as e:
            self.set_error(f"Error loading file: {str(e)}")
            return False
    
    def set_content(self, content: str):
        """Set the markdown content to display."""
        self.text_edit.setPlainText(content)
    
    def set_error(self, error_message: str):
        """Display an error message."""
        self.text_edit.setPlainText(error_message)
    
    def get_content(self) -> str:
        """Get the current content."""
        return self.text_edit.toPlainText()
    
    def set_read_only(self, read_only: bool):
        """Set whether the text edit is read-only."""
        self.text_edit.setReadOnly(read_only)
    
    def get_current_file_path(self) -> Optional[str]:
        """Get the path of the currently loaded file."""
        return self._current_file_path
    
    def _on_text_changed(self):
        """Handle text change events."""
        if self._current_file_path:
            self.content_changed.emit(self.get_content())
