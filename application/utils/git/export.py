"""Export staged files from git index."""

from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .types import GitResult
from . import runner


def export_staged_files_zip(repo_path: str, output_zip_path: str = None) -> GitResult:
    """Export staged files to a zip archive.

    Args:
        repo_path: The git repository path.
        output_zip_path: Optional destination path for the zip archive.

    Returns:
        The git operation result.
    """
    try:
        repo = runner.load_repo(repo_path)
        repo_root = Path(repo.working_dir).resolve()
        staged_entries = runner.get_staged_name_status(repo)
        if not staged_entries:
            return GitResult(False, "No staged changes to export.")

        branch = runner.get_current_branch(repo).replace("/", "_").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_zip_path:
            zip_path = Path(output_zip_path)
        else:
            exports_dir = repo_root.parent / "exports" / repo_root.name
            zip_path = exports_dir / f"staged_changes_{branch}_{timestamp}.zip"

        zip_path.parent.mkdir(parents=True, exist_ok=True)

        deleted_paths = []
        exported_paths = []
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
            for status, rel_path in staged_entries:
                if status == "D":
                    deleted_paths.append(rel_path)
                    continue

                abs_path = Path(repo.working_dir) / rel_path
                if abs_path.exists() and abs_path.is_file():
                    archive.write(abs_path, arcname=rel_path)
                    exported_paths.append(rel_path)

            if deleted_paths:
                deleted_list = "\n".join(deleted_paths)
                archive.writestr("deleted_files.txt", deleted_list)

        cleanup_result = runner.discard_working_tree_changes(repo, preserve_paths=[str(zip_path)])
        if not cleanup_result.get("success"):
            return GitResult(
                False,
                f"Exported staged changes to: {zip_path}\n"
                f"Failed to discard local changes: {cleanup_result.get('message', 'Unknown cleanup error.')}",
                payload={
                    "zip_path": str(zip_path),
                    "exported": exported_paths,
                    "deleted": deleted_paths,
                },
            )

        lines = [
            f"Exported staged changes to: {zip_path}",
            f"Exported {len(exported_paths)} file(s).",
            "Discarded all local tracked and untracked changes so pull can proceed.",
        ]
        if deleted_paths:
            lines.append(f"Included deleted file list for {len(deleted_paths)} file(s) in deleted_files.txt.")

        return GitResult(
            True,
            "\n".join(lines),
            payload={
                "zip_path": str(zip_path),
                "exported": exported_paths,
                "deleted": deleted_paths,
            },
        )
    except Exception as exc:
        return GitResult(False, f"Export staged changes failed: {str(exc)}")
