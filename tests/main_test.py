"""Test cases for the __main__ module."""

import pathlib

import pytest

from vercheck import vercheck

TEST_DIR = pathlib.Path(__file__).parent


def test_check_succeeds() -> None:
    """It exits with a status code of zero."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.0", str(TEST_DIR / "data"))
    assert excinfo.value.code == 0


def test_check_file_succeeds() -> None:
    """It exits with a status code of zero."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.0", str(TEST_DIR / "data" / "pkg.egg-info" / "PKG-INFO"))
    assert excinfo.value.code == 0


def test_check_fails_with_wrong_version() -> None:
    """It exits with a status code of one."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.1", str(TEST_DIR / "data"))
    assert excinfo.value.code == 1


def test_check_fails_with_wrong_tag_name() -> None:
    """It exits with a status code of one."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.0a", str(TEST_DIR / "data" / "BAD-PKG-INFO"))
    assert excinfo.value.code == 1


def test_check_fails_with_wrong_path() -> None:
    """It exits with a status code of one."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.0", str(TEST_DIR))
    assert excinfo.value.code == 1


def test_check_fails_when_path_not_exist() -> None:
    """It exits with a status code of one."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.0", str(TEST_DIR / "not_exist"))
    assert excinfo.value.code == 1


def test_check_fails_with_no_version() -> None:
    """It exits with a status code of one."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.check("0.1.0", str(TEST_DIR / "data" / "EMPTY-PKG-INFO"))
    assert excinfo.value.code == 1


def test_args() -> None:
    """It exits with a status code of zero."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert excinfo.value.code == 2
