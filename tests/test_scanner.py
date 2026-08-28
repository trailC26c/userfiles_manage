import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from userfiles_manage.scanner import scan_user_files


def make_profile(tmp_path):
    profile_dir = tmp_path / "alice"
    profile_dir.mkdir()
    (profile_dir / "notes.txt").write_text("hello")
    docs_dir = profile_dir / "Documents"
    docs_dir.mkdir()
    (docs_dir / "report.docx").write_text("report contents")
    return profile_dir


def test_scan_user_files_lists_all_files(tmp_path):
    profile_dir = make_profile(tmp_path)

    entries = scan_user_files(profile_dir)

    relative_paths = sorted(entry.relative_path for entry in entries)
    assert relative_paths == ["Documents/report.docx", "notes.txt"]


def test_scan_user_files_reports_size(tmp_path):
    profile_dir = make_profile(tmp_path)

    entries = scan_user_files(profile_dir)
    notes_entry = next(e for e in entries if e.relative_path == "notes.txt")

    assert notes_entry.size == len("hello")


def test_scan_user_files_missing_profile_raises(tmp_path):
    missing_dir = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        scan_user_files(missing_dir)


def test_scan_user_files_not_a_directory_raises(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("data")

    with pytest.raises(NotADirectoryError):
        scan_user_files(file_path)


def test_entry_to_dict_is_json_serializable(tmp_path):
    profile_dir = make_profile(tmp_path)

    entries = scan_user_files(profile_dir)

    json.dumps([entry.to_dict() for entry in entries])
