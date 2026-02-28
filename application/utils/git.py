"""
Git operations helper module.
"""
import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from PyQt6.QtCore import QThread, pyqtSignal

try:
    import git
    from git import Repo, GitCommandError, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class GitWorker(QThread):
    """Worker thread for git operations to avoid blocking UI."""
    
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation: str, repo_path: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.repo_path = repo_path
        self.kwargs = kwargs
    
    def run(self):
        """Execute git operation in separate thread."""
        print(f"DEBUG: GitWorker.run() called with operation: {self.operation}")
        print(f"DEBUG: GitWorker repo_path: {self.repo_path}")
        try:
            print("DEBUG: Creating GitHelper in worker thread")
            helper = GitHelper(self.repo_path)
            print(f"DEBUG: GitHelper created successfully: {helper}")
            
            if self.operation == "fetch":
                print("DEBUG: Calling helper.fetch()")
                success, message = helper.fetch()
                print(f"DEBUG: fetch() returned: success={success}, message={message}")
            elif self.operation == "pull":
                success, message = helper.pull()
            elif self.operation == "commit":
                commit_message = self.kwargs.get('message', 'Update')
                stage_all = self.kwargs.get('stage_all', False)
                success, message = helper.commit(commit_message, stage_all)
            elif self.operation == "status":
                success, message = helper.get_status_detailed()
            elif self.operation == "stage_all":
                success, message = helper.stage_all()
            elif self.operation == "unstage_all":
                success, message = helper.unstage_all()
            else:
                success, message = False, f"Unknown operation: {self.operation}"
            
            print(f"DEBUG: Emitting finished signal: success={success}")
            self.finished.emit(success, message)
            
        except Exception as e:
            print(f"DEBUG: Exception in GitWorker.run(): {e}")
            self.finished.emit(False, f"Git operation failed: {str(e)}")


class GitHelper:
    """Helper class for git operations using GitPython library."""
    
    def __init__(self, repo_path: Optional[str] = None, remote_name: str = "origin"):
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
    
    def _find_and_validate_repo(self):
        """Find and validate the git repository."""
        if not GIT_AVAILABLE:
            raise ImportError("GitPython library not available. Install with: pip install GitPython")
        
        try:
            if self.repo_path:
                self.repo = Repo(self.repo_path)
            else:
                # Search for repo starting from current directory
                current_path = Path.cwd()
                self.repo = Repo(current_path, search_parent_directories=True)
                self.repo_path = str(self.repo.working_dir)
        
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(f"No git repository found at {self.repo_path or 'current directory'}")
    
    def is_repo_available(self) -> bool:
        """Check if git repository is available and valid."""
        return self.repo is not None and not self.repo.bare
    
    def get_repo_root(self) -> str:
        """Get the root path of the git repository."""
        if not self.is_repo_available():
            raise InvalidGitRepositoryError("No valid git repository available")
        return str(self.repo.working_dir)
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        if not self.is_repo_available():
            return "unknown"
        
        try:
            return str(self.repo.active_branch)
        except Exception:
            return "unknown"
    
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
            staged = len(self.repo.index.diff("HEAD")) > 0
            return unstaged, staged
        except Exception:
            return False, False
    
    def get_status(self) -> Dict[str, List[str]]:
        """
        Get repository status.
        
        Returns:
            Dictionary with 'modified', 'added', 'deleted', 'untracked' file lists
        """
        if not self.is_repo_available():
            return {'modified': [], 'added': [], 'deleted': [], 'untracked': []}
        
        try:
            status = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': self.repo.untracked_files
            }
            
            # Check unstaged changes
            for diff in self.repo.index.diff(None):
                if diff.change_type == 'M':
                    status['modified'].append(diff.a_path)
                elif diff.change_type == 'D':
                    status['deleted'].append(diff.a_path)
            
            # Check staged changes
            for diff in self.repo.index.diff("HEAD"):
                if diff.change_type == 'A':
                    status['added'].append(diff.a_path)
                elif diff.change_type == 'M' and diff.a_path not in status['modified']:
                    status['modified'].append(diff.a_path)
                elif diff.change_type == 'D' and diff.a_path not in status['deleted']:
                    status['deleted'].append(diff.a_path)
            
            return status
        
        except Exception:
            return {'modified': [], 'added': [], 'deleted': [], 'untracked': []}
    
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
        
        except Exception as e:
            return False, f"Error getting status: {str(e)}"
    
    def fetch(self) -> Tuple[bool, str]:
        """
        Fetch changes from remote repository.
        
        Returns:
            Tuple of (success, message)
        """
        print("DEBUG: GitHelper.fetch() called - BREAKPOINT SHOULD BE HIT HERE!")
        try:
            if not self.is_repo_available():
                print("DEBUG: Repository not available in fetch()")
                return False, "No git repository found"
            
            print(f"DEBUG: Fetching from {len(self.repo.remotes)} remote(s)")
            # Fetch from all remotes
            for remote in self.repo.remotes:
                print(f"DEBUG: Fetching from remote: {remote.name}")
                remote.fetch()
            
            print("DEBUG: Fetch completed successfully")
            return True, "Successfully fetched changes from remote(s)"
        
        except GitCommandError as e:
            print(f"DEBUG: GitCommandError in fetch(): {e}")
            return False, f"Git fetch failed: {str(e)}"
        except Exception as e:
            print(f"DEBUG: Exception in fetch(): {e}")
            return False, f"Error during fetch: {str(e)}"
    
    def pull(self) -> Tuple[bool, str]:
        """
        Pull changes from remote repository.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            # Pull from current branch's upstream
            origin = self.repo.remotes.origin
            current_branch = self.repo.active_branch
            
            # Check if there are uncommitted changes
            if self.repo.is_dirty():
                return False, "Cannot pull: You have uncommitted changes. Commit or stash them first."
            
            result = origin.pull(current_branch.name)
            
            if result:
                return True, f"Successfully pulled changes. Updated {len(result)} reference(s)."
            else:
                return True, "Already up to date."
        
        except GitCommandError as e:
            return False, f"Git pull failed: {str(e)}"
        except Exception as e:
            return False, f"Error during pull: {str(e)}"
    
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
            return False, f"Failed to stage changes: {str(e)}"
        except Exception as e:
            return False, f"Error staging changes: {str(e)}"
    
    def unstage_all(self) -> Tuple[bool, str]:
        """
        Unstage all staged changes.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            self.repo.git.reset("HEAD")  # Unstage all files
            return True, "All changes unstaged successfully"
        
        except GitCommandError as e:
            return False, f"Failed to unstage changes: {str(e)}"
        except Exception as e:
            return False, f"Error unstaging changes: {str(e)}"
    
    def commit(self, message: str, stage_all: bool = False) -> Tuple[bool, str]:
        """
        Commit changes to repository.
        
        Args:
            message: Commit message
            stage_all: Whether to stage all changes before committing
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_repo_available():
                return False, "No git repository found"
            
            if not message.strip():
                return False, "Commit message cannot be empty"
            
            # Stage all changes if requested
            if stage_all:
                stage_success, stage_msg = self.stage_all()
                if not stage_success:
                    return False, f"Failed to stage changes: {stage_msg}"
            
            # Check if there are staged changes
            _, has_staged = self.has_changes()
            if not has_staged:
                return False, "No staged changes to commit"
            
            # Commit the changes
            commit = self.repo.index.commit(message)
            return True, f"Successfully committed changes: {commit.hexsha[:8]}"
        
        except GitCommandError as e:
            return False, f"Git commit failed: {str(e)}"
        except Exception as e:
            return False, f"Error during commit: {str(e)}"
    
    def get_remotes(self) -> List[str]:
        """Get list of remote names."""
        if not self.is_repo_available():
            return []
        
        try:
            return [remote.name for remote in self.repo.remotes]
        except Exception:
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
        except Exception:
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
        except Exception:
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
