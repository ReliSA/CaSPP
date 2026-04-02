"""
Application logic coordinator.
"""
# standard library imports
import sys

# third-party imports
from PyQt6.QtWidgets import QApplication

# local imports
from ui.main_window import MainWindow
from core.constants import FileConstants
from utils.document_loader import DocumentLoader
from utils.markdown_analyzer import MarkdownAnalyzer
from utils.template_loader import TemplateLoader
from core.config import Config
from application.utils.file_helper import FileHelper
from core.file_manager import FileManager


class Application:
    """Main application class that coordinates business logic."""
    
    def __init__(self) -> None:
        # Initialize the application
        self.app = QApplication(sys.argv if 'sys' in globals() else [])

        # Initialize main window
        self.main_window = MainWindow()

        # Initialize core components
        self.markdown_analyzer = MarkdownAnalyzer(str(Config.get_base_path()))
        self.template_loader = TemplateLoader(str(Config.get_base_path() / FileConstants.TEMPLATES_PATH))
        self.template_loader.load()
        self.document_loader = DocumentLoader()
        self.document_loader.load_dir(str(Config.get_base_path() / FileConstants.CATALOGUE_PATH))

        # Initialize file helper and file manager
        self.file_helper = FileHelper(str(Config.get_base_path()))
        self.file_manager = FileManager(self.main_window, self.markdown_analyzer, self.file_helper)

        # Set up application logic and signal connections
        self._setup_application()

    def _setup_application(self) -> None:
        """Set up the application."""
        # Set up toolbar file selection signal
        self.main_window.get_toolbar().file_selected.connect(self.file_manager.load_markdown_file)
        
        # Set up markdown viewer signals for auto-staging
        markdown_viewer = self.main_window.get_markdown_viewer()
        markdown_viewer.file_saved.connect(self.file_manager.on_file_saved)
        markdown_viewer.file_staged.connect(self.file_manager.on_file_staged)
        
        # Load default markdown file
        self.file_manager.load_markdown_file(Config.get_default_markdown_path())
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Application exit code
        """
        self.main_window.show()
        return self.app.exec()
    
    def get_main_window(self) -> MainWindow:
        """
        Get the main window instance.

        Returns:
            The MainWindow instance of the application.
        
        """
        return self.main_window
    
    def get_analyzer(self) -> MarkdownAnalyzer:
        """Get the markdown analyzer instance.

        Returns:
            The MarkdownAnalyzer instance of the application.
        """
        return self.markdown_analyzer
