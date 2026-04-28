"""
Application logic coordinator.
"""
# standard library imports
import sys

# third-party imports
from PyQt6.QtWidgets import QApplication

# local imports
from ui.main_window import MainWindow
from core.constants import FileConstants, AssetsConstants
from utils.markdown_parser import MarkdownParser
from utils.markdown_analyzer import MarkdownAnalyzer
from utils.template_parser import TemplateParser
from core.config import Config
from utils.file_helper import FileHelper
from core.file_manager import FileManager
from core.editor_manager import EditorManager
from core.tab_manager import TabManager
from core.git_manager import GitManager
from core.error_manager import ErrorManager
from utils.markdown_auto_stager import MarkdownAutoStager

class Application:
    """Main application class that coordinates business logic."""
    
    def __init__(self) -> None:
        # Initialize the application
        self.app = QApplication(sys.argv if 'sys' in globals() else [])

        # Initialize app theme
        self.app.setStyle("Fusion") 
        try:
            with open(AssetsConstants.APP_THEME_QSS_PATH, "r", encoding="utf-8") as f:
                qss_content = f.read()
                qss_content = qss_content.replace("{{ICONS_DIR}}", AssetsConstants.ICONS_DIR_QSS)
                self.app.setStyleSheet(qss_content)
        except Exception as e:
            print(f"Warning: Could not load stylesheet from {AssetsConstants.APP_THEME_QSS_PATH}: {e}")

        # Initialize main window
        self.main_window = MainWindow()

        # Initialize core components
        self.markdown_analyzer = MarkdownAnalyzer(str(Config.get_base_path()))
        
        # Initialize tab manager
        self.tab_manager = TabManager(self.main_window.get_markdown_viewer())

        # Initialize file helper and file manager
        self.file_helper = FileHelper(str(Config.get_base_path()))
        self.template_loader = TemplateParser(str(Config.get_base_path() / FileConstants.TEMPLATES_PATH), self.file_helper)
        self.template_loader.parse()
        self.document_loader = MarkdownParser(str(Config.get_base_path() / FileConstants.CATALOGUE_PATH), self.file_helper)
        self.document_loader.parse_dir()
        self.auto_stager = MarkdownAutoStager(str(Config.get_base_path()))
        self.file_manager = FileManager(
            self.main_window,
            self.tab_manager,
            self.markdown_analyzer,
            self.file_helper,
            self.auto_stager,
            self.template_loader,
            self.document_loader
        )

        # Initialize editor manager
        self.editor_manager = EditorManager(
            self.tab_manager
        )

        self.git_manager = GitManager(repo_path=str(Config.get_base_path()))

        self.error_manager = ErrorManager(self.main_window)
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

        markdown_viewer.tabs.tabCloseRequested.connect(
            self.tab_manager.close_tab
        )
        markdown_viewer.tabs.currentChanged.connect(
            self._on_tab_switched
        )
        self.tab_manager.on_editor_text_changed_callback = self._on_editor_text_changed
        self.tab_manager.on_preview_anchor_clicked_callback = self.file_manager.handle_link_clicked
        
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
        git_viewer.btn_status.clicked.connect(self.git_manager.status)
        git_viewer.btn_fetch.clicked.connect(self.git_manager.fetch)
        git_viewer.btn_pull.clicked.connect(self.git_manager.pull)
        git_viewer.btn_push.clicked.connect(self._push_with_custom_message)
        git_viewer.btn_export_staged.clicked.connect(self.git_manager.export_staged)
        toolbar.action_status.triggered.connect(self.git_manager.status)
        toolbar.action_fetch.triggered.connect(self.git_manager.fetch)
        toolbar.action_pull.triggered.connect(self.git_manager.pull)
        toolbar.action_push.triggered.connect(self._push_with_custom_message)
        toolbar.action_export_staged.triggered.connect(self.git_manager.export_staged)

        self.git_manager.operation_started.connect(self._on_git_operation_started)
        self.git_manager.operation_output.connect(self._on_git_operation_output)
        self.git_manager.operation_finished.connect(self._on_git_operation_finished)

        self.auto_stager.file_staged.connect(self.file_manager.on_file_staged)
        self.auto_stager.staging_failed.connect(
            lambda file_path, error: self.main_window.get_git_viewer().append_output(
                f"Auto-stage failed for {file_path}: {error}"
            )
        )

        # Load default markdown file
        #self.file_manager.load_markdown_file(Config.get_default_markdown_path())

    def _on_editor_text_changed(self) -> None:
        """Wrapper to trigger multiple updates when a tab's text changes.
        
        Returns:
            None.
        """
        self.file_manager.on_editor_text_changed()
        self.editor_manager.update_live_preview()

    def _on_tab_switched(self) -> None:
        """Wrapper to trigger updates when switching between tabs."""
        self.file_manager.on_tab_changed()
        self.editor_manager.update_live_preview()

    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Application exit code
        """
        self.main_window.show()
        return self.app.exec()

    def _on_git_operation_started(self, operation: str) -> None:
        """Update UI when git operation starts."""
        git_viewer = self.main_window.get_git_viewer()
        git_viewer.set_controls_enabled(False)
        git_viewer.set_output(f"Running git {operation}...")

    def _on_git_operation_output(self, operation: str, message: str) -> None:
        """Append manager output to git scene."""
        git_viewer = self.main_window.get_git_viewer()
        git_viewer.append_output(message)

    def _on_git_operation_finished(self, operation: str, success: bool, message: str) -> None:
        """Update git scene after background operation completes."""
        git_viewer = self.main_window.get_git_viewer()
        status_prefix = "Success" if success else "Failed"
        git_viewer.set_output(f"{status_prefix}: {operation}\n\n{message}")
        git_viewer.set_controls_enabled(True)

    def _push_with_custom_message(self) -> None:
        """Prompt for commit message and run push operation."""
        git_viewer = self.main_window.get_git_viewer()
        message, accepted = git_viewer.ask_push_commit_message()
        if not accepted:
            git_viewer.append_output("Push cancelled.")
            return

        self.git_manager.push(message=message)
    
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
