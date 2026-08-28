# userfiles_manage

This project provides a set of scripts for scanning, backing up and restoring
user files stored under a user profile name folder (e.g. `/home/<user>` or
`C:\Users\<user>`).

## Installation

```bash
pip install -e .
```

## Usage

The `userfiles_manage` package exposes a command line interface, available
either as `userfiles-manage` (after installing) or via
`python -m userfiles_manage.cli`.

### Scan

List every file found under a user profile folder, along with its size:

```bash
userfiles-manage scan /home/alice
userfiles-manage scan /home/alice --json
```

### Backup

Copy all files under a user profile folder into a backup folder named after
the profile, preserving the relative directory structure:

```bash
userfiles-manage backup /home/alice /path/to/backups
# creates /path/to/backups/alice/...
```

Running the same command again updates the backup in place (new or changed
files are copied over).

### Restore

Restore a previously backed-up profile's files into a destination folder:

```bash
userfiles-manage restore /path/to/backups alice /path/to/restore-destination
```

## Development

Install test dependencies and run the test suite with:

```bash
pip install pytest
pytest tests
```