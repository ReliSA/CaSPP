"""
Auto-staging utility for markdown files.
Handles automatic staging of edited markdown files in git repository.
"""

# standard library imports
import logging
from typing import Optional, Callable

# third-party imports
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

# local imports
from utils.git.runner import is_repo_available
from utils.git.stage import stage_file, stage_markdown_files
from utils.constants import FileConstants

logger = logging.getLogger(__name__)


class MarkdownAutoStager(QObject):
    """
    Handles automatic staging of edited markdown files.
    
    This class monitors for markdown file changes and automatically stages them
    when they are saved using a simple, synchronous approach to avoid threading issues.
    
    Signals:
        file_staged: Emitted when a file is successfully staged (file_path: str, message: str)
        staging_failed: Emitted when staging fails (file_path: str, error: str)
    """
    
    # Signals
    file_staged = pyqtSignal(str, str)  # file_path, message
    staging_failed = pyqtSignal(str, str)  # file_path, error
    
    def __init__(self, repo_path: Optional[str] = None, 
                 auto_stage_delay: int = 1000) -> None:
        """Initialize the auto-stager.

        Args:
            repo_path: Path to git repository. If None, will search for repo.
            auto_stage_delay: Delay in milliseconds before staging files (default: 1000ms).
        """
        super().__init__()
        self.repo_path = repo_path
        self.auto_stage_delay = auto_stage_delay
        
        # Queue of files pending staging
        self._pending_files = set()
        
        # Timer for delayed staging
        self._staging_timer = QTimer()
        self._staging_timer.timeout.connect(self._process_pending_files)
        self._staging_timer.setSingleShot(True)
        
        # Check if git is available
        self._git_available = self._check_git_availability()
        
        # Callbacks for external integration
        self._on_stage_success: Optional[Callable[[str, str], None]] = None
        self._on_stage_failure: Optional[Callable[[str, str], None]] = None
    
    def _check_git_availability(self) -> bool:
        """Check if git repository is available.

        Returns:
            The boolean result.
        """
        try:
            return is_repo_available(self.repo_path)
        except Exception:
            logger.warning("Git repository not available for auto-staging")
            return False

    def _is_markdown_file(self, file_path: str) -> bool:
        """Return True if path points to supported markdown extension.

        Args:
            file_path: The file path to process.

        Returns:
            The boolean result.
        """
        return file_path.lower().endswith(tuple(FileConstants.MARKDOWN_EXTENSIONS))
    
    def is_available(self) -> bool:
        """Check if auto-staging is available.

        Returns:
            The boolean result.
        """
        return self._git_available
    
    def set_callbacks(self, 
                     on_success: Optional[Callable[[str, str], None]] = None,
                     on_failure: Optional[Callable[[str, str], None]] = None) -> None:
        """Set callback functions for staging events.

        Args:
            on_success: Called when staging succeeds (file_path, message).
            on_failure: Called when staging fails (file_path, error).
        """
        self._on_stage_success = on_success
        self._on_stage_failure = on_failure
    
    def stage_file_immediately(self, file_path: str) -> None:
        """Stage a markdown file immediately using synchronous approach.

        Args:
            file_path: Path to the markdown file to stage.
        """
        if not self._git_available:
            logger.debug(f"Git not available, skipping staging of {file_path}")
            return
        
        if not self._is_markdown_file(file_path):
            logger.debug(f"Not a markdown file, skipping staging of {file_path}")
            return
        
        try:
            result = stage_file(self.repo_path or "", file_path)
            self._on_stage_complete(file_path, result.success, result.message)
        except Exception as e:
            logger.error(f"Error staging file immediately: {e}")
            self._on_stage_complete(file_path, False, str(e))
    
    def stage_file_delayed(self, file_path: str) -> None:
        """Stage a markdown file with configurable delay.

        Args:
            file_path: Path to the markdown file to stage.
        """
        if not self._git_available:
            logger.debug(f"Git not available, skipping staging of {file_path}")
            return
        
        if not self._is_markdown_file(file_path):
            logger.debug(f"Not a markdown file, skipping staging of {file_path}")
            return
        
        # Add to pending files and restart timer
        self._pending_files.add(file_path)
        self._staging_timer.start(self.auto_stage_delay)
        logger.debug(f"Added {file_path} to pending staging queue")
    
    def _process_pending_files(self) -> None:
        """Process all files in the pending queue synchronously.
        """
        if not self._pending_files:
            return
        
        files_to_stage = list(self._pending_files)
        self._pending_files.clear()
        
        logger.info(f"Processing {len(files_to_stage)} pending files for staging")
        
        try:
            result = stage_markdown_files(self.repo_path or "", files_to_stage)
            if result.success:
                logger.info(f"Successfully staged {len(files_to_stage)} markdown files")
                for file_path in files_to_stage:
                    self.file_staged.emit(file_path, f"Staged with {len(files_to_stage)} other files")
            else:
                logger.warning(f"Failed to stage markdown files: {result.message}")
                for file_path in files_to_stage:
                    self.staging_failed.emit(file_path, result.message)
        except Exception as e:
            logger.error(f"Error processing pending files: {e}")
            # Emit failure for all files
            for file_path in files_to_stage:
                self.staging_failed.emit(file_path, str(e))
    
    def _on_stage_complete(self, file_path: str, success: bool, message: str) -> None:
        """Handle completion of file staging.

        Args:
            file_path: The file path to process.
            success: Whether the operation completed successfully.
            message: The message to display or use for the operation.
        """
        if success:
            logger.info(f"Successfully staged: {file_path}")
            self.file_staged.emit(file_path, message)
            if self._on_stage_success:
                self._on_stage_success(file_path, message)
        else:
            logger.warning(f"Failed to stage {file_path}: {message}")
            self.staging_failed.emit(file_path, message)
            if self._on_stage_failure:
                self._on_stage_failure(file_path, message)
    
    def flush_pending(self) -> None:
        """Immediately process any pending files.
        """
        if self._staging_timer.isActive():
            self._staging_timer.stop()
            self._process_pending_files()
    
    def clear_pending(self) -> None:
        """Clear all pending files without staging them.
        """
        self._pending_files.clear()
        if self._staging_timer.isActive():
            self._staging_timer.stop()
        logger.debug("Cleared all pending files")
    
    def get_pending_count(self) -> int:
        """Get the number of files pending staging.

        Returns:
            The integer result.
        """
        return len(self._pending_files)
    
    def enable_auto_staging(self, enabled: bool = True) -> None:
        """Enable or disable auto-staging functionality.

        Args:
            enabled: Whether to enable auto-staging.
        """
        if not enabled:
            self.clear_pending()
        
        self._git_available = enabled and self._check_git_availability()
        logger.info(f"Auto-staging {'enabled' if self._git_available else 'disabled'}")
    
    def cleanup(self) -> None:
        """Clean up the auto-stager.
        """
        self.clear_pending()
        logger.debug("Auto-stager cleaned up")
