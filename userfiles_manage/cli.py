"""Command line interface for scanning, backing up and restoring user files."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .backup import backup_user_files
from .restore import restore_user_files
from .scanner import scan_user_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="userfiles_manage",
        description=(
            "Scan, back up and restore user files stored under a user "
            "profile name folder."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser(
        "scan", help="List the files found under a user profile folder."
    )
    scan_parser.add_argument("profile_dir", help="Path to the user profile folder.")
    scan_parser.add_argument(
        "--json", action="store_true", help="Print results as JSON."
    )

    backup_parser = subparsers.add_parser(
        "backup", help="Back up a user profile folder."
    )
    backup_parser.add_argument("profile_dir", help="Path to the user profile folder.")
    backup_parser.add_argument(
        "backup_root", help="Path to the folder where backups are stored."
    )

    restore_parser = subparsers.add_parser(
        "restore", help="Restore a previously backed-up user profile folder."
    )
    restore_parser.add_argument(
        "backup_root", help="Path to the folder containing profile backups."
    )
    restore_parser.add_argument(
        "profile_name", help="Name of the profile folder to restore."
    )
    restore_parser.add_argument(
        "restore_dir", help="Destination folder to restore the files into."
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "scan":
            entries = scan_user_files(args.profile_dir)
            if args.json:
                print(json.dumps([entry.to_dict() for entry in entries], indent=2))
            else:
                for entry in entries:
                    print(f"{entry.relative_path}\t{entry.size} bytes")
                print(f"Total files: {len(entries)}")
        elif args.command == "backup":
            destination = backup_user_files(args.profile_dir, args.backup_root)
            print(f"Backed up files to {destination}")
        elif args.command == "restore":
            destination = restore_user_files(
                args.backup_root, args.profile_name, args.restore_dir
            )
            print(f"Restored files to {destination}")
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
