"""
Application logic coordinator.
"""
# standard library imports
import sys
from typing import Optional

# third-party imports
from PyQt6.QtWidgets import QApplication

# local imports
from ui.main_window import MainWindow
from core.constants import FileConstants
from utils.markdown_parser import MarkdownParser
from utils.markdown_analyzer import MarkdownAnalyzer
from utils.template_parser import TemplateParser
from core.config import Config
from utils.file_helper import FileHelper
from core.file_manager import FileManager
from core.editor_manager import EditorManager
from utils.git import GitWorker
from utils.markdown_auto_stager import MarkdownAutoStager


class Application:
    """Main application class that coordinates business logic."""
    
    def __init__(self) -> None:
        # Initialize the application
        self.app = QApplication(sys.argv if 'sys' in globals() else [])

        # Initialize main window
        self.main_window = MainWindow()

        # Initialize core components
        self.markdown_analyzer = MarkdownAnalyzer(str(Config.get_base_path()))
        self.file_helper = FileHelper(str(Config.get_base_path()))
        self.template_loader = TemplateParser(str(Config.get_base_path() / FileConstants.TEMPLATES_PATH), self.file_helper)
        self.template_loader.parse()
        self.document_loader = MarkdownParser(str(Config.get_base_path() / FileConstants.CATALOGUE_PATH), self.file_helper)
        self.document_loader.parse_dir()
        self.auto_stager = MarkdownAutoStager(str(Config.get_base_path()))
        self.file_manager = FileManager(
            self.main_window,
            self.markdown_analyzer,
            self.file_helper,
            self.auto_stager,
            self.template_loader,
            self.document_loader
        )

        self.editor_manager = EditorManager(
            self.main_window.get_markdown_viewer()
        )

        self.git_worker: Optional[GitWorker] = None

        # Set up application logic and signal connections
        self._setup_application()

    def _setup_application(self) -> None:
        """Set up the application."""
        # Set up markdown viewer signals for auto-staging
        markdown_viewer = self.main_window.get_markdown_viewer()
        toolbar = self.main_window.get_toolbar()

        markdown_viewer.open_explorer_button.clicked.connect(
            self.file_manager.on_open_explorer_button_pressed
        )
        markdown_viewer.close_explorer_button.clicked.connect(
            self.file_manager.on_close_explorer_button_pressed
        )
        markdown_viewer.editor.textChanged.connect(
            self.file_manager.on_editor_text_changed
        )
        markdown_viewer.editor.textChanged.connect(
            self.editor_manager.update_live_preview
        )
        markdown_viewer.save_changes_button.clicked.connect(
            self.file_manager.save_current_markdown_file
        )
        markdown_viewer.file_tree_widget.itemDoubleClicked.connect(
            self.file_manager.on_explorer_item_activated
        )

        markdown_viewer.live_preview_check_box.stateChanged.connect(
            self.editor_manager.live_preview_check_box_state_changed
        )

        markdown_viewer.analyzer_check_box.stateChanged.connect(
            self.editor_manager.markdown_analyzer_check_box_state_changed
        )

        markdown_viewer.preview.anchorClicked.connect(
            self.file_manager.handle_link_clicked
        )

        toolbar.action_open_explorer.triggered.connect(
            self.file_manager.open_explorer
        )
        toolbar.action_save_file.triggered.connect(
            self.file_manager.save_current_markdown_file
        )
        toolbar.action_open_folder.triggered.connect(
            lambda _checked=False: self.file_manager.open_explorer_dialog("directory")
        )
        toolbar.action_open_file.triggered.connect(
            lambda _checked=False: self.file_manager.open_explorer_dialog("file")
        )
        toolbar.action_live_preview.triggered.connect(
            markdown_viewer.live_preview_check_box.toggle
        )

        toolbar.action_show_analyzer.triggered.connect(
            markdown_viewer.analyzer_check_box.toggle
        )

        git_viewer = self.main_window.get_git_viewer()
        git_viewer.btn_status.clicked.connect(lambda: self._start_git_operation("status"))
        git_viewer.btn_fetch.clicked.connect(lambda: self._start_git_operation("fetch"))
        git_viewer.btn_pull.clicked.connect(lambda: self._start_git_operation("pull"))
        git_viewer.btn_push.clicked.connect(lambda: self._start_git_operation("push"))
        toolbar.action_status.triggered.connect(lambda: self._start_git_operation("status"))
        toolbar.action_fetch.triggered.connect(lambda: self._start_git_operation("fetch"))
        toolbar.action_pull.triggered.connect(lambda: self._start_git_operation("pull"))
        toolbar.action_push.triggered.connect(lambda: self._start_git_operation("push"))

        self.auto_stager.file_staged.connect(self.file_manager.on_file_staged)
        self.auto_stager.staging_failed.connect(
            lambda file_path, error: self.main_window.get_git_viewer().append_output(
                f"Auto-stage failed for {file_path}: {error}"
            )
        )

        # Load default markdown file
        #self.file_manager.load_markdown_file(Config.get_default_markdown_path())
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Application exit code
        """
        self.main_window.show()
        return self.app.exec()

    def _start_git_operation(self, operation: str) -> None:
        """Run git operation in background and display output in git scene."""
        git_viewer = self.main_window.get_git_viewer()

        if self.git_worker is not None and self.git_worker.isRunning():
            git_viewer.append_output("Another git operation is already running.")
            return

        git_viewer.set_controls_enabled(False)
        git_viewer.set_output(f"Running git {operation}...")

        self.git_worker = GitWorker(operation=operation, repo_path=str(Config.get_base_path()))
        self.git_worker.finished.connect(
            lambda success, message, op=operation: self._on_git_operation_finished(op, success, message)
        )
        self.git_worker.start()

    def _on_git_operation_finished(self, operation: str, success: bool, message: str) -> None:
        """Update git scene after background operation completes."""
        git_viewer = self.main_window.get_git_viewer()
        status_prefix = "Success" if success else "Failed"
        git_viewer.set_output(f"{status_prefix}: {operation}\n\n{message}")
        git_viewer.set_controls_enabled(True)
        self.git_worker = None
    
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
