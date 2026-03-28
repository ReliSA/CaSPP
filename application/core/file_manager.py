"""
File-related operations extracted from Application.
"""
# local imports
from ui.main_window import MainWindow
from utils.markdown_analyzer import MarkdownAnalyzer
from application.utils.file_helper import FileHelper


class FileManager:
    """Handles loading and analyzing markdown files and related file events."""

    def __init__(self, main_window: MainWindow, markdown_analyzer: MarkdownAnalyzer, file_helper: FileHelper) -> None:
        """Initialize FileManager with required collaborators.

        Args:
            main_window: The application's MainWindow instance used to access
                UI components (viewer, analysis panel, toolbar, etc.).
            markdown_analyzer: Analyzer responsible for analyzing markdown
                content and producing reports.
            file_helper: Utility for validating and performing file I/O and
                dialogs.
        """
        self.main_window = main_window
        self.markdown_analyzer = markdown_analyzer
        self.file_helper = file_helper

    def load_markdown_file(self, file_path: str) -> None:
        """Load a markdown file into the viewer and analyze it.

        Args:
            file_path: Path to the markdown file to load and analyze.

        Returns:
            None. Updates the UI (viewer and analysis panel) or shows an
            error message on failure.
        """
        # Validate the file first using the FileHelper
        validated = self.file_helper.validate_file(file_path)
        if not validated:
            self.main_window.get_analysis_panel().set_error(
                "Cannot analyze - file not found or inaccessible."
            )
            return

        success = self.main_window.get_markdown_viewer().load_file(file_path)
        if success:
            self._analyze_current_file(file_path)
        else:
            self.main_window.get_analysis_panel().set_error(
                "Cannot analyze - failed to load file in viewer."
            )

    def _analyze_current_file(self, file_path: str) -> None:
        """Analyze the currently loaded markdown file and update the analysis panel.

        Args:
            file_path: Path to the markdown file to analyze. The file is assumed
                to already be loaded into the viewer.

        Returns:
            None. Updates analysis panel with loading state, analysis results
            or error message on exception.
        """
        try:
            self.main_window.get_analysis_panel().set_loading()

            # Use the analyzer which expects a file path
            analysis = self.markdown_analyzer.analyze_markdown_file(file_path)
            report = self.markdown_analyzer.generate_report(analysis)

            self.main_window.get_analysis_panel().set_analysis(report)

        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            self.main_window.get_analysis_panel().set_error(error_msg)

    def on_file_saved(self, file_path: str) -> None:
        """Handle file saved events and re-run analysis for markdown files.

        Args:
            file_path: Path to the file that was saved. If it ends with
                '.md' and is valid, the file will be re-analyzed.

        Returns:
            None. Triggers analysis when appropriate.
        """
        # Validate before analyzing
        if file_path.endswith('.md') and self.file_helper.validate_file(file_path):
            self._analyze_current_file(file_path)

    def on_file_staged(self, file_path: str, message: str) -> None:
        """Handle file staged events (UI notification / logging).

        Args:
            file_path: Path to the staged file.
            message: Commit/stage message or description associated with the staging action.

        Returns:
            None. Currently logs to stdout; can be extended to show UI notifications.
        """
        # Placeholder for future UI notifications; keep simple for now
        print(f"File staged: {file_path} - {message}")
