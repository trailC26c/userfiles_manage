"""Scan a user profile folder and report the files found within it."""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterator, List


@dataclass
class FileEntry:
    """Metadata describing a single file found while scanning a profile folder."""

    relative_path: str
    size: int
    modified_time: float

    def to_dict(self) -> dict:
        return asdict(self)


def scan_user_files(profile_dir: str | os.PathLike) -> List[FileEntry]:
    """Recursively scan ``profile_dir`` and return metadata for every file found.

    Args:
        profile_dir: Path to the user profile folder to scan.

    Returns:
        A list of :class:`FileEntry` objects, one per file, sorted by
        relative path for deterministic output. Paths are relative to
        ``profile_dir`` and use forward slashes regardless of platform.

    Raises:
        FileNotFoundError: If ``profile_dir`` does not exist.
        NotADirectoryError: If ``profile_dir`` is not a directory.
    """
    root = Path(profile_dir)
    if not root.exists():
        raise FileNotFoundError(f"profile folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"profile path is not a directory: {root}")

    entries = []
    for file_path in _iter_files(root):
        stat = file_path.stat()
        relative_path = file_path.relative_to(root).as_posix()
        entries.append(
            FileEntry(
                relative_path=relative_path,
                size=stat.st_size,
                modified_time=stat.st_mtime,
            )
        )

    entries.sort(key=lambda entry: entry.relative_path)
    return entries


def _iter_files(root: Path) -> Iterator[Path]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            yield Path(dirpath) / filename
