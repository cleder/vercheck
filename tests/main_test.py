"""Test cases for the __main__ module."""

import pathlib

import pytest

from vercheck import vercheck

TEST_DIR = pathlib.Path(__file__).parent


def test_check_succeeds() -> None:
    """Check returns a status code of zero."""
    assert vercheck.check("0.1.0", str(TEST_DIR / "data"), check_only=False) == 0


def test_check_with_flag_succeeds() -> None:
    """Check returns a status code of zero."""
    assert vercheck.check("0.1.0", "", check_only=True) == 0


def test_check_with_flag_and_filename_fails() -> None:
    """Check returns a status code of one."""
    assert vercheck.check("0.1.0", str(TEST_DIR / "data"), check_only=True) == 1


def test_check_file_succeeds() -> None:
    """It exits with a status code of zero."""
    assert (
        vercheck.check(
            "0.1.0",
            str(TEST_DIR / "data" / "pkg.egg-info" / "PKG-INFO"),
            check_only=False,
        )
        == 0
    )


def test_check_fails_with_wrong_version() -> None:
    """It exits with a status code of one."""
    assert vercheck.check("0.1.1", str(TEST_DIR / "data"), check_only=False) == 1


def test_check_fails_with_wrong_tag_name() -> None:
    """It exits with a status code of one."""
    assert (
        vercheck.check(
            "0.1.0a",
            str(TEST_DIR / "data" / "BAD-PKG-INFO"),
            check_only=False,
        )
        == 3
    )


def test_check_fails_with_wrong_path() -> None:
    """It exits with a status code of one."""
    assert vercheck.check("0.1.0", str(TEST_DIR), check_only=False) == 2


def test_check_fails_when_path_not_exist() -> None:
    """It exits with a status code of one."""
    assert vercheck.check("0.1.0", str(TEST_DIR / "not_exist"), check_only=False) == 2


def test_check_fails_with_no_version() -> None:
    """It exits with a status code of one."""
    assert (
        vercheck.check(
            "0.1.0",
            str(TEST_DIR / "data" / "EMPTY-PKG-INFO"),
            check_only=False,
        )
        == 2
    )


def test_check_fails_with_no_filename() -> None:
    """It exits with a status code of one."""
    assert vercheck.check("0.1.0", "", check_only=False) == 2


def test_args() -> None:
    """It exits with a status code of zero."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert isinstance(excinfo.value.code, int)
    assert excinfo.value.code >= 2


def test_get_version_from_pkg_info_empty() -> None:
    """Get the version from the PKG-INFO file."""
    assert (
        vercheck.get_version_from_pkg_info(TEST_DIR / "data" / "EMPTY-PKG-INFO") == ""
    )


def test_module_version() -> None:
    """Load a python module and get the version."""
    assert vercheck.get_version_from_module(TEST_DIR / "data" / "about.py") == "0.1.0a1"


def test_module_version_with_import_error() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "data" / "import_error.py")
    assert excinfo.value.code == 1


def test_module_version_with_syntax_error() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "data" / "syntax_error.py")
    assert excinfo.value.code == 1


def test_module_version_with_empty_file() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "data" / "empty.py")
    assert excinfo.value.code == 1


def test_module_version_with_file_does_not_exist() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "does" / "not" / "exist.py")
    assert excinfo.value.code == 1


def test_module_version_with_directory() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "data")
    assert excinfo.value.code == 1


def test_check_python_module_with_version() -> None:
    """Load a python module and check the version."""
    assert (
        vercheck.check("0.1.0a1", str(TEST_DIR / "data" / "about.py"), check_only=False)
        == 0
    )


def test_check_version_number_only() -> None:
    """Check if the version number is PEP-440 compliant."""
    assert vercheck.check("0.1.0", "", check_only=True) == 0


def test_check_version_number_only_fail() -> None:
    """Check if the version number is PEP-440 compliant."""
    assert vercheck.check("0.1.0a", "", check_only=True) == 1


def test_get_version_from_module_float_version() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "data" / "float_version.py")
    assert excinfo.value.code == 1


@pytest.mark.parametrize(
    "version",
    ["0.1a.0", "0.1.0a.dev0", "0.1.0a2.post", "0.1.0post1", "0.1.0a1.dev2.post0"],
)
def test_check_version_fail(version: str) -> None:
    """Test check_version function with invalid versions."""
    assert not vercheck.check_version(version)


@pytest.mark.parametrize(
    "version",
    [
        "0.1.0",
        "1.1.0a1",
        "2.1.0b2",
        "3.1.0rc1",
        "4.1.0.post1",
        "5.1.0.dev1",
        "6.1.0a1.dev1",
        "7.2.3.post4.dev5",
    ],
)
def test_check_version_success(version: str) -> None:
    """Test check_version function with valid versions.

    More comprehensive tests are in hypothesis_test.py.
    """
    assert vercheck.check_version(version)
