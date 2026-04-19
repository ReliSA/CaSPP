"""Tests for FileHelper markdown encoding behavior."""

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.constants import FileConstants
from utils.exceptions import FileWriteError
from utils.file_helper import FileHelper


def test_file_helper_cp1252_roundtrip_preserves_smart_quote(tmp_path: Path) -> None:
    helper = FileHelper(base_path=str(tmp_path))
    markdown_path = tmp_path / "roundtrip.md"
    original_content = "It was supposed to be ’just’.\n"

    markdown_path.write_bytes(original_content.encode(FileConstants.ENCODING_CP1252))

    loaded_content = helper.read_file(str(markdown_path))
    assert loaded_content == original_content

    saved_path = helper.save_file(loaded_content, file_path=str(markdown_path))
    assert saved_path == str(markdown_path)
    assert markdown_path.read_bytes() == original_content.encode(FileConstants.ENCODING_CP1252)


def test_file_helper_reads_utf8_smart_quote_without_mojibake(tmp_path: Path) -> None:
    helper = FileHelper(base_path=str(tmp_path))
    markdown_path = tmp_path / "utf8.md"
    original_content = "There are too much ECTS at stake to ’just’.\n"

    markdown_path.write_bytes(original_content.encode(FileConstants.ENCODING_UTF8))

    loaded_content = helper.read_file(str(markdown_path))

    assert loaded_content == original_content
    assert "â€™" not in loaded_content


def test_file_helper_save_rejects_non_cp1252_for_cp1252_file(tmp_path: Path) -> None:
    helper = FileHelper(base_path=str(tmp_path))
    markdown_path = tmp_path / "cp1252_existing.md"
    markdown_path.write_bytes("cp1252 ’baseline’\n".encode(FileConstants.ENCODING_CP1252))

    _ = helper.read_file(str(markdown_path))

    with pytest.raises(FileWriteError):
        helper.save_file("Unsupported 😀\n", file_path=str(markdown_path))
