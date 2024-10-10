"""Test the check_version function happy path with Hypothesis."""

from typing import Literal

from hypothesis import given
from hypothesis import strategies as st

from vercheck.vercheck import check_version


@given(
    required_parts=st.lists(st.integers(min_value=0), min_size=3, max_size=5),
    abrc=st.sampled_from(["a", "b", "rc", ""]),
    post=st.one_of(st.integers(min_value=0), st.none()),
    dev=st.one_of(st.integers(min_value=0), st.none()),
)
def test_check_version(
    required_parts: list[int],
    abrc: Literal["a", "b", "rc", ""],
    post: int | None,
    dev: int | None,
) -> None:
    """Test the check_version function.

    The version is constructed in compliance with the pattern:
    ``[N!]N(.N)*[{a|b|rc}N][.postN][.devN]``.
    """
    prerel = f"{required_parts[-1]}{abrc}{required_parts[-2]}"
    postdev = f".post{post}" if post else ""
    postdev += f".dev{dev}" if dev else ""
    version = f"{'.'.join(map(str, required_parts[:-2]))}.{prerel}{postdev}"

    assert check_version(version)
