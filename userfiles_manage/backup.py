"""Back up a user profile folder into a backup root, keyed by profile name."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .scanner import scan_user_files


def backup_user_files(
    profile_dir: str | os.PathLike, backup_root: str | os.PathLike
) -> Path:
    """Copy every file under ``profile_dir`` into ``backup_root/<profile_name>``.

    The destination folder is named after the profile folder itself (e.g.
    backing up ``/home/alice`` produces ``<backup_root>/alice/...``), and the
    relative directory structure of the profile is preserved underneath it.

    Args:
        profile_dir: Path to the user profile folder to back up.
        backup_root: Path to the folder where backups are stored.

    Returns:
        The path to the profile-specific backup folder that was created or
        updated (``<backup_root>/<profile_name>``).

    Raises:
        FileNotFoundError: If ``profile_dir`` does not exist.
        NotADirectoryError: If ``profile_dir`` is not a directory.
    """
    profile_path = Path(profile_dir).resolve()
    profile_name = profile_path.name
    destination_root = Path(backup_root) / profile_name

    entries = scan_user_files(profile_path)
    destination_root.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        source_file = profile_path / entry.relative_path
        destination_file = destination_root / entry.relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)

    return destination_root


def list_backed_up_profiles(backup_root: str | os.PathLike) -> list[str]:
    """Return the names of the profiles that have a backup under ``backup_root``."""
    root = Path(backup_root)
    if not root.exists():
        return []
    return sorted(child.name for child in root.iterdir() if child.is_dir())
