#!/usr/bin/env python3
"""Check if a version number is PEP-440 compliant.

Optionally compare it against a version specified in a python file or the PKG-INFO
metadata file.

"""

import argparse
import re
import sys
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from pathlib import Path
from typing import Final
from typing import cast

pattern: Final = (
    r"^(?P<version>\d+\.\d+)(?P<extraversion>(?:\.\d+)*)"
    r"(?:(?P<prerel>[ab]|rc)\d+(?:\.\d+)?)?(?P<postdev>(\.post(?P<post>\d+))?"
    r"(\.dev(?P<dev>\d+))?)?$"
)


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
        sys.stdout.write(f"Found '{egg_info_dirs[0]}'\n")
        return egg_info_dirs[0] / "PKG-INFO"
    sys.stderr.write("No filename provided and no '*.egg-info' directory found\n")
    return Path()


def get_version_from_module(file_name: Path) -> str:
    """Get the version from the module."""
    spec = spec_from_file_location("module.name", file_name)
    if spec is None:
        sys.stderr.write(f"Error loading file '{file_name}'")
        sys.exit(1)
    module = module_from_spec(spec)
    assert spec.loader is not None  # noqa: S101
    try:
        spec.loader.exec_module(module)
    except (FileNotFoundError, ImportError, SyntaxError) as e:
        sys.stderr.write(f"Error loading file '{file_name}': {e}")
        sys.exit(1)
    try:
        version = module.__version__
        if not isinstance(version, str):
            sys.stderr.write(f"Version in '{file_name}' is not a string")
            sys.exit(1)
        return cast(str, module.__version__)
    except AttributeError:
        sys.stderr.write(f"Module '{file_name}' has no __version__ attribute")
        sys.exit(1)


def get_version_from_pkg_info(file_path: Path) -> str:
    """Get the version from the file."""
    if file_path.is_dir():
        file_path = guess_file_name(file_path)
    try:
        with file_path.open("r") as f:
            for line in f:
                if line.startswith("Version:"):
                    sys.stdout.write(f"Found 'Version:' in '{file_path}'\n")
                    return line.split(":")[1].strip()
    except (FileNotFoundError, IsADirectoryError) as e:
        sys.stderr.write(f"Error loading file '{file_path}': {e}\n")
        return ""
    sys.stderr.write(f"No Version found in '{file_path}'\n")
    return ""


def get_version_from_file(file_name: str) -> str:
    """Get the version from the filename file."""
    file_path = Path(file_name)
    if file_name.endswith(".py"):
        return get_version_from_module(file_path)
    sys.stdout.write(f"Warning: filename {file_name} does not end with '.py'\n")
    sys.stdout.write(f"Checking version in '{file_name or '*.egg-info/PKG-INFO'}'\n")
    return get_version_from_pkg_info(file_path)


def check_version(version: str) -> bool:
    """Check if the version is PEP-440 compliant."""
    return bool(re.match(pattern, version))


def check_versions(version: str, tag_name: str) -> list[str]:
    """Check if the version in the filename file matches the given version."""
    errors = []
    if version != tag_name:
        errors.append(f"Version '{version}' does not match tag '{tag_name}'")
    if not check_version(tag_name):
        errors.append(f"Tag name '{tag_name}' is not PEP-440 compliant")
    if not check_version(version):
        errors.append(f"Version '{version}' is not PEP-440 compliant")
    return errors


def check_version_number_only(version: str) -> int:
    """Check if the version number is PEP-440 compliant."""
    if not check_version(version):
        sys.stderr.write(f"Tag name '{version}' is not PEP-440 compliant\n")
        return 1
    sys.stdout.write(f"Tag name '{version}' is PEP-440 compliant\n")
    return 0


def check(tag_name: str, file_name: str, *, check_only: bool) -> int:
    """Check if the version in the filename file matches the given version."""
    if check_only:
        if file_name:
            sys.stderr.write(
                "Error: --check-version-number-only "
                "can only be used without a filename\n",
            )
            return 1
        return check_version_number_only(tag_name)
    version = get_version_from_file(file_name)
    errors = check_versions(version, tag_name)
    if errors:
        for error in errors:
            sys.stderr.write(f"Error: {error}\n")
        return len(errors)
    return 0


def main() -> None:
    """Check if the version in the filename file matches the given version."""
    parser = argparse.ArgumentParser(
        description=("Check if the version is PEP-440 conformant."),
    )
    parser.add_argument("version", help="The version number to compare against.")
    parser.add_argument(
        "filename",
        nargs="?",
        default="",
        help="The path to the file containing the version information.",
    )
    parser.add_argument(
        "--check-version-number-only",
        action="store_true",
        help=(
            "Only check if the version number is PEP-440 compliant "
            "without trying to retrieve a version from a file."
        ),
    )

    args = parser.parse_args()

    exit_code = check(
        args.version,
        args.filename,
        check_only=args.check_version_number_only,
    )  # pragma: no cover
    sys.exit(exit_code)  # pragma: no cover


if __name__ == "__main__":
    main()
