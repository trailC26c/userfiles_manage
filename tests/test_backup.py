import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from userfiles_manage.backup import backup_user_files, list_backed_up_profiles


def make_profile(tmp_path, name="alice"):
    profile_dir = tmp_path / "profiles" / name
    profile_dir.mkdir(parents=True)
    (profile_dir / "notes.txt").write_text("hello")
    docs_dir = profile_dir / "Documents"
    docs_dir.mkdir()
    (docs_dir / "report.docx").write_text("report contents")
    return profile_dir


def test_backup_creates_profile_named_folder(tmp_path):
    profile_dir = make_profile(tmp_path)
    backup_root = tmp_path / "backups"

    destination = backup_user_files(profile_dir, backup_root)

    assert destination == backup_root / "alice"
    assert (destination / "notes.txt").read_text() == "hello"
    assert (destination / "Documents" / "report.docx").read_text() == "report contents"


def test_backup_is_idempotent_and_updates_changed_files(tmp_path):
    profile_dir = make_profile(tmp_path)
    backup_root = tmp_path / "backups"

    backup_user_files(profile_dir, backup_root)
    (profile_dir / "notes.txt").write_text("updated content")
    destination = backup_user_files(profile_dir, backup_root)

    assert (destination / "notes.txt").read_text() == "updated content"


def test_backup_missing_profile_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup_user_files(tmp_path / "missing", tmp_path / "backups")


def test_list_backed_up_profiles(tmp_path):
    backup_root = tmp_path / "backups"
    assert list_backed_up_profiles(backup_root) == []

    profile_dir = make_profile(tmp_path, "alice")
    backup_user_files(profile_dir, backup_root)
    other_profile_dir = make_profile(tmp_path, "bob")
    backup_user_files(other_profile_dir, backup_root)

    assert list_backed_up_profiles(backup_root) == ["alice", "bob"]
