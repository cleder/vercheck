"""Test cases for pyproject.toml support."""

import pathlib
import tempfile
from collections.abc import Generator

import pytest

from vercheck import vercheck

TEST_DIR = pathlib.Path(__file__).parent


@pytest.fixture
def standard_pyproject_toml() -> Generator[pathlib.Path, None, None]:
    """Create a temporary pyproject.toml file with standard version."""
    with tempfile.NamedTemporaryFile(suffix="pyproject.toml", mode="w", encoding="utf-8") as temp_file:
        temp_file.write("""
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vercheck"
version = "0.4.0"
description = "Version checking tool"
authors = [
    {name = "Test User", email = "test@example.com"}
]
        """)
        temp_file.flush()
        yield pathlib.Path(temp_file.name)


@pytest.fixture
def poetry_pyproject_toml() -> Generator[pathlib.Path, None, None]:
    """Create a temporary pyproject.toml file with poetry version."""
    with tempfile.NamedTemporaryFile(suffix="pyproject.toml", mode="w") as temp_file:
        temp_file.write("""
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "vercheck"
version = "0.5.0"
description = "Version checking tool"
authors = ["Test User <test@example.com>"]
        """)
        temp_file.flush()
        yield pathlib.Path(temp_file.name)


@pytest.fixture
def invalid_pyproject_toml() -> Generator[pathlib.Path, None, None]:
    """Create a temporary invalid pyproject.toml file."""
    with tempfile.NamedTemporaryFile(suffix="pyproject.toml", mode="w") as temp_file:
        temp_file.write("""
[build-system
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
        """)
        temp_file.flush()
        yield pathlib.Path(temp_file.name)


@pytest.fixture
def no_version_pyproject_toml() -> Generator[pathlib.Path, None, None]:
    """Create a temporary pyproject.toml file without version."""
    with tempfile.NamedTemporaryFile(suffix="pyproject.toml", mode="w") as temp_file:
        temp_file.write("""
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vercheck"
description = "Version checking tool"
        """)
        temp_file.flush()
        yield pathlib.Path(temp_file.name)


def test_get_version_from_standard_pyproject_toml(
    standard_pyproject_toml: pathlib.Path,
) -> None:
    """Test getting version from standard pyproject.toml format."""
    version = vercheck.get_version_from_pyproject_toml(standard_pyproject_toml)
    assert version == "0.4.0"


def test_get_version_from_poetry_pyproject_toml(
    poetry_pyproject_toml: pathlib.Path,
) -> None:
    """Test getting version from poetry pyproject.toml format."""
    version = vercheck.get_version_from_pyproject_toml(poetry_pyproject_toml)
    assert version == "0.5.0"


def test_get_version_from_invalid_pyproject_toml(
    invalid_pyproject_toml: pathlib.Path,
) -> None:
    """Test handling invalid TOML file."""
    version = vercheck.get_version_from_pyproject_toml(invalid_pyproject_toml)
    assert version == ""


def test_get_version_from_no_version_pyproject_toml(
    no_version_pyproject_toml: pathlib.Path,
) -> None:
    """Test handling pyproject.toml without version."""
    version = vercheck.get_version_from_pyproject_toml(no_version_pyproject_toml)
    assert version == ""


def test_check_with_standard_pyproject_toml(
    standard_pyproject_toml: pathlib.Path,
) -> None:
    """Test check function with standard pyproject.toml."""
    assert vercheck.check("0.4.0", str(standard_pyproject_toml), check_only=False) == 0


def test_check_with_poetry_pyproject_toml(
    poetry_pyproject_toml: pathlib.Path,
) -> None:
    """Test check function with poetry pyproject.toml."""
    assert vercheck.check("0.5.0", str(poetry_pyproject_toml), check_only=False) == 0


def test_check_fail_with_wrong_version_in_pyproject_toml(
    standard_pyproject_toml: pathlib.Path,
) -> None:
    """Test check function fails with wrong version."""
    assert vercheck.check("0.3.0", str(standard_pyproject_toml), check_only=False) == 1
