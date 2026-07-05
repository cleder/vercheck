#!/usr/bin/env python3
"""Check if a version number is PEP-440 compliant.

Optionally compare it against a version declared in a TOML manifest
(``pyproject.toml``, ``Cargo.toml``, or any other TOML file with an explicit
key path) or a Python module's ``__version__`` attribute.

"""

import argparse
import re
import sys
import tomllib
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


class _AutoDetect:
    """Sentinel marking a bare ``--toml`` (auto-detect mode)."""


AUTO_DETECT: Final = _AutoDetect()

TomlSpec = str | _AutoDetect

DEFAULT_KEY_PATHS: Final[dict[str, tuple[str, ...]]] = {
    "pyproject.toml": ("project", "version"),
    "Cargo.toml": ("package", "version"),
}

KEY_PATH_RE: Final = re.compile(
    r"^(?P<file>.+):(?P<key>[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*)$",
)


def check_version(version: str) -> bool:
    """Check if the version is PEP-440 compliant."""
    return bool(re.match(pattern, version))


def get_version_from_module(file_name: Path) -> str:
    """Get the version from a Python module's __version__ attribute."""
    spec = spec_from_file_location("module.name", file_name)
    if spec is None or spec.loader is None:
        sys.stderr.write(f"Error loading file '{file_name}'\n")
        sys.exit(1)
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (FileNotFoundError, ImportError, SyntaxError) as e:
        sys.stderr.write(f"Error loading file '{file_name}': {e}\n")
        sys.exit(1)
    try:
        version = module.__version__
        if not isinstance(version, str):
            sys.stderr.write(f"Version in '{file_name}' is not a string\n")
            sys.exit(1)
        return cast("str", module.__version__)
    except AttributeError:
        sys.stderr.write(f"Module '{file_name}' has no __version__ attribute\n")
        sys.exit(1)


def parse_toml_spec(spec: str) -> tuple[Path, tuple[str, ...]]:
    """Split a ``--toml`` value into a file path and a key path.

    ``file:dotted.key.path`` gives an explicit key path; otherwise the
    manifest's built-in default key path (keyed by file name) is used.
    """
    match = KEY_PATH_RE.match(spec)
    if match:
        return Path(match["file"]), tuple(match["key"].split("."))
    file_path = Path(spec)
    default = DEFAULT_KEY_PATHS.get(file_path.name)
    if default is None:
        sys.stderr.write(
            f"Error: no default key path known for '{file_path.name}', "
            f"use '{spec}:dotted.key.path' to specify one\n",
        )
        sys.exit(1)
    return file_path, default


def get_version_from_toml(file_path: Path, key_path: tuple[str, ...]) -> str:
    """Get the version string at key_path within a TOML file."""
    dotted = ".".join(key_path)
    try:
        with file_path.open("rb") as f:
            data = tomllib.load(f)
    except OSError as e:
        sys.stderr.write(f"Error: '{file_path}' could not be read: {e}\n")
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        sys.stderr.write(f"Error parsing '{file_path}': {e}\n")
        sys.exit(1)
    node: object = data
    for key in key_path:
        if not isinstance(node, dict) or key not in node:
            sys.stderr.write(f"Error: '{dotted}' not found in '{file_path}'\n")
            sys.exit(1)
        node = node[key]
    if not isinstance(node, str):
        sys.stderr.write(f"Error: '{dotted}' in '{file_path}' is not a string\n")
        sys.exit(1)
    return node


def autodetect_toml_files() -> list[Path]:
    """Find the known manifest files present in the current directory."""
    found = [Path(name) for name in DEFAULT_KEY_PATHS if Path(name).is_file()]
    if not found:
        names = " or ".join(DEFAULT_KEY_PATHS)
        sys.stderr.write(
            f"Error: --toml given with no value and no {names} "
            "found in the current directory\n",
        )
        sys.exit(1)
    return found


def resolve_toml_sources(toml_specs: list[TomlSpec]) -> list[tuple[str, str]]:
    """Resolve --toml specs to (label, version) pairs."""
    if AUTO_DETECT in toml_specs:
        if any(spec != AUTO_DETECT for spec in toml_specs):
            sys.stderr.write(
                "Error: --toml cannot be combined with --toml=<file>\n",
            )
            sys.exit(1)
        sources = [
            (file_path, DEFAULT_KEY_PATHS[file_path.name])
            for file_path in autodetect_toml_files()
        ]
    else:
        sources = [
            parse_toml_spec(spec) for spec in toml_specs if isinstance(spec, str)
        ]
    return [
        (str(file_path), get_version_from_toml(file_path, key_path))
        for file_path, key_path in sources
    ]


def check_versions(resolved: list[tuple[str, str]]) -> list[str]:
    """Check every resolved version is PEP-440 compliant and all agree."""
    errors = [
        f"'{version}' ({label}) is not PEP-440 compliant"
        for label, version in resolved
        if not check_version(version)
    ]
    if len({version for _, version in resolved}) > 1:
        details = ", ".join(f"{label}: {version}" for label, version in resolved)
        errors.append(f"Versions do not match: {details}")
    return errors


def collect_resolved(
    version: str | None,
    toml_specs: list[TomlSpec] | None,
    py_path: str | None,
) -> list[tuple[str, str]]:
    """Gather the given version and every resolved source's version."""
    resolved: list[tuple[str, str]] = []
    if version is not None:
        resolved.append(("the given version", version))
    if toml_specs:
        resolved.extend(resolve_toml_sources(toml_specs))
    if py_path:
        resolved.append((py_path, get_version_from_module(Path(py_path))))
    return resolved


def check(
    version: str | None,
    toml_specs: list[TomlSpec] | None,
    py_path: str | None,
) -> int:
    """Check version compliance and, if a source is given, agreement with it."""
    if toml_specs and py_path:
        sys.stderr.write("Error: --toml and --py are mutually exclusive\n")
        return 1
    if version is None and not toml_specs and not py_path:
        sys.stderr.write("Error: nothing to check: give a version, --toml, or --py\n")
        return 1
    errors = check_versions(collect_resolved(version, toml_specs, py_path))
    if errors:
        for error in errors:
            sys.stderr.write(f"Error: {error}\n")
        return min(len(errors), 255)
    return 0


def main() -> None:
    """Parse arguments and run the check."""
    parser = argparse.ArgumentParser(
        description="Check if a version is PEP-440 compliant.",
    )
    parser.add_argument(
        "version",
        nargs="?",
        default=None,
        help=(
            "The version number to check. If omitted, only the resolved "
            "--toml/--py source is checked for PEP-440 compliance."
        ),
    )
    parser.add_argument(
        "--toml",
        action="append",
        nargs="?",
        const=AUTO_DETECT,
        default=None,
        metavar="FILE[:KEY.PATH]",
        help=(
            "Check the version in a TOML manifest. With no value, "
            "auto-detects 'pyproject.toml'/'Cargo.toml' in the current "
            "directory; if more than one is found, they must agree. "
            "With a value, checks exactly that file (default key path "
            "'project.version'/'package.version', or 'file:dotted.key.path' "
            "to override). Repeatable; when multiple TOML sources are given, "
            "all resolved versions must agree. Put 'version' before --toml "
            "to avoid argparse swallowing it as --toml's value."
        ),
    )
    parser.add_argument(
        "--py",
        default=None,
        metavar="FILE",
        help="Check the __version__ attribute of a Python module.",
    )

    args = parser.parse_args()

    sys.exit(check(args.version, args.toml, args.py))


if __name__ == "__main__":
    main()
