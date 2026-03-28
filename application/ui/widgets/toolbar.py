"""
Application toolbar with file operations and git controls.
"""

# standard library imports
from pathlib import Path
from typing import Optional

# third-party imports
from PyQt6.QtWidgets import (
    QToolBar, QMessageBox, QInputDialog, 
    QProgressDialog, QApplication
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QAction

# local imports
from core.config import Config
from utils.git import GitHelper, GitWorker
from application.utils.file_helper import FileHelper


class Toolbar(QToolBar):
    """Application toolbar with file and git operations."""
    
    file_selected = pyqtSignal(str)  # Signal emitted when file is selected

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Main Toolbar")
        self.current_git_worker: Optional[GitWorker] = None
        self.progress_dialog: Optional[QProgressDialog] = None
        # Flag indicating whether a successful commit should be followed by a push
        self._push_after_commit: bool = False
        # Track last git operation name so callbacks can react (e.g. commit -> push)
        self._last_operation: Optional[str] = None
        self.file_helper: FileHelper = FileHelper(str(Config.get_base_path()))
        self.git_helper: Optional[GitHelper] = None
        self._init_git_helper()
        self._setup_actions()

    def _init_git_helper(self) -> None:
        """Initialize git helper if repository is available."""
        try:
            print(f"DEBUG: Initializing GitHelper with path: {Config.get_base_path()}")
            self.git_helper = GitHelper(str(Config.get_base_path()))
            print(f"DEBUG: GitHelper initialized successfully: {self.git_helper}")
        except Exception as e:
            # No git repository available
            print(f"DEBUG: Failed to initialize GitHelper: {e}")
            self.git_helper = None

    def _setup_actions(self) -> None:
        """Set up toolbar actions."""
        # File operations section
        self._add_file_actions()
        self.addSeparator()
        
        # Git operations section
        self._add_git_actions()

    def _add_file_actions(self) -> None:
        """Add file-related actions to toolbar."""
        # Open markdown file action
        self.open_file_action = QAction("📁 Open File", self)
        self.open_file_action.setToolTip("Select a markdown file for analysis")
        self.open_file_action.triggered.connect(self._open_file_dialog)
        self.addAction(self.open_file_action)


    def _add_git_actions(self) -> None:
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
        # NOTE: Stage All is scoped to markdown files only in this UI
        self.git_stage_all_action.setToolTip("Stage markdown files only")
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
        
        # Git commit action (markdown-focused)
        self.git_commit_action = QAction("📝 Commit and Push", self)
        self.git_commit_action.setToolTip("Commit markdown files")
        self.git_commit_action.triggered.connect(self._git_commit)
        self.addAction(self.git_commit_action)
        
        # Enable/disable based on git availability
        git_available = self.git_helper is not None
        self.enable_git_actions(git_available)

    def _open_file_dialog(self) -> None:
        """Open file dialog to select markdown file."""
        file_path = self.file_helper.select_markdown_file(
            parent=self,
            title="Select Markdown File for Analysis"
        )
        
        if file_path:
            self.file_selected.emit(file_path)

    def _execute_git_command(self, operation: str, success_message: str, **kwargs) -> None:
        """Execute git command in background thread."""
        print(f"DEBUG: _execute_git_command called with operation: {operation}")
        # remember what operation we're starting
        self._last_operation = operation
        
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
        self.progress_dialog.setAutoClose(False)  # Don't auto-close
        self.progress_dialog.show()
        QApplication.processEvents()  # Process events to show dialog
        
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

    def _on_git_operation_finished(self, success: bool, message: str, success_message: str) -> None:
        """Handle completion of git operation."""
        print(f"DEBUG: _on_git_operation_finished called - success: {success}")
        
        last_op = getattr(self, "_last_operation", None)
        
        # If the completed operation was a commit and the UI requested a push after commit,
        # start the push operation instead of showing an intermediate success dialog.
        if success and last_op == "commit" and getattr(self, "_push_after_commit", False):
            print("DEBUG: Commit succeeded and push requested; starting push (reuse dialog)")
            # reset push flag and set next operation
            self._push_after_commit = False
            self._last_operation = "push"

            # Clean up the commit worker reference (it has finished)
            if self.current_git_worker:
                try:
                    self.current_git_worker.deleteLater()
                except Exception:
                    pass
                finally:
                    self.current_git_worker = None

            # Reuse existing progress dialog to avoid creating an orphan dialog
            if self.progress_dialog is not None:
                try:
                    self.progress_dialog.setLabelText("Pushing changes...")
                except Exception:
                    # If updating label fails, close and recreate below
                    try:
                        self.progress_dialog.close()
                        self.progress_dialog.deleteLater()
                    except Exception:
                        pass
                    self.progress_dialog = None

            if self.progress_dialog is None:
                self.progress_dialog = QProgressDialog(
                    "Pushing changes...",
                    "Cancel",
                    0, 0,
                    self
                )
                self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
                self.progress_dialog.setAutoClose(False)
                self.progress_dialog.show()
                self.progress_dialog.canceled.connect(self._cancel_git_operation)

            # Create and start push worker directly (avoid _execute_git_command which would create another dialog)
            try:
                repo_path = self.git_helper.get_repo_root()
                print(f"DEBUG: Creating GitWorker (push) with repo_path: {repo_path}")
                self.current_git_worker = GitWorker(
                    operation="push",
                    repo_path=repo_path
                )
                self.current_git_worker.finished.connect(
                    lambda success, message: self._on_git_operation_finished(
                        success, message, "Successfully pushed changes to remote."
                    )
                )
                print("DEBUG: Starting GitWorker (push) thread")
                self.current_git_worker.start()
            except Exception as e:
                print(f"DEBUG: Failed to start push worker: {e}")
                # Show error immediately
                def show_error():
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.setWindowTitle("Git Error")
                    msg_box.setText(f"Failed to start push: {e}")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.show()
                QTimer.singleShot(100, show_error)

            # Return early; push worker will call this method again when finished
            return

        # Clean up the worker thread first
        if self.current_git_worker:
            print("DEBUG: Cleaning up worker thread")
            self.current_git_worker.deleteLater()
            self.current_git_worker = None
        
        # Close progress dialog with proper null checks
        if self.progress_dialog is not None:
            print("DEBUG: Closing progress dialog")
            # Capture the dialog reference locally to avoid re-entrancy issues where
            # closing the dialog triggers its 'canceled' handler which can set
            # self.progress_dialog to None before deleteLater() runs.
            dlg = self.progress_dialog
            try:
                # Try to disconnect the canceled handler to avoid re-entrancy. If
                # the disconnect fails (e.g. not connected) ignore the error.
                try:
                    dlg.canceled.disconnect(self._cancel_git_operation)
                except Exception:
                    pass

                dlg.close()
                dlg.deleteLater()
            except Exception as e:
                print(f"DEBUG: Error closing progress dialog: {e}")
            finally:
                # Ensure attribute is cleared
                self.progress_dialog = None
        
        # Use QTimer to show message after cleanup to avoid blocking
        def show_message():
            try:
                if success:
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.setWindowTitle("Git Success")
                    msg_box.setText(f"{success_message}\n\n{message}" if message else success_message)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.show()
                    print("DEBUG: Success message box created")
                else:
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.setWindowTitle("Git Error")
                    msg_box.setText(f"Git operation failed:\n{message}")
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.show()
                    print("DEBUG: Error message box created")
            except Exception as e:
                print(f"DEBUG: Error showing message box: {e}")
        
        # Show message after a short delay to ensure cleanup is complete
        QTimer.singleShot(100, show_message)
        
        # Clear last_operation after handling (if not already cleared)
        self._last_operation = None

    def _cancel_git_operation(self) -> None:
        """Cancel current git operation."""
        if self.current_git_worker and self.current_git_worker.isRunning():
            self.current_git_worker.terminate()
            self.current_git_worker.wait(1000)  # Wait up to 1 second
            self.current_git_worker.deleteLater()
            self.current_git_worker = None
        
        if self.progress_dialog is not None:
            try:
                self.progress_dialog.close()
                self.progress_dialog.deleteLater()
            except Exception as e:
                print(f"DEBUG: Error closing progress dialog in cancel: {e}")
            finally:
                self.progress_dialog = None

    def _git_fetch(self) -> None:
        """Execute git fetch command."""
        self._execute_git_command("fetch", "Successfully fetched latest changes from remote.")

    def _git_pull(self) -> None:
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

    def _git_stage_all(self) -> None:
        """Stage all changes."""
        # Stage only markdown files
        self._execute_git_command("stage_markdown", "Successfully staged markdown files.")

    def _git_unstage_all(self) -> None:
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

    def _git_commit(self) -> None:
        """Commit markdown files with a focused workflow."""
        # This toolbar action performs commit AND push
        self._push_after_commit = True

        if not self.git_helper or not self.git_helper.is_repo_available():
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found."
            )
            return
        
        try:
            # Get repository status
            status = self.git_helper.get_status()
            
            # Find all markdown files with changes
            all_md_files = []
            staged_md_files = []
            unstaged_md_files = []
            
            # Collect markdown files from all categories
            for file_list in [status['modified'], status['added'], status['deleted'], status['untracked']]:
                md_files = [f for f in file_list if f.endswith('.md')]
                all_md_files.extend(md_files)
            
            # Check which markdown files are staged
            staged_status = self.git_helper.get_status()
            for file in staged_status['added'] + staged_status['modified']:
                if file.endswith('.md'):
                    staged_md_files.append(file)
            
            # Check for unstaged markdown files
            for file in status['modified'] + status['untracked']:
                if file.endswith('.md') and file not in staged_md_files:
                    unstaged_md_files.append(file)
            
            if staged_md_files:
                # There are staged markdown files - proceed with commit
                file_list = '\n'.join(f"• {f}" for f in staged_md_files)
                commit_message, ok = QInputDialog.getText(
                    self,
                    "Commit Files",
                    f"Staged markdown files:\n{file_list}\n\nEnter commit message:",
                    text=f"Update {len(staged_md_files)} markdown file{'s' if len(staged_md_files) > 1 else ''}"
                )
                
                if ok and commit_message.strip():
                    self._execute_git_command(
                        "commit",
                        f"Successfully committed {len(staged_md_files)} markdown file(s).",
                        message=commit_message.strip()
                    )
                else:
                    # User cancelled the commit -- do not push
                    self._push_after_commit = False
                    QMessageBox.information(
                        self,
                        "Commit Cancelled",
                        "Commit cancelled - no message provided."
                    )
             
            elif unstaged_md_files:
                # No staged markdown files, but there are unstaged ones
                file_list = '\n'.join(f"• {f}" for f in unstaged_md_files)
                reply = QMessageBox.question(
                    self,
                    "Stage Files",
                    f"No staged markdown files found, but there are unstaged markdown files:\n{file_list}\n\nStage and commit these files?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Stage markdown files and commit
                    commit_message, ok = QInputDialog.getText(
                        self,
                        "Commit Files",
                        f"Enter commit message for {len(unstaged_md_files)} markdown file(s):",
                        text=f"Update {len(unstaged_md_files)} markdown file{'s' if len(unstaged_md_files) > 1 else ''}"
                    )
                    
                    if ok and commit_message.strip():
                        # First stage the markdown files
                        self._stage_markdown_files_and_commit(unstaged_md_files, commit_message.strip())
                    else:
                        # user didn't provide a commit message -> cancel push
                        self._push_after_commit = False
                else:
                    # user chose not to stage & commit
                    self._push_after_commit = False
             
            else:
                # Nothing to commit, so cancel the push request
                self._push_after_commit = False
                QMessageBox.information(
                    self,
                    "No Changes",
                    "No markdown file changes to commit."
                )
        
        except Exception as e:
            # on error, cancel any pending push
            self._push_after_commit = False
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to check git status: {str(e)}"
            )

    def _stage_markdown_files_and_commit(self, md_files: list, commit_message: str) -> None:
        """Stage specific markdown files and then commit."""
        # Create progress dialog for the two-step process
        self.progress_dialog = QProgressDialog(
            "Staging markdown files...",
            "Cancel",
            0, 0,
            self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.show()
        
        # Create worker to stage markdown files
        repo_path = self.git_helper.get_repo_root()
        self.current_git_worker = GitWorker(
            operation="stage_markdown",
            repo_path=repo_path,
            file_paths=md_files
        )
        
        # When staging finishes, commit
        self.current_git_worker.finished.connect(
            lambda success, message: self._on_markdown_staging_finished(
                success, message, commit_message
            )
        )
        self.progress_dialog.canceled.connect(self._cancel_git_operation)
        self.current_git_worker.start()

    def _on_markdown_staging_finished(self, success: bool, message: str, commit_message: str) -> None:
        """Handle completion of markdown file staging."""
        print(f"DEBUG: _on_markdown_staging_finished called - success: {success}")
        
        if not success:
            # Clean up on failure
            if self.current_git_worker:
                self.current_git_worker.deleteLater()
                self.current_git_worker = None
            
            if self.progress_dialog is not None:
                # Same safe-close approach as in _on_git_operation_finished to avoid
                # re-entrancy when closing the dialog.
                dlg = self.progress_dialog
                try:
                    try:
                        dlg.canceled.disconnect(self._cancel_git_operation)
                    except Exception:
                        pass

                    dlg.close()
                    dlg.deleteLater()
                except Exception as e:
                    print(f"DEBUG: Error closing progress dialog in staging failure: {e}")
                finally:
                    self.progress_dialog = None
            
            # Show error message with delay
            def show_error():
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Staging Error")
                msg_box.setText(f"Failed to stage markdown files:\n{message}")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.show()
            
            QTimer.singleShot(100, show_error)
            return
        
        # Update progress dialog for commit step
        if self.progress_dialog:
            self.progress_dialog.setLabelText("Committing changes...")
        
        # Clean up the staging worker first
        if self.current_git_worker:
            print("DEBUG: Cleaning up staging worker")
            self.current_git_worker.deleteLater()
            self.current_git_worker = None
        
        # Now create a new worker for commit
        repo_path = self.git_helper.get_repo_root()
        print("DEBUG: Creating commit worker")
        # Indicate that the upcoming worker is a commit so callbacks can chain a push
        self._last_operation = "commit"
        self.current_git_worker = GitWorker(
            operation="commit",
            repo_path=repo_path,
            message=commit_message
        )
        
        self.current_git_worker.finished.connect(
            lambda success, message: self._on_git_operation_finished(
                success, message, "Successfully staged and committed markdown files."
            )
        )
        self.current_git_worker.start()

    def _git_status(self) -> None:
        """Show git repository status."""
        if not self.git_helper or not self.git_helper.is_repo_available():
            QMessageBox.warning(
                self,
                "Git Error",
                "No git repository found."
            )
            return
        
        try:
            # Build a markdown-only status message from lower-level status info
            branch = self.git_helper.get_current_branch()
            status = self.git_helper.get_status()

            md_untracked = [f for f in status.get('untracked', []) if f.endswith('.md')]
            md_modified = [f for f in status.get('modified', []) if f.endswith('.md')]
            md_added = [f for f in status.get('added', []) if f.endswith('.md')]
            md_deleted = [f for f in status.get('deleted', []) if f.endswith('.md')]

            message_lines = [f"Branch: {branch}", ""]
            has_any = False

            if md_untracked:
                has_any = True
                message_lines.append("Untracked markdown files:")
                for f in md_untracked:
                    message_lines.append(f"  {f}")
                message_lines.append("")

            if md_modified:
                has_any = True
                message_lines.append("Modified markdown files:")
                for f in md_modified:
                    message_lines.append(f"  {f}")
                message_lines.append("")

            if md_added:
                has_any = True
                message_lines.append("Staged markdown files:")
                for f in md_added:
                    message_lines.append(f"  {f}")
                message_lines.append("")

            if md_deleted:
                has_any = True
                message_lines.append("Deleted markdown files:")
                for f in md_deleted:
                    message_lines.append(f"  {f}")
                message_lines.append("")

            if not has_any:
                message_lines.append("No markdown file changes found.")

            QMessageBox.information(
                self,
                "Git Status (Markdown)",
                "\n".join(message_lines)
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get git status: {str(e)}"
            )

    def enable_git_actions(self, enabled: bool = True) -> None:
        """Enable or disable git actions."""
        self.git_fetch_action.setEnabled(enabled)
        self.git_pull_action.setEnabled(enabled)
        self.git_stage_all_action.setEnabled(enabled)
        self.git_unstage_all_action.setEnabled(enabled)
        self.git_status_action.setEnabled(enabled)
        self.git_commit_action.setEnabled(enabled)

    def enable_file_actions(self, enabled: bool = True) -> None:
        """Enable or disable file actions."""
        self.open_file_action.setEnabled(enabled)
        self.recent_files_action.setEnabled(enabled)

    # def _show_recent_files(self) -> None:
    #     """Show recent files menu (placeholder)."""
    #     # TODO: Implement recent files functionality
    #     recent_files = self.file_helper.get_recent_files()
        
    #     if recent_files:
    #         # For now, just show a simple message with the files
    #         file_list = "\n".join(f"• {Path(f).name}" for f in recent_files[:5])
    #         QMessageBox.information(
    #             self,
    #             "Recent Files",
    #             f"Recent files:\n\n{file_list}\n\n(Selection from list not yet implemented)"
    #         )
    #     else:
    #         QMessageBox.information(
    #             self,
    #             "Recent Files", 
    #             "No recent files found."
    #         )
