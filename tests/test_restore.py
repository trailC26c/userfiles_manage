import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from userfiles_manage.backup import backup_user_files
from userfiles_manage.restore import restore_user_files


def make_profile(tmp_path, name="alice"):
    profile_dir = tmp_path / "profiles" / name
    profile_dir.mkdir(parents=True)
    (profile_dir / "notes.txt").write_text("hello")
    docs_dir = profile_dir / "Documents"
    docs_dir.mkdir()
    (docs_dir / "report.docx").write_text("report contents")
    return profile_dir


def test_restore_recreates_files(tmp_path):
    profile_dir = make_profile(tmp_path)
    backup_root = tmp_path / "backups"
    backup_user_files(profile_dir, backup_root)

    restore_dir = tmp_path / "restored" / "alice"
    destination = restore_user_files(backup_root, "alice", restore_dir)

    assert destination == restore_dir
    assert (restore_dir / "notes.txt").read_text() == "hello"
    assert (restore_dir / "Documents" / "report.docx").read_text() == "report contents"


def test_restore_missing_backup_raises(tmp_path):
    backup_root = tmp_path / "backups"
    backup_root.mkdir()

    with pytest.raises(FileNotFoundError):
        restore_user_files(backup_root, "unknown", tmp_path / "restored")
