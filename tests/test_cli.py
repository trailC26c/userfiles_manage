import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from userfiles_manage.cli import main


def make_profile(tmp_path, name="alice"):
    profile_dir = tmp_path / "profiles" / name
    profile_dir.mkdir(parents=True)
    (profile_dir / "notes.txt").write_text("hello")
    return profile_dir


def test_cli_scan_json_output(tmp_path, capsys):
    profile_dir = make_profile(tmp_path)

    exit_code = main(["scan", str(profile_dir), "--json"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output == [{"relative_path": "notes.txt", "size": 5, "modified_time": output[0]["modified_time"]}]


def test_cli_scan_missing_profile_returns_error(tmp_path, capsys):
    exit_code = main(["scan", str(tmp_path / "missing")])

    assert exit_code == 1
    assert "Error" in capsys.readouterr().err


def test_cli_backup_and_restore_round_trip(tmp_path, capsys):
    profile_dir = make_profile(tmp_path)
    backup_root = tmp_path / "backups"
    restore_dir = tmp_path / "restored"

    backup_exit = main(["backup", str(profile_dir), str(backup_root)])
    restore_exit = main(
        ["restore", str(backup_root), profile_dir.name, str(restore_dir)]
    )

    assert backup_exit == 0
    assert restore_exit == 0
    assert (restore_dir / "notes.txt").read_text() == "hello"
