"""
Application toolbar with file operations and git controls.
"""
import os
import subprocess
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QToolBar, QFileDialog, QMessageBox, QInputDialog, 
    QProgressDialog, QApplication
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QAction

from core.config import Config


class GitWorker(QThread):
    """Worker thread for git operations to avoid blocking UI."""
    
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, command: str, working_dir: str):
        super().__init__()
        self.command = command
        self.working_dir = working_dir
    
    def run(self):
        """Execute git command in separate thread."""
        try:
            result = subprocess.run(
                self.command.split(),
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.finished.emit(True, result.stdout.strip())
            else:
                self.finished.emit(False, result.stderr.strip())
                
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Git operation timed out")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class Toolbar(QToolBar):
    """Application toolbar with file and git operations."""
    
    file_selected = pyqtSignal(str)  # Signal emitted when file is selected
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Toolbar")
        self.current_git_worker: Optional[GitWorker] = None
        self.progress_dialog: Optional[QProgressDialog] = None
        self._setup_actions()
    
    def _setup_actions(self):
        """Set up toolbar actions."""
        # File operations section
        self._add_file_actions()
        self.addSeparator()
        
        # Git operations section
        self._add_git_actions()
    
    def _add_file_actions(self):
        """Add file-related actions to toolbar."""
        # Open markdown file action
        self.open_file_action = QAction("📁 Open File", self)
        self.open_file_action.setToolTip("Select a markdown file for analysis")
        self.open_file_action.triggered.connect(self._open_file_dialog)
        self.addAction(self.open_file_action)
    
    def _add_git_actions(self):
        """Add git-related actions to toolbar."""
        # Git fetch action
        self.git_fetch_action = QAction("🔄 Fetch", self)
        self.git_fetch_action.setToolTip("Fetch latest changes from remote repository")
        self.git_fetch_action.triggered.connect(self._git_fetch)
        self.addAction(self.git_fetch_action)
        
        # Git pull action
        self.git_pull_action = QAction("⬇️ Pull", self)
        self.git_pull_action.setToolTip("Pull latest changes from remote repository")
        self.git_pull_action.triggered.connect(self._git_pull)
        self.addAction(self.git_pull_action)
        
        # Git commit action
        self.git_commit_action = QAction("💾 Commit", self)
        self.git_commit_action.setToolTip("Commit current changes")
        self.git_commit_action.triggered.connect(self._git_commit)
        self.addAction(self.git_commit_action)
    
    def _open_file_dialog(self):
        """Open file dialog to select markdown file."""
        try:
            # Get the base path for the dialog
            base_path = str(Config.get_base_path())
            
            # Open file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Markdown File for Analysis",
                base_path,
                "Markdown Files (*.md);;All Files (*)"
            )
            
            if file_path:
                # Check if file exists and is readable
                if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                    self.file_selected.emit(file_path)
                else:
                    QMessageBox.warning(
                        self,
                        "File Error",
                        f"Cannot read file: {file_path}"
                    )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file dialog: {str(e)}"
            )
    
    def _get_git_root(self) -> Optional[str]:
        """Find the git repository root directory."""
        try:
            base_path = Config.get_base_path()
            current_path = Path(base_path)
            
            # Walk up the directory tree to find .git folder
            while current_path.parent != current_path:
                git_dir = current_path / ".git"
                if git_dir.exists():
                    return str(current_path)
                current_path = current_path.parent
            
            return None
        
        except Exception:
            return None
    
    def _execute_git_command(self, command: str, success_message: str):
        """Execute git command in background thread."""
        git_root = self._get_git_root()
        if not git_root:
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found. Make sure you're in a git repository."
            )
            return
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            f"Executing: {command}...",
            "Cancel",
            0, 0,
            self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.show()
        
        # Create and start worker thread
        self.current_git_worker = GitWorker(command, git_root)
        self.current_git_worker.finished.connect(
            lambda success, message: self._on_git_operation_finished(
                success, message, success_message
            )
        )
        self.progress_dialog.canceled.connect(self._cancel_git_operation)
        self.current_git_worker.start()
    
    def _on_git_operation_finished(self, success: bool, message: str, success_message: str):
        """Handle completion of git operation."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if success:
            QMessageBox.information(
                self,
                "Git Success",
                f"{success_message}\n\n{message}" if message else success_message
            )
        else:
            QMessageBox.warning(
                self,
                "Git Error",
                f"Git operation failed:\n{message}"
            )
        
        self.current_git_worker = None
    
    def _cancel_git_operation(self):
        """Cancel current git operation."""
        if self.current_git_worker and self.current_git_worker.isRunning():
            self.current_git_worker.terminate()
            self.current_git_worker.wait()
            self.current_git_worker = None
    
    def _git_fetch(self):
        """Execute git fetch command."""
        self._execute_git_command("git fetch", "Successfully fetched latest changes from remote.")
    
    def _git_pull(self):
        """Execute git pull command."""
        reply = QMessageBox.question(
            self,
            "Confirm Pull",
            "This will pull and potentially merge changes from the remote repository. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._execute_git_command("git pull", "Successfully pulled changes from remote.")
    
    def _git_commit(self):
        """Execute git commit command."""
        # First check if there are changes to commit
        git_root = self._get_git_root()
        if not git_root:
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found."
            )
            return
        
        try:
            # Check for staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=git_root,
                capture_output=True
            )
            
            if result.returncode != 0:  # There are staged changes
                # Get commit message from user
                commit_message, ok = QInputDialog.getText(
                    self,
                    "Commit Changes",
                    "Enter commit message:",
                    text="Update analysis"
                )
                
                if ok and commit_message.strip():
                    self._execute_git_command(
                        f'git commit -m "{commit_message.strip()}"',
                        "Successfully committed changes."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Commit Cancelled",
                        "Commit cancelled - no message provided."
                    )
            else:
                # Check if there are unstaged changes to add
                result = subprocess.run(
                    ["git", "diff", "--quiet"],
                    cwd=git_root,
                    capture_output=True
                )
                
                if result.returncode != 0:  # There are unstaged changes
                    reply = QMessageBox.question(
                        self,
                        "Stage Changes",
                        "No staged changes found, but there are unstaged changes. Stage all changes and commit?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Stage all changes first
                        stage_result = subprocess.run(
                            ["git", "add", "."],
                            cwd=git_root,
                            capture_output=True
                        )
                        
                        if stage_result.returncode == 0:
                            # Now get commit message and commit
                            commit_message, ok = QInputDialog.getText(
                                self,
                                "Commit Changes",
                                "Enter commit message:",
                                text="Update analysis"
                            )
                            
                            if ok and commit_message.strip():
                                self._execute_git_command(
                                    f'git commit -m "{commit_message.strip()}"',
                                    "Successfully staged and committed changes."
                                )
                        else:
                            QMessageBox.warning(
                                self,
                                "Git Error",
                                "Failed to stage changes."
                            )
                else:
                    QMessageBox.information(
                        self,
                        "No Changes",
                        "No changes to commit."
                    )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to check git status: {str(e)}"
            )
    
    def _git_status(self):
        """Show git repository status."""
        git_root = self._get_git_root()
        if not git_root:
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found."
            )
            return
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status_output = result.stdout.strip()
                
                # Get branch info
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
                
                if status_output:
                    # Format the status output
                    lines = status_output.split('\n')
                    formatted_status = []
                    
                    for line in lines:
                        if len(line) >= 3:
                            status_code = line[:2]
                            filename = line[3:]
                            
                            if status_code == "??":
                                formatted_status.append(f"  Untracked: {filename}")
                            elif status_code[0] == "M":
                                formatted_status.append(f"  Modified: {filename}")
                            elif status_code[0] == "A":
                                formatted_status.append(f"  Added: {filename}")
                            elif status_code[0] == "D":
                                formatted_status.append(f"  Deleted: {filename}")
                            else:
                                formatted_status.append(f"  {status_code}: {filename}")
                    
                    message = f"Branch: {current_branch}\n\nChanges:\n" + "\n".join(formatted_status)
                else:
                    message = f"Branch: {current_branch}\n\nWorking directory clean - no changes to commit."
                
                QMessageBox.information(
                    self,
                    "Git Status",
                    message
                )
            else:
                QMessageBox.warning(
                    self,
                    "Git Error",
                    f"Failed to get git status: {result.stderr.strip()}"
                )
        
        except subprocess.TimeoutExpired:
            QMessageBox.warning(
                self,
                "Git Error",
                "Git status command timed out."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get git status: {str(e)}"
            )
    
    def enable_git_actions(self, enabled: bool = True):
        """Enable or disable git actions."""
        self.git_fetch_action.setEnabled(enabled)
        self.git_pull_action.setEnabled(enabled)
        self.git_commit_action.setEnabled(enabled)
        self.git_status_action.setEnabled(enabled)
    
    def enable_file_actions(self, enabled: bool = True):
        """Enable or disable file actions."""
        self.open_file_action.setEnabled(enabled)
        self.recent_files_action.setEnabled(enabled)
