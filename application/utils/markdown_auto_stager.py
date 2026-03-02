"""
Auto-staging utility for markdown files.
Handles automatic staging of edited markdown files in git repository.
"""
import logging
from pathlib import Path
from typing import Optional, Callable
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from utils.git import GitHelper, GitWorker
from utils.exceptions import GitRepositoryNotFoundError, GitLibraryNotAvailableError

logger = logging.getLogger(__name__)


class MarkdownAutoStager(QObject):
    """
    Handles automatic staging of edited markdown files.
    
    This class monitors for markdown file changes and automatically stages them
    when they are saved. It provides both immediate staging and batched staging
    with configurable delay to avoid excessive git operations.
    
    Signals:
        file_staged: Emitted when a file is successfully staged (file_path: str, message: str)
        staging_failed: Emitted when staging fails (file_path: str, error: str)
        batch_staged: Emitted when multiple files are staged (count: int, message: str)
    """
    
    # Signals
    file_staged = pyqtSignal(str, str)  # file_path, message
    staging_failed = pyqtSignal(str, str)  # file_path, error
    batch_staged = pyqtSignal(int, str)  # count, message
    
    def __init__(self, repo_path: Optional[str] = None, 
                 auto_stage_delay: int = 2000, 
                 batch_staging: bool = True):
        """
        Initialize the auto-stager.
        
        Args:
            repo_path: Path to git repository. If None, will search for repo.
            auto_stage_delay: Delay in milliseconds before staging files (default: 2000ms)
            batch_staging: Whether to batch multiple file changes together (default: True)
        """
        super().__init__()
        self.repo_path = repo_path
        self.auto_stage_delay = auto_stage_delay
        self.batch_staging = batch_staging
        
        # Queue of files pending staging
        self._pending_files = set()
        
        # Timer for batched staging
        self._staging_timer = QTimer()
        self._staging_timer.timeout.connect(self._process_pending_files)
        self._staging_timer.setSingleShot(True)
        
        # Keep track of active workers to clean them up properly
        self._active_workers = []
        
        # Check if git is available
        self._git_available = self._check_git_availability()
        
        # Callbacks for external integration
        self._on_stage_success: Optional[Callable[[str, str], None]] = None
        self._on_stage_failure: Optional[Callable[[str, str], None]] = None
    
    def _check_git_availability(self) -> bool:
        """Check if git repository is available."""
        try:
            with GitHelper(self.repo_path) as helper:
                return helper.is_repo_available()
        except (GitRepositoryNotFoundError, GitLibraryNotAvailableError):
            logger.warning("Git repository not available for auto-staging")
            return False
        except Exception as e:
            logger.warning(f"Error checking git availability: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if auto-staging is available."""
        return self._git_available
    
    def set_callbacks(self, 
                     on_success: Optional[Callable[[str, str], None]] = None,
                     on_failure: Optional[Callable[[str, str], None]] = None):
        """
        Set callback functions for staging events.
        
        Args:
            on_success: Called when staging succeeds (file_path, message)
            on_failure: Called when staging fails (file_path, error)
        """
        self._on_stage_success = on_success
        self._on_stage_failure = on_failure
    
    def stage_file_immediately(self, file_path: str) -> None:
        """
        Stage a markdown file immediately.
        
        Args:
            file_path: Path to the markdown file to stage
        """
        if not self._git_available:
            logger.debug(f"Git not available, skipping staging of {file_path}")
            return
        
        if not file_path.endswith('.md'):
            logger.debug(f"Not a markdown file, skipping staging of {file_path}")
            return
        
        # Use GitWorker for non-blocking operation
        worker = GitWorker("stage_file", self.repo_path or "", file_path=file_path)
        worker.finished.connect(lambda success, message: self._on_stage_complete(file_path, success, message))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()
    
    def stage_file_delayed(self, file_path: str) -> None:
        """
        Stage a markdown file with configurable delay (for batching).
        
        Args:
            file_path: Path to the markdown file to stage
        """
        if not self._git_available:
            logger.debug(f"Git not available, skipping staging of {file_path}")
            return
        
        if not file_path.endswith('.md'):
            logger.debug(f"Not a markdown file, skipping staging of {file_path}")
            return
        
        if self.batch_staging:
            # Add to pending files and restart timer
            self._pending_files.add(file_path)
            self._staging_timer.start(self.auto_stage_delay)
            logger.debug(f"Added {file_path} to pending staging queue")
        else:
            # Stage immediately
            self.stage_file_immediately(file_path)
    
    def _process_pending_files(self) -> None:
        """Process all files in the pending queue."""
        if not self._pending_files:
            return
        
        files_to_stage = list(self._pending_files)
        self._pending_files.clear()
        
        logger.info(f"Processing {len(files_to_stage)} pending files for staging")
        
        # Use GitWorker for non-blocking batch operation
        worker = GitWorker("stage_markdown", self.repo_path or "", file_paths=files_to_stage)
        worker.finished.connect(lambda success, message: self._on_batch_complete(len(files_to_stage), success, message))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()
    
    def _cleanup_worker(self, worker):
        """Clean up a finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
    
    def _on_stage_complete(self, file_path: str, success: bool, message: str) -> None:
        """Handle completion of single file staging."""
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
    
    def _on_batch_complete(self, file_count: int, success: bool, message: str) -> None:
        """Handle completion of batch staging."""
        if success:
            logger.info(f"Successfully staged {file_count} markdown files")
            self.batch_staged.emit(file_count, message)
        else:
            logger.warning(f"Failed to stage markdown files: {message}")
            # For batch operations, we emit a general staging failure
            self.staging_failed.emit(f"{file_count} files", message)
    
    def flush_pending(self) -> None:
        """Immediately process any pending files."""
        if self._staging_timer.isActive():
            self._staging_timer.stop()
            self._process_pending_files()
    
    def clear_pending(self) -> None:
        """Clear all pending files without staging them."""
        self._pending_files.clear()
        if self._staging_timer.isActive():
            self._staging_timer.stop()
        logger.debug("Cleared all pending files")
    
    def cleanup(self) -> None:
        """Clean up all resources and stop any running operations."""
        # Clear pending files
        self.clear_pending()
        
        # Stop and clean up all active workers
        for worker in self._active_workers[:]:  # Copy list to avoid modification during iteration
            if worker.isRunning():
                worker.terminate()
                worker.wait(1000)  # Wait up to 1 second for graceful termination
            worker.deleteLater()
        self._active_workers.clear()
        
        logger.debug("Auto-stager cleanup completed")
    
    def get_pending_count(self) -> int:
        """Get the number of files pending staging."""
        return len(self._pending_files)
    
    def enable_auto_staging(self, enabled: bool = True) -> None:
        """
        Enable or disable auto-staging functionality.
        
        Args:
            enabled: Whether to enable auto-staging
        """
        if not enabled:
            self.clear_pending()
        
        self._git_available = enabled and self._check_git_availability()
        logger.info(f"Auto-staging {'enabled' if self._git_available else 'disabled'}")
