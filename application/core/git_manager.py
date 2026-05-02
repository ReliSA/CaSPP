"""Git manager orchestrating threaded git operations for UI."""

from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from core.constants import GitConstants
from utils.git import commit as commit_operation
from utils.git import export_staged_files_zip as export_staged_files_zip_operation
from utils.git import fetch as fetch_operation
from utils.git import get_status_detailed
from utils.git import pull as pull_operation
from utils.git import push_markdown_changes
from utils.git import stage_file as stage_file_operation
from utils.git import stage_markdown_files as stage_markdown_files_operation
from utils.git import unstage_all as unstage_all_operation
from utils.git.types import GitResult


class GitOperationWorker(QThread):
    """Thread worker that executes a single git operation."""

    finished = pyqtSignal(str, bool, str, object)

    def __init__(self, operation: str, repo_path: str, **kwargs: Any) -> None:
        """Initialize the object with required collaborators.

        Args:
            operation: The git operation name.
            repo_path: The git repository path.
            **kwargs: The kwargs value.
        """
        super().__init__()
        self.operation = operation
        self.repo_path = repo_path
        self.kwargs = kwargs

    def run(self) -> None:
        """Dispatch the operation and emit a normalized result.
        """
        result = self._dispatch()
        self.finished.emit(self.operation, result.success, result.message, result.payload)

    def _dispatch(self) -> GitResult:
        """Dispatch the configured git operation.

        Returns:
            The git operation result.
        """
        if self.operation == "status":
            return get_status_detailed(self.repo_path, markdown_only=True)
        if self.operation == "fetch":
            return fetch_operation(self.repo_path)
        if self.operation == "pull":
            return pull_operation(self.repo_path)
        if self.operation == "push":
            return push_markdown_changes(
                self.repo_path,
                commit_message=self.kwargs.get("message", GitConstants.DEFAULT_COMMIT_MESSAGE),
                remote_name=self.kwargs.get("remote"),
                branch=self.kwargs.get("branch"),
            )
        if self.operation == "stage_file":
            return stage_file_operation(self.repo_path, self.kwargs.get("file_path", ""))
        if self.operation == "stage_markdown":
            return stage_markdown_files_operation(self.repo_path, self.kwargs.get("file_paths"))
        if self.operation == "unstage_all":
            return unstage_all_operation(self.repo_path)
        if self.operation == "commit":
            return commit_operation(
                self.repo_path,
                self.kwargs.get("message", GitConstants.DEFAULT_COMMIT_MESSAGE),
                stage_all=bool(self.kwargs.get("stage_all", False)),
            )
        if self.operation == "export_staged":
            return export_staged_files_zip_operation(
                self.repo_path,
                self.kwargs.get("output_zip_path"),
            )

        return GitResult(False, f"Unknown operation: {self.operation}")


class GitManager(QObject):
    """UI-facing git orchestration layer with a single concurrency boundary."""

    operation_started = pyqtSignal(str)
    operation_output = pyqtSignal(str, str)
    operation_finished = pyqtSignal(str, bool, str)
    status_updated = pyqtSignal(dict)

    def __init__(self, repo_path: str) -> None:
        """Initialize the object with required collaborators.

        Args:
            repo_path: The git repository path.
        """
        super().__init__()
        self.repo_path = repo_path
        self._worker: Optional[GitOperationWorker] = None

    def is_busy(self) -> bool:
        """Return True when an operation is already running.

        Returns:
            The boolean result.
        """
        return self._worker is not None and self._worker.isRunning()

    def start_operation(self, operation: str, **kwargs: Any) -> bool:
        """Start a git operation in background thread.

        Args:
            operation: The git operation name.
            **kwargs: The kwargs value.

        Returns:
            The boolean result.
        """
        if self.is_busy():
            self.operation_output.emit(operation, "Another git operation is already running.")
            return False

        self._worker = GitOperationWorker(operation=operation, repo_path=self.repo_path, **kwargs)
        self._worker.finished.connect(self._on_operation_finished)
        self.operation_started.emit(operation)
        self._worker.start()
        return True

    def status(self) -> bool:
        """Start a git status operation.

        Returns:
            The boolean result.
        """
        return self.start_operation("status")

    def fetch(self) -> bool:
        """Start a git fetch operation.

        Returns:
            The boolean result.
        """
        return self.start_operation("fetch")

    def pull(self) -> bool:
        """Start a git pull operation.

        Returns:
            The boolean result.
        """
        return self.start_operation("pull")

    def push(self, message: Optional[str] = None, remote: Optional[str] = None, branch: Optional[str] = None) -> bool:
        """Start a git push operation.

        Args:
            message: The message to display or use for the operation.
            remote: The target git remote.
            branch: The target git branch.

        Returns:
            The boolean result.
        """
        kwargs: Dict[str, Any] = {}
        if message is not None:
            kwargs["message"] = message
        if remote is not None:
            kwargs["remote"] = remote
        if branch is not None:
            kwargs["branch"] = branch
        return self.start_operation("push", **kwargs)

    def stage_file(self, file_path: str) -> bool:
        """Start staging a single file.

        Args:
            file_path: The file path to process.

        Returns:
            The boolean result.
        """
        return self.start_operation("stage_file", file_path=file_path)

    def stage_markdown(self, file_paths: Optional[list] = None) -> bool:
        """Start staging markdown files.

        Args:
            file_paths: The file paths to process.

        Returns:
            The boolean result.
        """
        return self.start_operation("stage_markdown", file_paths=file_paths)

    def unstage_all(self) -> bool:
        """Start unstaging all files.

        Returns:
            The boolean result.
        """
        return self.start_operation("unstage_all")

    def commit(self, message: str, stage_all: bool = False) -> bool:
        """Start a git commit operation.

        Args:
            message: The message to display or use for the operation.
            stage_all: Whether to stage all changes before committing.

        Returns:
            The boolean result.
        """
        return self.start_operation("commit", message=message, stage_all=stage_all)

    def export_staged(self, output_zip_path: Optional[str] = None) -> bool:
        """Start exporting staged files.

        Args:
            output_zip_path: Optional destination path for the zip archive.

        Returns:
            The boolean result.
        """
        kwargs: Dict[str, Any] = {}
        if output_zip_path is not None:
            kwargs["output_zip_path"] = output_zip_path
        return self.start_operation("export_staged", **kwargs)

    def _on_operation_finished(self, operation: str, success: bool, message: str, payload: object) -> None:
        """Fan out completion updates to listeners.

        Args:
            operation: The git operation name.
            success: Whether the operation completed successfully.
            message: The message to display or use for the operation.
            payload: Additional operation result data.
        """
        if operation == "status" and success and isinstance(payload, dict):
            status_payload = payload.get("status")
            if isinstance(status_payload, dict):
                self.status_updated.emit(status_payload)

        self.operation_output.emit(operation, message)
        self.operation_finished.emit(operation, success, message)
        self._worker = None
