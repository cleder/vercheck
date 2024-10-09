"""Test cases for the __main__ module."""

import pytest

from vercheck import __main__


def test_main_succeeds() -> None:
    """It exits with a status code of zero."""
    with pytest.raises(SystemExit) as excinfo:
        __main__.main("tests/data/PKG-INFO", "0.1.0")
    assert excinfo.value.code == 0
