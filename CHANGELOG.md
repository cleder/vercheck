# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a `.pre-commit-hooks.yaml` manifest exposing `vercheck` and
  `vercheck-py` hooks for use with `pre-commit`/`prek`.

### Changed

- Replaced the positional `filename` argument with explicit, mutually
  exclusive `--toml` and `--py` flags. `--toml` auto-detects
  `pyproject.toml`/`Cargo.toml` in the current directory when given no
  value, or reads an explicit `file[:dotted.key.path]` otherwise
  (repeatable; when more than one source resolves, all versions must
  agree). `--py` checks a Python module's `__version__` attribute.
- `version` is now an optional positional argument.
  Omitting it checks only the resolved `--toml`/`--py` source's PEP-440 compliance, with no comparison — this replaces the old `--check-version-number-only` flag.
- Raised the minimum supported Python version to 3.11, to use the
  standard library's `tomllib` for TOML parsing instead of adding a
  runtime dependency.

### Removed

- Dropped support for reading a version from a `*.egg-info/PKG-INFO` file.
  Use `--toml` (for `pyproject.toml`/`Cargo.toml`) or `--py` (for a Python module's `__version__`) instead.
- Removed the `--check-version-number-only` flag; omit the `version`
  argument for the same effect.

## [0.2.0] - 2024-10-11

### Added

- Support for checking a version against a Python module's
  `__version__` attribute.

### Changed

- Improved error handling when extracting a version from a file.

## [0.1.0] - 2024-10-09

### Added

- Initial release: check a version number for PEP-440 compliance, and
  optionally compare it against a version read from a
  `*.egg-info/PKG-INFO` file.

[unreleased]: https://github.com/cleder/vercheck/compare/0.2.0...HEAD
[0.2.0]: https://github.com/cleder/vercheck/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/cleder/vercheck/releases/tag/0.1.0
