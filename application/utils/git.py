"""
Git operations helper module.
"""

# standard library imports
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# third-party imports
from PyQt6.QtCore import QThread, pyqtSignal
try:
    import git
    from git import Repo, GitCommandError, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# local imports
from core.constants import GitConstants
from utils.exceptions import (
    GitLibraryNotAvailableError, GitRepositoryNotFoundError, GitOperationError,
    GitRemoteError, GitDirtyWorkingTreeError, InvalidInputError
)

# Set up logging
logger = logging.getLogger(__name__)


class GitWorker(QThread):
    """
    Worker thread for git operations to avoid blocking UI.
    
    This class handles git operations in a separate thread to keep the UI responsive.
    It creates a fresh GitHelper instance for each operation and properly cleans up
    resources when done.
    
    Attributes:
        finished: Signal emitted when operation completes (success: bool, message: str)
        
    Thread Safety:
        - Creates isolated GitHelper instances per operation
        - No shared state between operations
        - Proper resource cleanup via context manager
    """
    
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation: str, repo_path: str, **kwargs) -> None:
        """
        Initialize GitWorker.
        
        Args:
            operation: Git operation to perform ('fetch', 'pull', 'commit', etc.)
            repo_path: Path to git repository
            **kwargs: Additional parameters for the operation
                - message (str): Commit message for 'commit' operation
                - stage_all (bool): Whether to stage all files for 'commit' operation
        """
        super().__init__()
        self.operation = operation
        self.repo_path = repo_path
        self.kwargs = kwargs
    
    def run(self) -> None:
        """Execute git operation in separate thread."""
        logger.debug(f"GitWorker executing operation: {self.operation}")
        
        # Use context manager for proper resource cleanup
        try:
            with GitHelper(self.repo_path) as helper:
                success, message = self._dispatch_operation(helper)
                self.finished.emit(success, message)
                
        except (GitRepositoryNotFoundError, GitLibraryNotAvailableError) as e:
            # These are user-facing errors with friendly messages
            self.finished.emit(False, e.user_message)
        except (GitOperationError, GitRemoteError, GitDirtyWorkingTreeError) as e:
            # Git operation errors with context
            logger.error(f"Git operation '{self.operation}' failed: {e}")
            self.finished.emit(False, e.user_message)
        except Exception as e:
            # Unexpected errors
            logger.exception(f"Unexpected error in GitWorker operation '{self.operation}': {e}")
            self.finished.emit(False, f"Unexpected error during {self.operation}: {str(e)}")
        finally:
            # Ensure we mark the thread as finished
            self.quit()
            logger.debug(f"GitWorker finished operation: {self.operation}")
    
    def _dispatch_operation(self, helper: 'GitHelper') -> Tuple[bool, str]:
        """
        Dispatch the operation to the appropriate GitHelper method.
        
        Args:
            helper: GitHelper instance to use for the operation
            
        Returns:
            Tuple of (success, message)
        """
        if self.operation == "fetch":
            return helper.fetch()
        elif self.operation == "pull":
            return helper.pull()
        elif self.operation == "commit":
            commit_message = self.kwargs.get('message', GitConstants.DEFAULT_COMMIT_MESSAGE)
            stage_all = self.kwargs.get('stage_all', False)
            return helper.commit(commit_message, stage_all)
        elif self.operation == "push":
            # allow caller to provide remote and branch via kwargs
            remote = self.kwargs.get('remote')
            branch = self.kwargs.get('branch')
            return helper.push(remote, branch)
        elif self.operation == "status":
            return helper.get_status_detailed()
        elif self.operation == "stage_all":
            return helper.stage_all()
        elif self.operation == "unstage_all":
            return helper.unstage_all()
        elif self.operation == "stage_file":
            file_path = self.kwargs.get('file_path')
            if not file_path:
                return False, "No file path provided for staging"
            return helper.stage_file(file_path)
        elif self.operation == "stage_markdown":
            file_paths = self.kwargs.get('file_paths')
            return helper.stage_markdown_files(file_paths)
        else:
            return False, f"Unknown operation: {self.operation}"


class GitHelper:
    """Helper class for git operations using GitPython library."""
    
    def __init__(self, repo_path: Optional[str] = None, remote_name: str = GitConstants.DEFAULT_REMOTE_NAME) -> None:
        """
        Initialize git helper.
        
        Args:
            repo_path: Path to git repository. If None, will search for repo.
            remote_name: Name of the remote to use for fetch/pull operations (default: "origin")
        """
        self.repo_path = repo_path
        self.remote_name = remote_name
        self.repo = None
        self._find_and_validate_repo()
    
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with resource cleanup."""
        self._cleanup()

    def _cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'repo') and self.repo:
            try:
                # Close any open git resources
                if hasattr(self.repo, 'close'):
                    self.repo.close()
            except Exception as e:
                logger.warning(f"Error during GitHelper cleanup: {e}")
            finally:
                self.repo = None
    
    def _find_and_validate_repo(self) -> None:
        """Find and validate the git repository."""
        if not GIT_AVAILABLE:
            raise GitLibraryNotAvailableError()
        
        try:
            if self.repo_path:
                if not Path(self.repo_path).exists():
                    raise GitRepositoryNotFoundError(self.repo_path)
                self.repo = Repo(self.repo_path)
            else:
                # Search for repo starting from current directory
                current_path = Path.cwd()
                self.repo = Repo(current_path, search_parent_directories=True)
                self.repo_path = str(self.repo.working_dir)
        
        except InvalidGitRepositoryError as e:
            raise GitRepositoryNotFoundError(self.repo_path) from e
    
    def is_repo_available(self) -> bool:
        """Check if git repository is available and valid."""
        return self.repo is not None and not self.repo.bare
    
    def _ensure_repo_available(self, operation_name: str = "operation") -> None:
        """
        Ensure repository is available or raise appropriate exception.
        
        Args:
            operation_name: Name of operation for error context
            
        Raises:
            GitRepositoryNotFoundError: If repository is not available
        """
        if not self.is_repo_available():
            raise GitRepositoryNotFoundError(f"Cannot perform {operation_name}")
    
    def _safe_repo_operation(self, operation_name: str, default_return=None):
        """
        Decorator-like helper for safe repository operations.
        
        Args:
            operation_name: Name of operation for logging
            default_return: Value to return if repo is not available
        """
        if not self.is_repo_available():
            logger.warning(f"Repository not available for {operation_name}")
            return default_return
    
    def get_repo_root(self) -> str:
        """Get the root path of the git repository."""
        self._ensure_repo_available("get_repo_root")
        return str(self.repo.working_dir)
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        if not self.is_repo_available():
            return "unknown"
        
        try:
            return str(self.repo.active_branch)
        except (git.exc.GitError, TypeError) as e:
            # Handle detached HEAD or other git-specific errors
            logger.warning(f"Could not get current branch: {e}")
            return "detached HEAD"
    
    def has_changes(self) -> Tuple[bool, bool]:
        """
        Check if there are changes in the repository.
        
        Returns:
            Tuple of (has_unstaged_changes, has_staged_changes)
        """
        if not self.is_repo_available():
            return False, False
        
        try:
            unstaged = len(self.repo.index.diff(None)) > 0 or len(self.repo.untracked_files) > 0
            staged = len(self.repo.index.diff(GitConstants.DEFAULT_BRANCH_HEAD)) > 0
            return unstaged, staged
        except (GitCommandError, git.exc.BadName) as e:
            # Handle case where HEAD doesn't exist (new repo) or other git errors
            logger.warning(f"Error checking changes: {e}")
            # For new repos without HEAD, check if there are any files to stage
            try:
                untracked = len(self.repo.untracked_files) > 0
                return untracked, False
            except (GitCommandError, AttributeError, OSError) as e:
                logger.warning(f"Error checking untracked files: {e}")
                return False, False
    
    def get_status(self) -> Dict[str, List[str]]:
        """
        Get repository status.
        
        Returns:
            Dictionary with 'modified', 'added', 'deleted', 'untracked' file lists
        """
        empty_status = {'modified': [], 'added': [], 'deleted': [], 'untracked': []}
        if not self.is_repo_available():
            return empty_status
        
        try:
            status = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': self.repo.untracked_files
            }
            
            # Check unstaged changes
            for diff in self.repo.index.diff(None):
                if diff.change_type == GitConstants.CHANGE_TYPE_MODIFIED:
                    status['modified'].append(diff.a_path)
                elif diff.change_type == GitConstants.CHANGE_TYPE_DELETED:
                    status['deleted'].append(diff.a_path)
            
            # Check staged changes
            for diff in self.repo.index.diff(GitConstants.DEFAULT_BRANCH_HEAD):
                if diff.change_type == GitConstants.CHANGE_TYPE_ADDED:
                    status['added'].append(diff.a_path)
                elif diff.change_type == GitConstants.CHANGE_TYPE_MODIFIED and diff.a_path not in status['modified']:
                    status['modified'].append(diff.a_path)
                elif diff.change_type == GitConstants.CHANGE_TYPE_DELETED and diff.a_path not in status['deleted']:
                    status['deleted'].append(diff.a_path)
            
            return status
        
        except (GitCommandError, git.exc.BadName, AttributeError, OSError) as e:
            logger.warning(f"Error getting repository status: {e}")
            return empty_status
    
    def get_status_detailed(self) -> Tuple[bool, str]:
        """
        Get detailed status information as a formatted string.
        
        Returns:
            Tuple of (success, status_message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            branch = self.get_current_branch()
            status = self.get_status()
            
            message_lines = [f"Branch: {branch}", ""]
            
            has_any_changes = False
            
            if status['untracked']:
                message_lines.append("Untracked files:")
                for file in status['untracked']:
                    message_lines.append(f"  {file}")
                message_lines.append("")
                has_any_changes = True
            
            if status['modified']:
                message_lines.append("Modified files:")
                for file in status['modified']:
                    message_lines.append(f"  {file}")
                message_lines.append("")
                has_any_changes = True
            
            if status['added']:
                message_lines.append("Staged files:")
                for file in status['added']:
                    message_lines.append(f"  {file}")
                message_lines.append("")
                has_any_changes = True
            
            if status['deleted']:
                message_lines.append("Deleted files:")
                for file in status['deleted']:
                    message_lines.append(f"  {file}")
                message_lines.append("")
                has_any_changes = True
            
            if not has_any_changes:
                message_lines.append("Working directory clean - no changes to commit.")
            
            return True, "\n".join(message_lines)
        
        except (GitCommandError, git.exc.BadName, AttributeError, OSError) as e:
            logger.error(f"Error getting detailed status: {e}")
            return False, f"Error getting status: {str(e)}"
    
    def fetch(self) -> Tuple[bool, str]:
        """
        Fetch changes from remote repository.
        
        Returns:
            Tuple of (success, message)
            
        Raises:
            GitRepositoryNotFoundError: If repository is not available
            GitRemoteError: If fetch operation fails
        """
        self._ensure_repo_available("fetch")
        
        try:
            logger.info(f"Fetching from {len(self.repo.remotes)} remote(s)")
            
            if not self.repo.remotes:
                return False, "No remotes configured"
            
            # Fetch from all remotes
            for remote in self.repo.remotes:
                logger.debug(f"Fetching from remote: {remote.name}")
                remote.fetch()
            
            logger.info("Fetch completed successfully")
            return True, "Successfully fetched changes from remote(s)"
        
        except GitCommandError as e:
            logger.error(f"Git fetch failed: {e}")
            raise GitRemoteError("origin", "fetch", e) from e
    
    def pull(self) -> Tuple[bool, str]:
        """
        Pull changes from remote repository.
        
        Returns:
            Tuple of (success, message)
            
        Raises:
            GitRepositoryNotFoundError: If repository is not available
            GitDirtyWorkingTreeError: If there are uncommitted changes
            GitRemoteError: If pull operation fails
        """
        if not self.is_repo_available():
            raise GitRepositoryNotFoundError()
        
        # Check if there are uncommitted changes
        if self.repo.is_dirty():
            raise GitDirtyWorkingTreeError("pull")
        
        try:
            # Check if origin remote exists
            if 'origin' not in [remote.name for remote in self.repo.remotes]:
                return False, "No 'origin' remote found"
            
            origin = self.repo.remotes.origin
            current_branch = self.repo.active_branch
            
            logger.info(f"Pulling from origin/{current_branch.name}")
            result = origin.pull(current_branch.name)
            
            if result:
                return True, f"Successfully pulled changes. Updated {len(result)} reference(s)."
            else:
                return True, "Already up to date."
        
        except GitCommandError as e:
            logger.error(f"Git pull failed: {e}")
            raise GitRemoteError("origin", "pull", e) from e
    
    def stage_all(self) -> Tuple[bool, str]:
        """
        Stage all changes for commit.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            self.repo.git.add(A=True)  # Add all files including untracked
            return True, "All changes staged successfully"
        
        except GitCommandError as e:
            logger.error(f"Git command failed during staging: {e}")
            return False, f"Failed to stage changes: {str(e)}"
        except (AttributeError, OSError) as e:
            logger.error(f"File system error during staging: {e}")
            return False, f"Error staging changes: {str(e)}"
    
    def stage_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Stage a specific file for commit.
        
        Args:
            file_path: Path to the file to stage (relative or absolute)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            # Convert to relative path from repo root if absolute path provided
            repo_root = Path(self.repo.working_dir)
            file_path_obj = Path(file_path)
            
            if file_path_obj.is_absolute():
                try:
                    relative_path = file_path_obj.relative_to(repo_root)
                    file_to_stage = str(relative_path)
                except ValueError:
                    return False, f"File is not within repository: {file_path}"
            else:
                file_to_stage = file_path
                # Check if file exists in repo
                full_path = repo_root / file_to_stage
                if not full_path.exists():
                    return False, f"File not found: {file_path}"
            
            # Stage the file
            self.repo.git.add(file_to_stage)
            logger.info(f"Successfully staged file: {file_to_stage}")
            return True, f"Successfully staged: {file_to_stage}"
        
        except GitCommandError as e:
            logger.error(f"Git command failed during staging of '{file_path}': {e}")
            return False, f"Failed to stage file: {str(e)}"
        except (AttributeError, OSError) as e:
            logger.error(f"File system error during staging of '{file_path}': {e}")
            return False, f"Error staging file: {str(e)}"
    
    def stage_markdown_files(self, file_paths: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Stage markdown files for commit.
        
        Args:
            file_paths: List of specific .md files to stage. If None, stages all modified .md files.
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            staged_files = []
            failed_files = []
            
            if file_paths is None:
                # Get all modified .md files
                status = self.get_status()
                md_files = []
                
                # Collect all .md files that have changes
                for file_list in [status['modified'], status['deleted'], status['untracked']]:
                    md_files.extend([f for f in file_list if f.endswith('.md')])
                
                file_paths = md_files
            
            if not file_paths:
                return True, "No markdown files to stage"
            
            # Stage each markdown file
            for file_path in file_paths:
                if file_path.endswith('.md'):
                    success, msg = self.stage_file(file_path)
                    if success:
                        staged_files.append(file_path)
                    else:
                        failed_files.append(f"{file_path}: {msg}")
                        logger.warning(f"Failed to stage {file_path}: {msg}")
            
            # Prepare result message
            messages = []
            if staged_files:
                messages.append(f"Staged {len(staged_files)} markdown file(s): {', '.join(staged_files)}")
            
            if failed_files:
                messages.append(f"Failed to stage {len(failed_files)} file(s): {', '.join(failed_files)}")
                return len(staged_files) > 0, "; ".join(messages)
            
            return len(staged_files) > 0, messages[0] if messages else "No files staged"
        
        except Exception as e:
            logger.error(f"Unexpected error during markdown staging: {e}")
            return False, f"Error staging markdown files: {str(e)}"
    
    def unstage_all(self) -> Tuple[bool, str]:
        """
        Unstage all staged changes.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            self.repo.git.reset(GitConstants.DEFAULT_BRANCH_HEAD)  # Unstage all files
            return True, "All changes unstaged successfully"
        
        except GitCommandError as e:
            logger.error(f"Git command failed during unstaging: {e}")
            return False, f"Failed to unstage changes: {str(e)}"
        except (AttributeError, OSError) as e:
            logger.error(f"File system error during unstaging: {e}")
            return False, f"Error unstaging changes: {str(e)}"
    
    def push(self, remote_name: Optional[str] = None, branch: Optional[str] = None) -> Tuple[bool, str]:
        """
        Push local commits to the specified remote/branch.

        Args:
            remote_name: Name of the remote to push to. If None, uses self.remote_name.
            branch: Branch name to push. If None, uses the current active branch.

        Returns:
            Tuple of (success, message)

        Raises:
            GitRepositoryNotFoundError: If repository is not available
            GitRemoteError: If push operation fails
        """
        self._ensure_repo_available("push")

        if remote_name is None:
            remote_name = self.remote_name

        # Ensure remotes exist
        try:
            remote_names = [r.name for r in self.repo.remotes]
        except Exception as e:
            logger.error(f"Error reading remotes: {e}")
            return False, "No remotes configured"

        if not remote_names:
            return False, "No remotes configured"

        if remote_name not in remote_names:
            return False, f"Remote '{remote_name}' not found"

        remote = getattr(self.repo.remotes, remote_name)

        # Determine branch to push
        if branch is None:
            try:
                current_branch = self.repo.active_branch
                branch = current_branch.name
            except Exception as e:
                logger.warning(f"Could not determine current branch for push: {e}")
                return False, "Cannot determine current branch (detached HEAD). Specify branch explicitly."

        try:
            logger.info(f"Pushing branch '{branch}' to remote '{remote_name}'")
            result = remote.push(branch)

            # result is a list of PushInfo objects; we treat absence of exception as success
            logger.info(f"Push result: {result}")
            return True, f"Successfully pushed {branch} to {remote_name}"

        except GitCommandError as e:
            logger.error(f"Git push failed: {e}")
            raise GitRemoteError(remote_name, "push", e) from e
        except Exception as e:
            logger.exception(f"Unexpected error during push: {e}")
            raise GitRemoteError(remote_name, "push", e) from e
    
    def commit(self, message: str, stage_all: bool = False) -> Tuple[bool, str]:
        """
        Commit changes to repository.
        
        Args:
            message: Commit message
            stage_all: Whether to stage all changes before committing
        
        Returns:
            Tuple of (success, message)
            
        Raises:
            GitRepositoryNotFoundError: If repository is not available
            InvalidInputError: If commit message is invalid
            GitOperationError: If commit operation fails
        """
        if not self.is_repo_available():
            raise GitRepositoryNotFoundError()
        
        # Validate commit message
        if not message or not message.strip():
            raise InvalidInputError("commit message", message, "cannot be empty")
        
        if len(message.strip()) > GitConstants.MAX_COMMIT_MESSAGE_LENGTH:
            raise InvalidInputError("commit message", message, 
                                  f"too long (max {GitConstants.MAX_COMMIT_MESSAGE_LENGTH} characters)")
        
        try:
            # Stage all changes if requested
            if stage_all:
                logger.info("Staging all changes before commit...")
                stage_success, stage_msg = self.stage_all()
                if not stage_success:
                    logger.error(f"Failed to stage changes: {stage_msg}")
                    raise GitOperationError("stage", Exception(stage_msg))
                logger.info("Successfully staged all changes")
            
            # Check if there are staged changes
            unstaged, has_staged = self.has_changes()
            logger.debug(f"Repository state - Unstaged changes: {unstaged}, Staged changes: {has_staged}")
            
            if not has_staged:
                if unstaged:
                    return False, "No staged changes to commit. Use 'Stage All' first or enable 'Stage All' option."
                else:
                    return False, "No changes to commit - working directory is clean."
            
            # Commit the changes
            logger.info(f"Committing changes with message: {message[:GitConstants.LOG_MESSAGE_TRUNCATE]}...")
            commit = self.repo.index.commit(message.strip())
            logger.info(f"Successfully committed: {commit.hexsha[:GitConstants.COMMIT_HASH_DISPLAY_LENGTH]}")
            return True, f"Successfully committed changes: {commit.hexsha[:GitConstants.COMMIT_HASH_DISPLAY_LENGTH]}"
        
        except GitCommandError as e:
            logger.error(f"Git commit failed: {e}")
            raise GitOperationError("commit", e) from e
    
    def get_remotes(self) -> List[str]:
        """Get list of remote names."""
        if not self.is_repo_available():
            return []
        
        try:
            return [remote.name for remote in self.repo.remotes]
        except (GitCommandError, AttributeError, OSError) as e:
            logger.warning(f"Error getting remotes: {e}")
            return []
    
    def get_remote_info(self) -> Dict[str, str]:
        """
        Get information about configured remotes.
        
        Returns:
            Dictionary mapping remote names to their URLs
        """
        if not self.is_repo_available():
            return {}
        
        try:
            remotes = {}
            for remote in self.repo.remotes:
                # Get the fetch URL (first URL if multiple)
                if remote.urls:
                    remotes[remote.name] = list(remote.urls)[0]
                else:
                    remotes[remote.name] = "No URL configured"
            return remotes
        except (GitCommandError, AttributeError, OSError) as e:
            logger.warning(f"Error getting remote info: {e}")
            return {}
    
    def set_remote_name(self, remote_name: str) -> bool:
        """
        Set the remote name to use for operations.
        
        Args:
            remote_name: Name of the remote to use
        
        Returns:
            True if remote exists, False otherwise
        """
        if not self.is_repo_available():
            return False
        
        try:
            # Check if remote exists
            remote_names = self.get_remotes()
            if remote_name in remote_names:
                self.remote_name = remote_name
                return True
            return False
        except (GitCommandError, AttributeError, OSError) as e:
            logger.warning(f"Error checking remote {remote_name}: {e}")
            return False


def find_git_repo(start_path: Optional[str] = None) -> Optional[str]:
    """
    Find git repository starting from the given path.
    
    Args:
        start_path: Path to start searching from. If None, uses current directory.
    
    Returns:
        Path to git repository root, or None if not found
    """
    if not GIT_AVAILABLE:
        return None
    
    try:
        search_path = Path(start_path) if start_path else Path.cwd()
        repo = Repo(search_path, search_parent_directories=True)
        return str(repo.working_dir)
    except (InvalidGitRepositoryError, Exception):
        return None


def is_git_available() -> bool:
    """Check if GitPython library is available."""
    return GIT_AVAILABLE
