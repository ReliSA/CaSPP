"""
File operations helper module.
"""
import os
from pathlib import Path
from typing import Optional, List, Tuple

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget


class FileHelper:
    """Helper class for file operations."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize file helper.
        
        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def select_markdown_file(self, parent: Optional[QWidget] = None, 
                           title: str = "Select Markdown File") -> Optional[str]:
        """
        Open file dialog to select a markdown file.
        
        Args:
            parent: Parent widget for the dialog
            title: Dialog title
        
        Returns:
            Selected file path or None if cancelled
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                title,
                str(self.base_path),
                "Markdown Files (*.md);;All Files (*)"
            )
            
            if file_path:
                return self._validate_file(file_path)
            
            return None
        
        except Exception as e:
            self._show_error(parent, "File Selection Error", 
                           f"Failed to open file dialog: {str(e)}")
            return None
    
    def select_multiple_markdown_files(self, parent: Optional[QWidget] = None,
                                     title: str = "Select Markdown Files") -> List[str]:
        """
        Open file dialog to select multiple markdown files.
        
        Args:
            parent: Parent widget for the dialog
            title: Dialog title
        
        Returns:
            List of selected file paths
        """
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                parent,
                title,
                str(self.base_path),
                "Markdown Files (*.md);;All Files (*)"
            )
            
            validated_paths = []
            for file_path in file_paths:
                validated_path = self._validate_file(file_path)
                if validated_path:
                    validated_paths.append(validated_path)
            
            return validated_paths
        
        except Exception as e:
            self._show_error(parent, "File Selection Error",
                           f"Failed to open file dialog: {str(e)}")
            return []
    
    def select_directory(self, parent: Optional[QWidget] = None,
                        title: str = "Select Directory") -> Optional[str]:
        """
        Open directory dialog to select a directory.
        
        Args:
            parent: Parent widget for the dialog
            title: Dialog title
        
        Returns:
            Selected directory path or None if cancelled
        """
        try:
            dir_path = QFileDialog.getExistingDirectory(
                parent,
                title,
                str(self.base_path)
            )
            
            if dir_path:
                return dir_path
            
            return None
        
        except Exception as e:
            self._show_error(parent, "Directory Selection Error",
                           f"Failed to open directory dialog: {str(e)}")
            return None
    
    def _validate_file(self, file_path: str) -> Optional[str]:
        """
        Validate that a file exists and is readable.
        
        Args:
            file_path: Path to validate
        
        Returns:
            Validated file path or None if invalid
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
            
            if not path.is_file():
                return None
            
            if not os.access(file_path, os.R_OK):
                return None
            
            return str(path.resolve())
        
        except Exception:
            return None
    
    def _show_error(self, parent: Optional[QWidget], title: str, message: str):
        """Show error message dialog."""
        QMessageBox.critical(parent, title, message)
    
    def _show_warning(self, parent: Optional[QWidget], title: str, message: str):
        """Show warning message dialog.""" 
        QMessageBox.warning(parent, title, message)
    
    def _show_info(self, parent: Optional[QWidget], title: str, message: str):
        """Show information message dialog."""
        QMessageBox.information(parent, title, message)
    
    def find_markdown_files(self, directory: Optional[str] = None, 
                          recursive: bool = True) -> List[str]:
        """
        Find all markdown files in a directory.
        
        Args:
            directory: Directory to search in. If None, uses base_path.
            recursive: Whether to search recursively
        
        Returns:
            List of markdown file paths
        """
        search_dir = Path(directory) if directory else self.base_path
        
        if not search_dir.exists() or not search_dir.is_dir():
            return []
        
        try:
            if recursive:
                pattern = "**/*.md"
            else:
                pattern = "*.md"
            
            md_files = list(search_dir.glob(pattern))
            return [str(f.resolve()) for f in md_files if f.is_file()]
        
        except Exception:
            return []
    
    def get_recent_files(self, max_count: int = 10) -> List[str]:
        """
        Get list of recently accessed files.
        This is a placeholder - in a real app, you'd store this in settings.
        
        Args:
            max_count: Maximum number of recent files to return
        
        Returns:
            List of recent file paths
        """
        # TODO: Implement actual recent files tracking using QSettings
        # For now, return some common files from the project
        recent_files = []
        
        # Look for common markdown files
        common_names = ["README.md", "index.md", "main.md", "introduction.md"]
        
        for name in common_names:
            file_path = self.base_path / name
            if file_path.exists():
                recent_files.append(str(file_path))
            
            if len(recent_files) >= max_count:
                break
        
        return recent_files
    
    def save_file(self, content: str, file_path: Optional[str] = None, 
                  parent: Optional[QWidget] = None) -> Optional[str]:
        """
        Save content to a file.
        
        Args:
            content: Content to save
            file_path: File path to save to. If None, opens save dialog.
            parent: Parent widget for dialog
        
        Returns:
            Path where file was saved, or None if cancelled/failed
        """
        try:
            if file_path is None:
                file_path, _ = QFileDialog.getSaveFileName(
                    parent,
                    "Save Markdown File",
                    str(self.base_path),
                    "Markdown Files (*.md);;All Files (*)"
                )
                
                if not file_path:
                    return None
            
            # Ensure the directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return file_path
        
        except Exception as e:
            self._show_error(parent, "Save Error", 
                           f"Failed to save file: {str(e)}")
            return None
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to file to read
        
        Returns:
            File content or None if failed
        """
        try:
            validated_path = self._validate_file(file_path)
            if not validated_path:
                return None
            
            with open(validated_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        except Exception:
            return None
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                'name': path.name,
                'path': str(path.resolve()),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'extension': path.suffix
            }
        
        except Exception:
            return None
