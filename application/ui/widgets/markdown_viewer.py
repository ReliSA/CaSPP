"""
Markdown viewer widget for displaying markdown content.
"""
# standard library imports
import logging
from pathlib import Path
from typing import Optional

# third-party imports
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

# local imports
from utils.markdown_auto_stager import MarkdownAutoStager

logger = logging.getLogger(__name__)


class MarkdownViewer(QWidget):
    """Custom widget for viewing markdown content."""
    
    # Signal emitted when file content changes
    content_changed = pyqtSignal(str)
    # Signal emitted when file is saved
    file_saved = pyqtSignal(str)  # file_path
    # Signal emitted when auto-staging occurs
    file_staged = pyqtSignal(str, str)  # file_path, message

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_file_path = None
        self._original_content = ""
        self._unsaved_changes = False
        
        # Auto-stager for git integration
        self._auto_stager = MarkdownAutoStager()
        self._auto_stager.file_staged.connect(self._on_file_staged)
        self._auto_stager.staging_failed.connect(self._on_staging_failed)
        
        # Auto-save timer
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.setSingleShot(True)
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with label and controls
        header_layout = QHBoxLayout()
        
        # Label
        self.label = QLabel("Markdown Content:")
        header_layout.addWidget(self.label)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setEnabled(False)
        header_layout.addWidget(self.save_button)
        
        # Status label for git operations
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()  # Push everything to the left
        layout.addLayout(header_layout)
        
        # Text edit
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        
        # Connect signals
        self.text_edit.textChanged.connect(self._on_text_changed)
        
        # Keyboard shortcuts
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a markdown file and display its content.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.set_content(content)
                self._current_file_path = file_path
                self._original_content = content
                self._unsaved_changes = False
                self._update_save_button()
                self._update_status("File loaded")
                return True
        except FileNotFoundError:
            self.set_error("Markdown file not found. Please check the file path.")
            return False
        except Exception as e:
            self.set_error(f"Error loading file: {str(e)}")
            return False
    
    def save_file(self) -> bool:
        """
        Save the current content to file.
        
        Returns:
            True if file was saved successfully, False otherwise
        """
        if not self._current_file_path:
            self._update_status("No file to save", error=True)
            return False
        
        if not self._unsaved_changes:
            self._update_status("No changes to save")
            return True
        
        try:
            content = self.get_content()
            
            # Save to file
            with open(self._current_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            # Update state
            self._original_content = content
            self._unsaved_changes = False
            self._update_save_button()
            
            # Emit signal
            self.file_saved.emit(self._current_file_path)
            
            # Auto-stage the file if it's a markdown file
            if self._current_file_path.endswith('.md') and self._auto_stager.is_available():
                try:
                    self._auto_stager.stage_file_delayed(self._current_file_path)
                    self._update_status("Saved and queued for staging")
                except Exception as e:
                    logger.warning(f"Auto-staging failed: {e}")
                    self._update_status("Saved (staging failed)")
            else:
                self._update_status("Saved successfully")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to save file: {str(e)}"
            self._update_status(error_msg, error=True)
            QMessageBox.critical(self, "Save Error", error_msg)
            return False
    
    def _auto_save(self) -> None:
        """Auto-save the file if there are unsaved changes."""
        if self._unsaved_changes and self._current_file_path:
            try:
                if self.save_file():
                    self._update_status("Auto-saved")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
                self._update_status(f"Auto-save failed: {str(e)}", error=True)
    
    def _update_save_button(self) -> None:
        """Update the save button state based on unsaved changes."""
        self.save_button.setEnabled(self._unsaved_changes and bool(self._current_file_path))
        
        if self._current_file_path:
            filename = Path(self._current_file_path).name
            if self._unsaved_changes:
                self.label.setText(f"Markdown Content: {filename} *")
            else:
                self.label.setText(f"Markdown Content: {filename}")
        else:
            self.label.setText("Markdown Content:")
    
    def _update_status(self, message: str, error: bool = False) -> None:
        """Update the status label."""
        if error:
            self.status_label.setStyleSheet("color: red; font-size: 10px;")
        else:
            self.status_label.setStyleSheet("color: green; font-size: 10px;")
        
        self.status_label.setText(message)
        
        # Clear status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def _on_file_staged(self, file_path: str, message: str) -> None:
        """Handle successful file staging."""
        if file_path == self._current_file_path:
            self._update_status(f"Staged: {message}")
            self.file_staged.emit(file_path, message)
    
    def _on_staging_failed(self, file_path: str, error: str) -> None:
        """Handle failed file staging."""
        if file_path == self._current_file_path:
            self._update_status(f"Staging failed: {error}", error=True)

    def set_content(self, content: str) -> None:
        """Set the markdown content to display."""
        # Temporarily disconnect the signal to avoid triggering change events
        self.text_edit.textChanged.disconnect()
        self.text_edit.setPlainText(content)
        self.text_edit.textChanged.connect(self._on_text_changed)

    def set_error(self, error_message: str) -> None:
        """Display an error message."""
        self.text_edit.setPlainText(error_message)
        self._update_status(error_message, error=True)
    
    def get_content(self) -> str:
        """Get the current content."""
        return self.text_edit.toPlainText()

    def set_read_only(self, read_only: bool) -> None:
        """Set whether the text edit is read-only."""
        self.text_edit.setReadOnly(read_only)
        # Disable save functionality when read-only
        if read_only:
            self.save_button.setEnabled(False)
            self.save_shortcut.setEnabled(False)
        else:
            self._update_save_button()
            self.save_shortcut.setEnabled(True)
    
    def get_current_file_path(self) -> Optional[str]:
        """Get the path of the currently loaded file."""
        return self._current_file_path
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self._unsaved_changes
    
    def enable_auto_staging(self, enabled: bool = True) -> None:
        """Enable or disable auto-staging of markdown files."""
        self._auto_stager.enable_auto_staging(enabled)
    
    def get_auto_stager(self) -> MarkdownAutoStager:
        """Get the auto-stager instance."""
        return self._auto_stager

    def closeEvent(self, event) -> None:
        """Handle widget close event."""
        # Clean up auto-stager
        if hasattr(self, '_auto_stager'):
            self._auto_stager.cleanup()
        
        # Stop auto-save timer
        if hasattr(self, '_auto_save_timer'):
            self._auto_save_timer.stop()
        
        super().closeEvent(event)

    def _on_text_changed(self) -> None:
        """Handle text change events."""
        current_content = self.get_content()
        self._unsaved_changes = (current_content != self._original_content)
        self._update_save_button()
        
        if self._current_file_path:
            self.content_changed.emit(current_content)
            
            # Start auto-save timer (5 seconds delay)
            if hasattr(self, '_auto_save_timer'):
                self._auto_save_timer.start(5000)
