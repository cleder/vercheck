"""Test cases for the __main__ module."""

import pathlib

import pytest

from vercheck import vercheck

TEST_DIR = pathlib.Path(__file__).parent
DATA_DIR = TEST_DIR / "data"
TOML_DIR = DATA_DIR / "toml"


# -- check_version --------------------------------------------------------


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


# -- get_version_from_module ----------------------------------------------


def test_module_version() -> None:
    """Load a python module and get the version."""
    assert vercheck.get_version_from_module(DATA_DIR / "about.py") == "0.1.0a1"


def test_module_version_with_import_error() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(DATA_DIR / "import_error.py")
    assert excinfo.value.code == 1


def test_module_version_with_syntax_error() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(DATA_DIR / "syntax_error.py")
    assert excinfo.value.code == 1


def test_module_version_with_empty_file() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(DATA_DIR / "empty.py")
    assert excinfo.value.code == 1


def test_module_version_with_file_does_not_exist() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(TEST_DIR / "does" / "not" / "exist.py")
    assert excinfo.value.code == 1


def test_module_version_with_directory() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(DATA_DIR)
    assert excinfo.value.code == 1


def test_get_version_from_module_float_version() -> None:
    """Load a python module and get the version."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_module(DATA_DIR / "float_version.py")
    assert excinfo.value.code == 1


# -- parse_toml_spec --------------------------------------------------------


def test_parse_toml_spec_default_pyproject() -> None:
    """A plain pyproject.toml path uses the built-in default key path."""
    file_path, key_path = vercheck.parse_toml_spec(str(TOML_DIR / "pyproject.toml"))
    assert file_path == TOML_DIR / "pyproject.toml"
    assert key_path == ("project", "version")


def test_parse_toml_spec_default_cargo() -> None:
    """A plain Cargo.toml path uses the built-in default key path."""
    _file_path, key_path = vercheck.parse_toml_spec(str(TOML_DIR / "Cargo.toml"))
    assert key_path == ("package", "version")


def test_parse_toml_spec_explicit_key_path() -> None:
    """An explicit file:dotted.key.path overrides the default."""
    file_path, key_path = vercheck.parse_toml_spec(
        f"{TOML_DIR / 'poetry.toml'}:tool.poetry.version",
    )
    assert file_path == TOML_DIR / "poetry.toml"
    assert key_path == ("tool", "poetry", "version")


def test_parse_toml_spec_single_segment_key_path() -> None:
    """A single-segment (undotted) explicit key path is accepted."""
    file_path, key_path = vercheck.parse_toml_spec(
        f"{TOML_DIR / 'top_level_version.toml'}:version",
    )
    assert file_path == TOML_DIR / "top_level_version.toml"
    assert key_path == ("version",)


def test_parse_toml_spec_unrecognized_name_without_key_path() -> None:
    """A file with no built-in default and no override key path errors."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.parse_toml_spec(str(TOML_DIR / "unrecognized_name.toml"))
    assert excinfo.value.code == 1


# -- get_version_from_toml --------------------------------------------------


def test_get_version_from_toml_success() -> None:
    """Read a version from a valid key path."""
    assert (
        vercheck.get_version_from_toml(
            TOML_DIR / "pyproject.toml",
            ("project", "version"),
        )
        == "0.1.0"
    )


def test_get_version_from_toml_file_not_found() -> None:
    """Error when the toml file does not exist."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_toml(
            TOML_DIR / "does-not-exist.toml",
            ("project", "version"),
        )
    assert excinfo.value.code == 1


def test_get_version_from_toml_directory() -> None:
    """Error (not an unhandled traceback) when the path is a directory."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_toml(TOML_DIR, ("project", "version"))
    assert excinfo.value.code == 1


def test_get_version_from_toml_malformed() -> None:
    """Error when the toml file cannot be parsed."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_toml(
            TOML_DIR / "malformed.toml.invalid",
            ("project", "version"),
        )
    assert excinfo.value.code == 1


def test_get_version_from_toml_key_not_found() -> None:
    """Error when the key path is absent (e.g. a dynamic version)."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_toml(
            TOML_DIR / "dynamic_pyproject.toml",
            ("project", "version"),
        )
    assert excinfo.value.code == 1


def test_get_version_from_toml_non_dict_intermediate() -> None:
    """Error when a key path segment resolves to a non-table value."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_toml(
            TOML_DIR / "non_dict_intermediate.toml",
            ("project", "version"),
        )
    assert excinfo.value.code == 1


def test_get_version_from_toml_non_string_value() -> None:
    """Error when the resolved value is not a string."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.get_version_from_toml(
            TOML_DIR / "non_string_version.toml",
            ("project", "version"),
        )
    assert excinfo.value.code == 1


# -- autodetect_toml_files / resolve_toml_sources ---------------------------


def test_autodetect_toml_files_none_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    """Error when no known manifest is present in the cwd."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        vercheck.autodetect_toml_files()
    assert excinfo.value.code == 1


def test_resolve_toml_sources_autodetect_single(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-detect finds the one manifest present."""
    monkeypatch.chdir(TOML_DIR / "autodetect_single")
    resolved = vercheck.resolve_toml_sources([vercheck.AUTO_DETECT])
    assert resolved == [("pyproject.toml", "0.1.0")]


def test_resolve_toml_sources_autodetect_both_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-detect finds both manifests and their versions agree."""
    monkeypatch.chdir(TOML_DIR / "autodetect_both_match")
    resolved = vercheck.resolve_toml_sources([vercheck.AUTO_DETECT])
    assert dict(resolved) == {"pyproject.toml": "0.1.0", "Cargo.toml": "0.1.0"}


def test_resolve_toml_sources_repeated_bare_toml(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repeating bare --toml still auto-detects, it is not "combined with explicit"."""
    monkeypatch.chdir(TOML_DIR / "autodetect_single")
    resolved = vercheck.resolve_toml_sources(
        [vercheck.AUTO_DETECT, vercheck.AUTO_DETECT],
    )
    assert resolved == [("pyproject.toml", "0.1.0")]


def test_resolve_toml_sources_autodetect_combined_with_explicit() -> None:
    """Combining bare --toml with an explicit --toml=file is an error."""
    with pytest.raises(SystemExit) as excinfo:
        vercheck.resolve_toml_sources([vercheck.AUTO_DETECT, "Cargo.toml"])
    assert excinfo.value.code == 1


def test_resolve_toml_sources_explicit_multiple() -> None:
    """Explicit mode resolves every given file."""
    resolved = vercheck.resolve_toml_sources(
        [str(TOML_DIR / "pyproject.toml"), str(TOML_DIR / "Cargo.toml")],
    )
    assert dict(resolved) == {
        str(TOML_DIR / "pyproject.toml"): "0.1.0",
        str(TOML_DIR / "Cargo.toml"): "0.1.0",
    }


def test_check_multiple_toml_sources_must_agree(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    """Multiple TOML sources are all checked and mismatches fail."""
    mismatched_file = tmp_path / "mismatch.toml"
    mismatched_file.write_text("version = '0.2.0'\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "vercheck",
            "0.1.0",
            f"--toml={TOML_DIR / 'pyproject.toml'}",
            f"--toml={mismatched_file}",
        ],
    )
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert excinfo.value.code == 1


# -- check_versions ----------------------------------------------------------


def test_check_versions_all_compliant_and_matching() -> None:
    """No errors when everything is compliant and matches."""
    assert vercheck.check_versions([("a", "0.1.0"), ("b", "0.1.0")]) == []


def test_check_versions_non_compliant() -> None:
    """An error is reported for each non-compliant version."""
    errors = vercheck.check_versions([("a", "not-a-version")])
    assert len(errors) == 1
    assert "not-a-version" in errors[0]


def test_check_versions_mismatch() -> None:
    """A single mismatch error lists every source and its version."""
    errors = vercheck.check_versions([("a", "0.1.0"), ("b", "0.2.0")])
    assert len(errors) == 1
    assert "a: 0.1.0" in errors[0]
    assert "b: 0.2.0" in errors[0]


def test_check_versions_non_compliant_and_mismatch() -> None:
    """Both a compliance error and a mismatch error can occur together."""
    errors = vercheck.check_versions([("a", "not-a-version"), ("b", "0.2.0")])
    assert len(errors) == 2


# -- check --------------------------------------------------------------------


def test_check_version_only_succeeds() -> None:
    """A compliant literal version with no source succeeds."""
    assert vercheck.check("0.1.0", None, None) == 0


def test_check_version_only_fails() -> None:
    """A non-compliant literal version with no source fails."""
    assert vercheck.check("0.1.0a", None, None) == 1


def test_check_nothing_given_fails() -> None:
    """Nothing to check is an error."""
    assert vercheck.check(None, None, None) == 1


def test_check_toml_and_py_mutually_exclusive() -> None:
    """--toml and --py cannot both be given."""
    assert vercheck.check(None, [str(TOML_DIR / "pyproject.toml")], "some/file.py") == 1


def test_check_toml_only_succeeds() -> None:
    """--toml with no literal version checks the toml's own compliance."""
    assert vercheck.check(None, [str(TOML_DIR / "pyproject.toml")], None) == 0


def test_check_py_only_succeeds() -> None:
    """--py with no literal version checks the module's own compliance."""
    assert vercheck.check(None, None, str(DATA_DIR / "about.py")) == 0


def test_check_version_matches_toml() -> None:
    """A literal version matching the toml source succeeds."""
    assert vercheck.check("0.1.0", [str(TOML_DIR / "pyproject.toml")], None) == 0


def test_check_version_mismatches_toml() -> None:
    """A literal version disagreeing with the toml source fails."""
    assert vercheck.check("0.2.0", [str(TOML_DIR / "pyproject.toml")], None) == 1


def test_check_version_matches_py() -> None:
    """A literal version matching the py source succeeds."""
    assert vercheck.check("0.1.0a1", None, str(DATA_DIR / "about.py")) == 0


def test_check_version_mismatches_py() -> None:
    """A literal version disagreeing with the py source fails."""
    assert vercheck.check("0.1.0", None, str(DATA_DIR / "about.py")) == 1


# -- main ---------------------------------------------------------------------


def test_main_with_no_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bare invocation with nothing to check exits with code 1."""
    monkeypatch.setattr("sys.argv", ["vercheck"])
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert excinfo.value.code == 1


def test_main_with_compliant_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """A compliant version on the CLI exits with code 0."""
    monkeypatch.setattr("sys.argv", ["vercheck", "0.1.0"])
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert excinfo.value.code == 0


def test_main_with_toml(monkeypatch: pytest.MonkeyPatch) -> None:
    """--toml=file is parsed and checked end-to-end."""
    monkeypatch.setattr(
        "sys.argv",
        ["vercheck", "0.1.0", f"--toml={TOML_DIR / 'pyproject.toml'}"],
    )
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert excinfo.value.code == 0


def test_main_with_py(monkeypatch: pytest.MonkeyPatch) -> None:
    """--py=file is parsed and checked end-to-end."""
    monkeypatch.setattr(
        "sys.argv",
        ["vercheck", "0.1.0a1", f"--py={DATA_DIR / 'about.py'}"],
    )
    with pytest.raises(SystemExit) as excinfo:
        vercheck.main()
    assert excinfo.value.code == 0
