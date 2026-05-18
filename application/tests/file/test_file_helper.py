"""Tests for FileHelper encoding and filesystem behaviors."""

from pathlib import Path

import pytest

import utils.file_helper as file_helper_mod  # noqa: E402
from utils.constants import FileConstants  # noqa: E402
from utils.exceptions import FileNotFoundError, FileSizeError, FileWriteError  # noqa: E402
from utils.file_helper import FileHelper  # noqa: E402


class TestFileHelperEncoding:
    def test_file_helper_cp1252_roundtrip_preserves_smart_quote(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        markdown_path = tmp_path / "roundtrip.md"
        original_content = "It was supposed to be ’just’.\n"

        markdown_path.write_bytes(original_content.encode(FileConstants.ENCODING_CP1252))

        loaded_content = helper.read_file(str(markdown_path))
        assert loaded_content == original_content

        saved_path = helper.save_file(loaded_content, file_path=str(markdown_path))
        assert saved_path == str(markdown_path)
        assert markdown_path.read_bytes() == original_content.encode(FileConstants.ENCODING_CP1252)

    def test_file_helper_reads_utf8_smart_quote_without_mojibake(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        markdown_path = tmp_path / "utf8.md"
        original_content = "There are too much ECTS at stake to ’just’.\n"

        markdown_path.write_bytes(original_content.encode(FileConstants.ENCODING_UTF8))

        loaded_content = helper.read_file(str(markdown_path))

        assert loaded_content == original_content
        assert "â€™" not in loaded_content

    def test_file_helper_save_rejects_non_cp1252_for_cp1252_file(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        markdown_path = tmp_path / "cp1252_existing.md"
        markdown_path.write_bytes("cp1252 ’baseline’\n".encode(FileConstants.ENCODING_CP1252))

        _ = helper.read_file(str(markdown_path))
        # Lock save encoding: charset detection can pick utf-8 on some environments; we test cp1252 guardrails.
        helper._file_encodings[str(markdown_path.resolve())] = FileConstants.ENCODING_CP1252

        with pytest.raises(FileWriteError):
            helper.save_file("Unsupported 😀\n", file_path=str(markdown_path))


class TestFileHelperIo:
    def test_find_markdown_files_recursive_and_flat(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        (tmp_path / "root.md").write_text("a\n", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "inner.md").write_text("b\n", encoding="utf-8")

        shallow = helper.find_markdown_files(str(tmp_path), recursive=False)
        deep = helper.find_markdown_files(str(tmp_path), recursive=True)

        assert any(p.endswith("root.md") for p in shallow)
        assert not any("inner.md" in p for p in shallow)
        assert any(p.endswith("inner.md") for p in deep)

    def test_find_markdown_files_missing_directory_returns_empty(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        assert helper.find_markdown_files(str(tmp_path / "nonexistent")) == []

    def test_find_markdown_files_dedupes_same_file(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        (tmp_path / "only.md").write_text("x\n", encoding="utf-8")
        paths = helper.find_markdown_files(str(tmp_path), recursive=True)
        assert paths.count(str((tmp_path / "only.md").resolve())) == 1

    def test_get_file_info_present_and_missing(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        f = tmp_path / "x.md"
        f.write_text("hi", encoding="utf-8")
        info = helper.get_file_info(str(f))
        assert info is not None
        assert info["name"] == "x.md"
        assert info["is_file"] is True
        assert helper.get_file_info(str(tmp_path / "missing.md")) is None

    def test_resolve_relative_markdown_link(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        current = tmp_path / "chapter" / "here.md"
        current.parent.mkdir(parents=True)
        current.write_text("x", encoding="utf-8")
        peer = tmp_path / "chapter" / "peer.md"
        peer.write_text("y", encoding="utf-8")

        resolved = helper.resolve_relative_markdown_link(str(current), "peer.md")
        assert resolved == str(peer.resolve())

        assert helper.resolve_relative_markdown_link(str(current), "missing.md") is None

        txt = tmp_path / "chapter" / "note.txt"
        txt.write_text("z", encoding="utf-8")
        assert helper.resolve_relative_markdown_link(str(current), "note.txt") is None

    def test_validate_and_read_raise_for_missing_file(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        missing = str(tmp_path / "nope.md")
        with pytest.raises(FileNotFoundError):
            helper.validate_file(missing)
        with pytest.raises(FileNotFoundError):
            helper.read_file(missing)

    def test_validate_returns_resolved_path_for_readable_file(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        f = tmp_path / "ok.md"
        f.write_text("k", encoding="utf-8")
        assert helper.validate_file(str(f)) == str(f.resolve())

    def test_save_new_file_uses_utf8(self, tmp_path: Path) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        target = tmp_path / "new.md"
        helper.save_file("Pi π\n", file_path=str(target))
        raw = target.read_bytes()
        assert raw.decode(FileConstants.ENCODING_UTF8) == "Pi π\n"

    def test_save_file_raises_file_size_error_when_content_too_large(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        monkeypatch.setattr(file_helper_mod.FileConstants, "MAX_FILE_SIZE_MB", 0)
        out = tmp_path / "big.md"
        with pytest.raises(FileSizeError):
            helper.save_file("hello\n", file_path=str(out))

    def test_read_file_raises_file_size_error_when_plaintext_huge(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        helper = FileHelper(base_path=str(tmp_path))
        f = tmp_path / "hits_limit.md"
        f.write_bytes(b"x")
        monkeypatch.setattr(file_helper_mod.FileConstants, "MAX_FILE_SIZE_MB", 0)
        with pytest.raises(FileSizeError):
            helper.read_file(str(f))
