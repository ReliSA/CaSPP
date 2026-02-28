"""
Main application window.
"""
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QApplication)

from ui.widgets.markdown_viewer import MarkdownViewer
from ui.widgets.analysis_panel import AnalysisPanel
from ui.widgets.toolbar import Toolbar
from core.config import Config


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Window configuration
        self.setWindowTitle(Config.APP_NAME)
        self.setMinimumSize(Config.WINDOW_MIN_WIDTH, Config.WINDOW_MIN_HEIGHT)
        self.resize(Config.WINDOW_DEFAULT_WIDTH, Config.WINDOW_DEFAULT_HEIGHT)
        
        # Create toolbar
        self.toolbar = Toolbar()
        self.addToolBar(self.toolbar)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create widgets
        self.markdown_viewer = MarkdownViewer()
        self.analysis_panel = AnalysisPanel()
        
        # Add widgets to main layout
        main_layout.addWidget(self.markdown_viewer)
        main_layout.addWidget(self.analysis_panel)

    
    def _connect_signals(self):
        """Connect widget signals."""
        # Connect markdown viewer content changes to analysis updates
        self.markdown_viewer.content_changed.connect(self._on_content_changed)
        
        # File selection from toolbar is handled directly by the Application class
    
    def _on_content_changed(self, content: str):
        """Handle markdown content changes."""
        # This could trigger re-analysis in the future
        pass
    
    def get_toolbar(self) -> Toolbar:
        """Get the toolbar widget."""
        return self.toolbar
    
    def get_markdown_viewer(self) -> MarkdownViewer:
        """Get the markdown viewer widget."""
        return self.markdown_viewer
    
    def get_analysis_panel(self) -> AnalysisPanel:
        """Get the analysis panel widget."""
        return self.analysis_panel
