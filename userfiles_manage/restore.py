"""Restore a previously backed-up user profile folder."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .scanner import scan_user_files


def restore_user_files(
    backup_root: str | os.PathLike,
    profile_name: str,
    restore_dir: str | os.PathLike,
) -> Path:
    """Restore files for ``profile_name`` from ``backup_root`` into ``restore_dir``.

    Args:
        backup_root: Path to the folder containing profile backups, as
            produced by :func:`userfiles_manage.backup.backup_user_files`.
        profile_name: Name of the profile folder to restore (matches the
            folder name created under ``backup_root`` during backup).
        restore_dir: Destination folder that the profile's files should be
            restored into. It is created if it does not already exist.

    Returns:
        The path to the restore destination folder.

    Raises:
        FileNotFoundError: If no backup exists for ``profile_name`` under
            ``backup_root``.
    """
    source_root = Path(backup_root) / profile_name
    if not source_root.exists() or not source_root.is_dir():
        raise FileNotFoundError(
            f"no backup found for profile '{profile_name}' under {backup_root}"
        )

    destination_root = Path(restore_dir)
    destination_root.mkdir(parents=True, exist_ok=True)

    entries = scan_user_files(source_root)
    for entry in entries:
        source_file = source_root / entry.relative_path
        destination_file = destination_root / entry.relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)

    return destination_root
