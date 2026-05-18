"""
File operations helper module.
"""

# standard library imports
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict

# third-party imports
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

try:
    from charset_normalizer import from_bytes
except ImportError:
    from_bytes = None

# local imports
from utils.constants import FileConstants
from utils.exceptions import (
    FileNotFoundError, FileReadError, FileWriteError, 
    InvalidFileTypeError, FileSizeError, FileAccessError
)
from core.managers.error_manager import ErrorManager

logger = logging.getLogger(__name__)

class FileHelper:
    """Helper class for file operations."""

    def __init__(self, base_path: Optional[str] = None) -> None:
        """Initialize file helper.

        Args:
            base_path: Base directory for file operations.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._file_encodings: Dict[str, str] = {}

    def _detect_encoding_from_bytes(self, raw_bytes: bytes) -> str:
        """Detect text encoding with strict fallbacks.

        Args:
            raw_bytes: The raw bytes value.

        Returns:
            The string result.
        """
        try:
            raw_bytes.decode(FileConstants.ENCODING_UTF8)
            return FileConstants.ENCODING_UTF8
        except UnicodeDecodeError:
            pass

        if from_bytes is not None:
            matches = from_bytes(raw_bytes)
            best = matches.best()
            if best and best.encoding:
                return best.encoding.lower()

        return FileConstants.ENCODING_CP1252

    def _resolve_save_encoding(self, file_path: Optional[str]) -> str:
        """Resolve output encoding for file writes.

        Args:
            file_path: The file path to process.

        Returns:
            The string result.
        """
        if not file_path:
            return FileConstants.ENCODING_UTF8

        resolved_path = str(Path(file_path).resolve())
        if resolved_path in self._file_encodings:
            return self._file_encodings[resolved_path]

        path_obj = Path(file_path)
        if path_obj.exists() and path_obj.is_file():
            raw_bytes = path_obj.read_bytes()
            encoding = self._detect_encoding_from_bytes(raw_bytes)
            self._file_encodings[resolved_path] = encoding
            return encoding

        return FileConstants.ENCODING_UTF8
    
    def select_markdown_file(self, parent: Optional[QWidget] = None, 
                           title: str = "Select Markdown File") -> Optional[str]:
        """Open file dialog to select a markdown file.

        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.

        Returns:
            Selected file path or None if cancelled.
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                title,
                str(self.base_path),
                FileConstants.MARKDOWN_FILTER
            )
            
            if file_path:
                return self.validate_file(file_path)
            
            return None
        
        except (OSError, RuntimeError) as e:
            ErrorManager.show_error("File Selection Error", f"Failed to open file dialog: {str(e)}")
            return None
    
    def select_multiple_markdown_files(self, parent: Optional[QWidget] = None,
                                     title: str = "Select Markdown Files") -> List[str]:
        """Open file dialog to select multiple markdown files.

        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.

        Returns:
            List of selected file paths.
        """
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                parent,
                title,
                str(self.base_path),
                FileConstants.MARKDOWN_FILTER
            )
            
            validated_paths = []
            for file_path in file_paths:
                validated_path = self.validate_file(file_path)
                if validated_path:
                    validated_paths.append(validated_path)
            
            return validated_paths
        
        except (OSError, RuntimeError) as e:
            ErrorManager.show_error("File Selection Error", f"Failed to open file dialog: {str(e)}")
            return []
    
    def select_directory(self, parent: Optional[QWidget] = None,
                        title: str = "Select Directory") -> Optional[str]:
        """Open directory dialog to select a directory.

        Args:
            parent: Parent widget for the dialog.
            title: Dialog title.

        Returns:
            Selected directory path or None if cancelled.
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
        
        except (OSError, RuntimeError) as e:
            ErrorManager.show_error("Directory Selection Error", f"Failed to open directory dialog: {str(e)}")
            return None
    
    def validate_file(self, file_path: str) -> Optional[str]:
        """Validate that a file exists and is readable.

        Args:
            file_path: Path to validate.

        Returns:
            Validated file path or None if invalid.
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(str(path))
            
            if not path.is_file():
                raise InvalidFileTypeError(str(path), ["regular file"])
            
            if not os.access(file_path, os.R_OK):
                raise FileAccessError(str(path), "read")
            
            return str(path.resolve())
        
        except (OSError, ValueError) as e:
            # Log the error but return None for validation failure in UI context
            logger = logging.getLogger(__name__)
            logger.warning(f"File validation failed for '{file_path}': {e}")
            return None
    
    def find_markdown_files(self, directory: Optional[str] = None, 
                          recursive: bool = True) -> List[str]:
        """Find all markdown files in a directory.

        Args:
            directory: Directory to search in. If None, uses base_path.
            recursive: Whether to search recursively.

        Returns:
            List of markdown file paths.
        """
        search_dir = Path(directory) if directory else self.base_path
        
        if not search_dir.exists() or not search_dir.is_dir():
            return []
        
        try:
            markdown_files = []
            for extension in FileConstants.MARKDOWN_EXTENSIONS:
                pattern = f"**/*{extension}" if recursive else f"*{extension}"
                markdown_files.extend(search_dir.glob(pattern))

            unique_files = {f.resolve() for f in markdown_files if f.is_file()}
            return [str(file_path) for file_path in sorted(unique_files)]
        
        except (OSError, ValueError) as e:
            logger.warning(f"Error finding markdown files in '{search_dir}': {e}")
            return []
    
    def save_file(self, content: str, file_path: Optional[str] = None, 
                  parent: Optional[QWidget] = None) -> Optional[str]:
        """Save content to a file.

        Args:
            content: Content to save.
            file_path: File path to save to. If None, opens save dialog.
            parent: Parent widget for dialog.

        Returns:
            Path where file was saved, or None if cancelled/failed.
        """
        try:
            # Validate content size
            target_encoding = self._resolve_save_encoding(file_path)
            content_size = len(content.encode(target_encoding))
            max_size = FileConstants.MAX_FILE_SIZE_MB * 1024 * 1024
            if content_size > max_size:
                raise FileSizeError("content", content_size, max_size)
            
            if file_path is None:
                file_path, _ = QFileDialog.getSaveFileName(
                    parent,
                    "Save Markdown File",
                    str(self.base_path),
                    FileConstants.MARKDOWN_FILTER
                )
                
                if not file_path:
                    return None
            
            # Ensure the directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file using preserved or detected encoding
            with open(file_path, 'w', encoding=target_encoding) as f:
                f.write(content)

            self._file_encodings[str(Path(file_path).resolve())] = target_encoding
            
            return file_path
        
        except (OSError, UnicodeEncodeError) as e:
            logger.error(f"Failed to save file '{file_path}': {e}")
            raise FileWriteError(file_path or "unknown", str(e))
        except RuntimeError as e:
            ErrorManager.show_error("Save Error", f"Failed to save file: {str(e)}")
            return None
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read content from a file.

        Args:
            file_path: Path to file to read.

        Returns:
            File content or None if failed.
        """
        try:
            validated_path = self.validate_file(file_path)
            if not validated_path:
                # validate_file already logs the specific error
                return None
            
            raw_bytes = Path(validated_path).read_bytes()
            detected_encoding = self._detect_encoding_from_bytes(raw_bytes)
            content = raw_bytes.decode(detected_encoding)
            self._file_encodings[str(Path(validated_path).resolve())] = detected_encoding
                
            # Check for reasonable file size
            if len(content) > FileConstants.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise FileSizeError(validated_path, len(content), FileConstants.MAX_FILE_SIZE_MB * 1024 * 1024)
                
            return content
        
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading file '{file_path}': {e}")
            raise FileReadError(file_path, "File encoding not supported")
        except OSError as e:
            logger.error(f"Failed to read file '{file_path}': {e}")
            raise FileReadError(file_path, str(e))
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get information about a file.

        Args:
            file_path: Path to file.

        Returns:
            Dictionary with file information or None if file doesn't exist.
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
        
        except (OSError, ValueError) as e:
            logger.warning(f"Failed to get file info for '{file_path}': {e}")
            return None
        
    def resolve_relative_markdown_link(self, current_file_path: str, link_path: str) -> Optional[str]:
        """Resolve a relative link from a markdown file to an absolute path.

        Args:
            current_file_path: The absolute path of the currently open markdown file.
            link_path: The relative path from the link (e.g., "facets/facets.md").

        Returns:
            The resolved absolute file path if it exists and is a markdown file, otherwise None.
        """
        try:
            current_dir = Path(current_file_path).parent
            target_path = (current_dir / link_path).resolve()
            
            # Check if the file exists and has a markdown extension
            if target_path.exists() and target_path.suffix.lower() in FileConstants.MARKDOWN_EXTENSIONS:
                return str(target_path)
                
            return None
            
        except (ValueError, OSError) as e:
            logger.warning(f"Failed to resolve path '{link_path}' from '{current_file_path}': {e}")
            return None
