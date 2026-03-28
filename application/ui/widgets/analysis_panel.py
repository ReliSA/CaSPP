"""
Analysis panel widget for displaying markdown analysis results.
"""
# third-party imports
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel

# local imports
from core.config import Config


class AnalysisPanel(QWidget):
    """Widget for displaying analysis results."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel("Analysis Report:")
        layout.addWidget(self.label)
        
        # Analysis display
        self.analysis_edit = QTextEdit()
        self.analysis_edit.setReadOnly(True)
        self.analysis_edit.setMaximumHeight(Config.ANALYSIS_PANEL_MAX_HEIGHT)
        layout.addWidget(self.analysis_edit)

    def set_analysis(self, analysis_report: str) -> None:
        """
        Display an analysis report.
        
        Args:
            analysis_report: The analysis report to display
        """
        self.analysis_edit.setMarkdown(analysis_report)

    def set_error(self, error_message: str) -> None:
        """
        Display an error message.
        
        Args:
            error_message: The error message to display
        """
        self.analysis_edit.setPlainText(error_message)

    def clear(self) -> None:
        """Clear the analysis display."""
        self.analysis_edit.clear()

    def set_loading(self) -> None:
        """Show a loading message."""
        self.analysis_edit.setPlainText("Analyzing markdown file...")
    
    def get_content(self) -> str:
        """Get the current analysis content."""
        return self.analysis_edit.toPlainText()
