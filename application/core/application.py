"""
Application logic coordinator.
"""
from PyQt6.QtWidgets import QApplication
import sys
from pathlib import Path

from ui.main_window import MainWindow
from utils.markdown_analyzer import MarkdownAnalyzer
from core.config import Config


class Application:
    """Main application class that coordinates business logic."""
    
    def __init__(self):
        self.app = QApplication(sys.argv if 'sys' in globals() else [])
        self.main_window = MainWindow()
        self.markdown_analyzer = MarkdownAnalyzer(str(Config.get_base_path()))
        self._setup_application()
    
    def _setup_application(self):
        """Set up the application."""
        # Set up toolbar file selection signal
        self.main_window.get_toolbar().file_selected.connect(self.load_markdown_file)
        
        # Load default markdown file
        self.load_markdown_file(Config.get_default_markdown_path())
    
    def load_markdown_file(self, file_path: str):
        """
        Load and analyze a markdown file.
        
        Args:
            file_path: Path to the markdown file to load
        """
        # Load file in markdown viewer
        success = self.main_window.get_markdown_viewer().load_file(file_path)
        
        if success:
            # Perform analysis
            self._analyze_current_file(file_path)
        else:
            # Show error in analysis panel
            self.main_window.get_analysis_panel().set_error(
                "Cannot analyze - file not found."
            )
    
    def _analyze_current_file(self, file_path: str):
        """
        Analyze the currently loaded markdown file.
        
        Args:
            file_path: Path to the file to analyze
        """
        try:
            # Show loading state
            self.main_window.get_analysis_panel().set_loading()
            
            # Perform analysis
            analysis = self.markdown_analyzer.analyze_markdown_file(file_path)
            report = self.markdown_analyzer.generate_report(analysis)
            
            # Display results
            self.main_window.get_analysis_panel().set_analysis(report)
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            self.main_window.get_analysis_panel().set_error(error_msg)
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Application exit code
        """
        self.main_window.show()
        return self.app.exec()
    
    def get_main_window(self) -> MainWindow:
        """Get the main window instance."""
        return self.main_window
    
    def get_analyzer(self) -> MarkdownAnalyzer:
        """Get the markdown analyzer instance."""
        return self.markdown_analyzer
