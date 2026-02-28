"""
Application toolbar with file operations and git controls.
"""
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QToolBar, QMessageBox, QInputDialog, 
    QProgressDialog, QApplication
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QAction

from core.config import Config
from utils.git import GitHelper, GitWorker
from utils.file import FileHelper


class Toolbar(QToolBar):
    """Application toolbar with file and git operations."""
    
    file_selected = pyqtSignal(str)  # Signal emitted when file is selected
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Toolbar")
        self.current_git_worker: Optional[GitWorker] = None
        self.progress_dialog: Optional[QProgressDialog] = None
        self.file_helper: FileHelper = FileHelper(str(Config.get_base_path()))
        self.git_helper: Optional[GitHelper] = None
        self._init_git_helper()
        self._setup_actions()
    
    def _init_git_helper(self):
        """Initialize git helper if repository is available."""
        try:
            print(f"DEBUG: Initializing GitHelper with path: {Config.get_base_path()}")
            self.git_helper = GitHelper(str(Config.get_base_path()))
            print(f"DEBUG: GitHelper initialized successfully: {self.git_helper}")
        except Exception as e:
            # No git repository available
            print(f"DEBUG: Failed to initialize GitHelper: {e}")
            self.git_helper = None
    
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
        
        self.addSeparator()
        
        # Git staging actions
        self.git_stage_all_action = QAction("📋 Stage All", self)
        self.git_stage_all_action.setToolTip("Stage all changes for commit")
        self.git_stage_all_action.triggered.connect(self._git_stage_all)
        self.addAction(self.git_stage_all_action)
        
        self.git_unstage_all_action = QAction("🔄 Unstage All", self)
        self.git_unstage_all_action.setToolTip("Unstage all staged changes")
        self.git_unstage_all_action.triggered.connect(self._git_unstage_all)
        self.addAction(self.git_unstage_all_action)
        
        self.git_status_action = QAction("📊 Status", self)
        self.git_status_action.setToolTip("View repository status")
        self.git_status_action.triggered.connect(self._git_status)
        self.addAction(self.git_status_action)
        
        self.addSeparator()
        
        # Git commit action
        self.git_commit_action = QAction("💾 Commit", self)
        self.git_commit_action.setToolTip("Commit current changes")
        self.git_commit_action.triggered.connect(self._git_commit)
        self.addAction(self.git_commit_action)
        
        # Enable/disable based on git availability
        git_available = self.git_helper is not None
        self.enable_git_actions(git_available)
    
    def _open_file_dialog(self):
        """Open file dialog to select markdown file."""
        file_path = self.file_helper.select_markdown_file(
            parent=self,
            title="Select Markdown File for Analysis"
        )
        
        if file_path:
            self.file_selected.emit(file_path)
    
    def _execute_git_command(self, operation: str, success_message: str, **kwargs):
        """Execute git command in background thread."""
        print(f"DEBUG: _execute_git_command called with operation: {operation}")
        print(f"DEBUG: git_helper: {self.git_helper}")
        print(f"DEBUG: git_helper.is_repo_available(): {self.git_helper.is_repo_available() if self.git_helper else 'N/A'}")
        
        if not self.git_helper or not self.git_helper.is_repo_available():
            print("DEBUG: Git helper not available, showing warning")
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found. Make sure you're in a git repository."
            )
            return
        
        print("DEBUG: Creating progress dialog and worker thread")
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            f"Executing git {operation}...",
            "Cancel",
            0, 0,
            self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.show()
        
        # Create and start worker thread
        repo_path = self.git_helper.get_repo_root()
        print(f"DEBUG: Creating GitWorker with repo_path: {repo_path}")
        self.current_git_worker = GitWorker(
            operation=operation,
            repo_path=repo_path,
            **kwargs
        )
        self.current_git_worker.finished.connect(
            lambda success, message: self._on_git_operation_finished(
                success, message, success_message
            )
        )
        self.progress_dialog.canceled.connect(self._cancel_git_operation)
        print("DEBUG: Starting GitWorker thread")
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
        self._execute_git_command("fetch", "Successfully fetched latest changes from remote.")
    
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
            self._execute_git_command("pull", "Successfully pulled changes from remote.")
    
    def _git_stage_all(self):
        """Stage all changes."""
        self._execute_git_command("stage_all", "Successfully staged all changes.")
    
    def _git_unstage_all(self):
        """Unstage all changes."""
        reply = QMessageBox.question(
            self,
            "Confirm Unstage",
            "This will unstage all staged changes. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._execute_git_command("unstage_all", "Successfully unstaged all changes.")
    
    def _git_commit(self):
        """Execute git commit command."""
        if not self.git_helper or not self.git_helper.is_repo_available():
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found."
            )
            return
        
        try:
            # Check for changes
            unstaged_changes, staged_changes = self.git_helper.has_changes()
            
            if staged_changes:
                # There are staged changes, get commit message and commit
                commit_message, ok = QInputDialog.getText(
                    self,
                    "Commit Changes",
                    "Enter commit message:",
                    text="Update analysis"
                )
                
                if ok and commit_message.strip():
                    self._execute_git_command(
                        "commit",
                        "Successfully committed changes.",
                        message=commit_message.strip()
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Commit Cancelled",
                        "Commit cancelled - no message provided."
                    )
            
            elif unstaged_changes:
                # There are unstaged changes, ask to stage and commit
                reply = QMessageBox.question(
                    self,
                    "Stage Changes",
                    "No staged changes found, but there are unstaged changes. Stage all changes and commit?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Get commit message and stage + commit
                    commit_message, ok = QInputDialog.getText(
                        self,
                        "Commit Changes", 
                        "Enter commit message:",
                        text="Update analysis"
                    )
                    
                    if ok and commit_message.strip():
                        self._execute_git_command(
                            "commit",
                            "Successfully staged and committed changes.",
                            message=commit_message.strip(),
                            stage_all=True
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
        if not self.git_helper or not self.git_helper.is_repo_available():
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found."
            )
            return
        
        try:
            success, message = self.git_helper.get_status_detailed()
            
            if success:
                QMessageBox.information(
                    self,
                    "Git Status",
                    message
                )
            else:
                QMessageBox.warning(
                    self,
                    "Git Error",
                    f"Failed to get git status: {message}"
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
        self.git_stage_all_action.setEnabled(enabled)
        self.git_unstage_all_action.setEnabled(enabled)
        self.git_status_action.setEnabled(enabled)
        self.git_commit_action.setEnabled(enabled)
    
    def enable_file_actions(self, enabled: bool = True):
        """Enable or disable file actions."""
        self.open_file_action.setEnabled(enabled)
        self.recent_files_action.setEnabled(enabled)
    
    def _show_recent_files(self):
        """Show recent files menu (placeholder)."""
        # TODO: Implement recent files functionality
        recent_files = self.file_helper.get_recent_files()
        
        if recent_files:
            # For now, just show a simple message with the files
            file_list = "\n".join(f"• {Path(f).name}" for f in recent_files[:5])
            QMessageBox.information(
                self,
                "Recent Files",
                f"Recent files:\n\n{file_list}\n\n(Selection from list not yet implemented)"
            )
        else:
            QMessageBox.information(
                self,
                "Recent Files", 
                "No recent files found."
            )
