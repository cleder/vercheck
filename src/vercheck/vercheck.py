#!/usr/bin/env python3
"""Check if the version in the about.py file matches the given version.

Usage: check_version_tag.py <filename> <tag_version>

This script checks if the version in the project metadata matches the given version.

"""

import argparse
import re
import sys
from pathlib import Path
from typing import Final

pattern: Final = (
    r"^(?P<version>\d+\.\d+)(?P<extraversion>(?:\.\d+)*)"
    r"(?:(?P<prerel>[abc]|rc)\d+(?:\.\d+)?)?(?P<postdev>(\.post(?P<post>\d+))?"
    r"(\.dev(?P<dev>\d+))?)?$"
)
__version__: Final = "0.1.0"


def guess_file_name(path: Path) -> Path:
    """Guesses the file name of the PKG-INFO file within an .egg-info directory.

    This function searches for directories with the .egg-info extension in the current
    directory. If such a directory is found, it returns the path to the PKG-INFO file
    within that directory.
    If no .egg-info directory is found, it writes an error message to stdout and
    exits the program with a status code of 1.

    Returns:
        Path: The path to the PKG-INFO file within the found .egg-info directory.

    Raises:
        SystemExit: If no .egg-info directory is found.

    """
    """"""
    egg_info_dirs = list(path.glob("*.egg-info"))
    if egg_info_dirs:
        return egg_info_dirs[0] / "PKG-INFO"
    sys.stderr.write("No filename provided and no '*.egg-info' directory found\n")
    sys.exit(1)


def get_version_from_pkg_info(file_name: str) -> str:
    """Get the version from the file."""
    file_path = Path(file_name)
    if not file_name or file_path.is_dir():
        file_path = guess_file_name(file_path)
    try:
        with file_path.open("r") as f:
            for line in f:
                if line.startswith("Version:"):
                    return line.split(":")[1].strip()
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"Error loading file {file_name}: {e}\n")
        sys.exit(1)
    sys.stderr.write(f"No Version found in '{file_name}'\n")
    sys.exit(1)


def check_versions(version: str, tag_name: str) -> list[str]:
    """Check if the version in the filename file matches the given version."""
    errors = []
    if version != tag_name:
        errors.append(f"Version {version} does not match tag {tag_name}")
    if not re.match(pattern, tag_name):
        errors.append(f"Tag name '{tag_name}' is not PEP-386 compliant")
    if not re.match(pattern, version):
        errors.append(f"Version {version} is not PEP-386 compliant")
    return errors


def check(tag_name: str, file_name: str) -> None:
    """Check if the version in the filename file matches the given version."""
    version = get_version_from_pkg_info(file_name)
    errors = check_versions(version, tag_name)
    if errors:
        for error in errors:
            sys.stderr.write(f"Error: {error}\n")
        sys.exit(1)
    sys.exit(0)


def main() -> None:
    """Check if the version in the filename file matches the given version."""
    parser = argparse.ArgumentParser(
        description="Check if the version in the metadata matches the given version.",
    )
    parser.add_argument("tag_version", help="The version tag to compare against.")
    parser.add_argument(
        "filename",
        nargs="?",
        default="",
        help="The path to the file containing the version information.",
    )

    args = parser.parse_args()

    check(args.tag_version, args.filename)  # pragma: no cover


if __name__ == "__main__":
    main()
