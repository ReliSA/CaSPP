"""
File-related operations extracted from Application.
"""
import logging
import os
from typing import Optional

# local imports
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

from ui.main_window import MainWindow
from core.analyzer.markdown_analyzer import MarkdownAnalyzer
from utils.file_helper import FileHelper
from utils.constants import FileConstants
from core.managers.tab_manager import TabManager
from core.managers.error_manager import safe_slot
from utils.git.markdown_auto_stager import MarkdownAutoStager
from utils.file_matcher import FileMatcher
from utils.exceptions import FileNotFoundError

logger = logging.getLogger(__name__)


class FileManager:
    """Handles loading and analyzing markdown files and related file events."""

    def __init__(
        self,
        main_window: MainWindow,
        tab_manager: TabManager,
        markdown_analyzer: MarkdownAnalyzer,
        file_helper: FileHelper,
        auto_stager: Optional[MarkdownAutoStager] = None,
        template_loader = None,
        document_loader = None
    ) -> None:
        """Initialize FileManager with required collaborators.

        Args:
            main_window: The application's MainWindow instance used to access UI components (viewer, analysis panel, toolbar, etc.).
            tab_manager: Manager for open tabs of markdown files.
            markdown_analyzer: Analyzer responsible for analyzing markdown content and producing reports.
            file_helper: Utility for validating and performing file I/O and dialogs.
            auto_stager: The auto stager value.
            template_loader: The template parser used to find matching templates.
            document_loader: The document loader value.
        """
        self.main_window = main_window
        self.tab_manager = tab_manager
        self.markdown_analyzer = markdown_analyzer
        self.file_helper = file_helper
        self.auto_stager = auto_stager
        self.current_file_path: Optional[str] = None
        self.current_file_content: Optional[str] = None
        self._is_loading_file = False
        self._is_dirty = False
        self.template_loader = template_loader
        self.document_loader = document_loader
        self.project_index = {}
        self.references_content: Optional[str] = None
        self.file_matcher = FileMatcher(self.template_loader) if self.template_loader else None
        self.current_explorer_dir = ""

    def load_templates(self, templates_dir: str) -> None:
        """Discover, read, and parse every template in *templates_dir*.

        Args:
            templates_dir: Directory that contains the ``.md`` template files.
        """
        if not self.template_loader:
            return

        filepaths = sorted(
            self.file_helper.find_markdown_files(templates_dir, recursive=False)
        )
        if not filepaths:
            logger.warning("No templates found in: %s", templates_dir)
            return

        for filepath in filepaths:
            content = self.file_helper.read_file(filepath)
            if content is None:
                logger.error("Failed to read template: %s", filepath)
                continue
            try:
                self.template_loader.parse_content(filepath, content)
            except Exception as exc:
                logger.error("Failed to parse template %s: %s", filepath, exc)

        logger.info(
            "Loaded %d template(s) from %s",
            len(self.template_loader.templates),
            templates_dir,
        )

    def load_markdown_file(self, file_path: str) -> None:
        """Load a markdown file into the tab manager and analyze it.

        Args:
            file_path: Path to the markdown file to load and analyze.
        """
        # Validate the file first using the FileHelper
        validated = self.file_helper.validate_file(file_path)
        if not validated:
            logger.warning("Load rejected (invalid or missing file): %s", file_path)
            self.tab_manager.set_error(
                "Cannot analyze - file not found or inaccessible."
            )
            return

        self._is_loading_file = True
        try:
            logger.info("Loading markdown file: %s", validated)
            content = self.file_helper.read_file(validated)
            if content is None:
                logger.error("Read failed for: %s", validated)
                self.tab_manager.set_error("Cannot analyze - failed to read file content.")
                return

            self.tab_manager.load_file_into_tab(validated, content)
            
            self.current_file_path = validated
            self.current_file_content = content
            self._is_dirty = False
            self.tab_manager.set_active_tab_file(validated)
            self.tab_manager.set_tab_dirty(False)
            self._analyze_current_file(validated, content)
        except Exception:
            logger.exception("Failed to load markdown file in viewer")
            self.tab_manager.set_error("Cannot analyze - failed to load file in viewer.")
        finally:
            self._is_loading_file = False

    def _analyze_current_file(self, file_path: str, content: str) -> None:
        """Analyze the currently loaded markdown file and update the analysis panel.

        Args:
            file_path: Path to the markdown file to analyze. The file is assumed to already be loaded into the viewer.
            content: In-memory markdown content supplied by FileManager.
        """
        try:
            self.tab_manager.set_loading()

            analysis = {"file": file_path, "warnings": [], "passed": []}

            if self.document_loader and self.template_loader:
                parsed_doc = self.document_loader.parse_content(file_path, content)

                self._update_project_index_entry(file_path, parsed_doc)

                template = self.file_matcher.match(file_path) if self.file_matcher else None
                if not template:
                    raise ValueError("Template matching failed for the document (It's possible that for this document, template just doesn't exist.")

                analysis = self.markdown_analyzer.validate_structure(parsed_doc, template, project_index=self.project_index, references_content=self.references_content)

            report = self.markdown_analyzer.generate_report(analysis)
            self.tab_manager.set_analysis(report)

        except Exception as e:
            logger.exception("Analysis failed for %s", file_path)
            error_msg = f"Error during analysis: {str(e)}"
            self.tab_manager.set_analysis(error_msg)

    def _update_project_index_entry(self, file_path: str, parsed_doc) -> None:
        """Refresh the project index entry for a single file after it has been edited.

        Args:
            file_path: Absolute path of the file that changed.
            parsed_doc: Already-parsed document, so we avoid reading the file again.
        """
        if not self.project_index or not self.document_loader:
            return
        filename = os.path.basename(file_path)
        try:
            metadata = self.document_loader.get_link_metadata(parsed_doc)
            self.project_index[filename] = {
                "full_path": file_path,
                "aliases": metadata["aliases"],
                "related": metadata["related_links"],
            }
        except Exception as e:
            logger.warning("Failed to update project index for %s: %s", filename, e)

    def on_file_saved(self, file_path: str, content: Optional[str] = None) -> None:
        """Handle file saved events and re-run analysis for markdown files.

        Args:
            file_path: Path to the file that was saved. If it ends with '.md' and is valid, the file will be re-analyzed.
            content: Optional in-memory content of the active editor.
        """
        # Validate before analyzing
        if file_path.lower().endswith(tuple(FileConstants.MARKDOWN_EXTENSIONS)) and self.file_helper.validate_file(file_path):
            file_content = content if content is not None else self.file_helper.read_file(file_path)
            if file_content is None:
                self.tab_manager.set_analysis("Cannot analyze - failed to read saved file content.")
                return

            self.current_file_path = file_path
            self.current_file_content = file_content
            self._analyze_current_file(file_path, file_content)

            if self.auto_stager and self.auto_stager.is_available():
                self.auto_stager.stage_file_delayed(file_path)

    def on_file_staged(self, file_path: str, message: str) -> None:
        """Handle file staged events (UI notification / logging).

        Args:
            file_path: Path to the staged file.
            message: Commit/stage message or description associated with the staging action.
        """
        self.main_window.get_git_viewer().append_output(
            f"Auto-staged: {file_path} ({message})"
        )
        logger.info("Auto-staged %s (%s)", file_path, message)

    def save_current_markdown_file(self) -> None:
        """Save current editor content and run post-save hooks.
        """
        content = self.tab_manager.get_editor_content()

        saved_file = self.file_helper.save_file(
            content=content,
            file_path=self.current_file_path,
            parent=self.main_window,
        )

        if saved_file:
            logger.info("Saved markdown file: %s", saved_file)
            self.current_file_path = saved_file
            self.current_file_content = content
            self._is_dirty = False
            self.tab_manager.set_active_tab_file(saved_file)
            self.tab_manager.set_tab_dirty(False)
            self.on_file_saved(saved_file, content)

    def on_editor_text_changed(self) -> None:
        """Mark current tab dirty when user edits loaded content.
        """
        if self._is_loading_file:
            return

        if not self._is_dirty:
            self._is_dirty = True
            self.tab_manager.set_tab_dirty(True)

    def open_explorer_dialog(self, selection_mode: str = "directory") -> None:
        """Open directory explorer or select and open a single markdown file.

        Args:
            selection_mode: Whether to select a file or directory.
        """
        if selection_mode == "file":
            selected_file = self.file_helper.select_markdown_file(
                parent=self.main_window,
                title="Open File"
            )

            if not selected_file:
                logger.info("UI: open file dialog cancelled")
                return

            logger.info("UI: open file — %s", selected_file)
            self.load_markdown_file(selected_file)
            return

        selected_directory = self.file_helper.select_directory(
            parent=self.main_window,
            title="Open Explorer"
        )

        if not selected_directory:
            logger.info("UI: open folder dialog cancelled")
            return

        logger.info("UI: opened project folder — %s", selected_directory)
        self.build_project_index(selected_directory)
        self.current_explorer_dir = selected_directory

        markdown_files = self.file_helper.find_markdown_files(
            directory=selected_directory,
            recursive=True,
        )

        self.main_window.get_markdown_viewer().populate_explorer(
            selected_directory,
            markdown_files,
        )

    def on_explorer_item_activated(self, item, _column: int) -> None:
        """Open markdown file when a file item is activated in explorer.

        Args:
            item: The activated tree item.
            _column: The activated tree column.
        """
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            logger.info("UI: explorer opened file — %s", file_path)
            self.load_markdown_file(file_path)

    @safe_slot
    def handle_link_clicked(self, url: QUrl) -> None:
        """Handle link clicks from the markdown preview.

        Args:
            url: The clicked or resolved URL.
        """
        
        if not self.current_file_path:
            return

        if url.scheme() in ('http', 'https'):
            logger.info("UI: preview opened external URL — %s", url.toString())
            QDesktopServices.openUrl(url)
            return
        
        link_path = url.toString()
        logger.info("UI: preview link follow — %s (from %s)", link_path, self.current_file_path)

        target_path = self.file_helper.resolve_relative_markdown_link(
            self.current_file_path, 
            link_path
        )

        if not target_path or not self.file_helper.validate_file(target_path):
            raise FileNotFoundError(link_path)

        self.load_markdown_file(target_path)
    
    def on_open_explorer_button_pressed(self) -> None:
        """Button listener for opening explorer.
        """
        self.open_explorer()

    def on_close_explorer_button_pressed(self) -> None:
        """Button listener for closing explorer.
        """
        self.close_explorer()

    def open_explorer(self) -> None:
        """Sets visibility of ui elements for open file explorer.
        """
        logger.info("UI: file explorer panel shown")
        markdown_scene = self.main_window.get_markdown_viewer()
        markdown_scene.close_explorer_button.setVisible(True)
        markdown_scene.open_explorer_button.setVisible(False)
        markdown_scene.file_explorer_widget.setVisible(True)
    
    def close_explorer(self) -> None:
        """Sets visibility of ui elements for closed file explorer.
        """
        logger.info("UI: file explorer panel hidden")
        markdown_scene = self.main_window.get_markdown_viewer()
        markdown_scene.close_explorer_button.setVisible(False)
        markdown_scene.open_explorer_button.setVisible(True)
        markdown_scene.file_explorer_widget.setVisible(False)

    def on_tab_changed(self) -> None:
        """Syncs the FileManager's tracked file path and save state with the currently focused tab.
        """
        state = self.tab_manager.get_current_state()
        if not state:
            self.current_file_path = None
            self.current_file_content = None
            self._is_dirty = False
            return
        
        self.current_file_path = state.file_path
        self.current_file_content = self.tab_manager.get_editor_content() if state.file_path else None
        self._is_dirty = state.is_dirty

    def build_project_index(self, root_dir: str) -> None:
        """
        Builds a project-wide index of aliases and links for cross-validation.

        Args:
            root_dir: The root directory to scan for markdown files.
        """
        if not self.document_loader:
            return

        self.project_index = {}
        self.references_content = None
        all_files = self.file_helper.find_markdown_files(root_dir, recursive=True)

        logger.info("Indexing project files for link validation...")
        for path in all_files:
            filename = os.path.basename(path)
            content = self.file_helper.read_file(path)

            if filename.lower() == 'references.md':
                self.references_content = content
                continue

            if content:
                try:
                    doc = self.document_loader.parse_content(path, content)
                    metadata = self.document_loader.get_link_metadata(doc)

                    self.project_index[filename] = {
                        "full_path": path,
                        "aliases": metadata["aliases"],
                        "related": metadata["related_links"]
                    }
                except Exception as e:
                    logger.error(f"Failed to index {filename}: {e}")

        logger.info(f"Project indexed: {len(self.project_index)} files processed.")
