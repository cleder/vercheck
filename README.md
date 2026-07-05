# Vercheck

Check whether a version string is PEP 440 compliant and optionally compare it with a version declared in a TOML manifest or a Python module's `__version__` attribute.

[![PyPI](https://img.shields.io/pypi/v/vercheck.svg)][pypi status] [![Status](https://img.shields.io/pypi/status/vercheck.svg)][pypi status] [![Python Version](https://img.shields.io/pypi/pyversions/vercheck)][pypi status] [![License](https://img.shields.io/pypi/l/vercheck)][license]

[![Read the documentation at https://vercheck.readthedocs.io/](https://img.shields.io/readthedocs/vercheck/latest.svg?label=Read%20the%20Docs)][read the docs] [![Tests](https://github.com/cleder/vercheck/workflows/Tests/badge.svg?branch=main)][tests] [![Codecov](https://codecov.io/gh/cleder/vercheck/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit] [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/vercheck/
[read the docs]: https://vercheck.readthedocs.io/
[tests]: https://github.com/cleder/vercheck/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/cleder/vercheck
[pre-commit]: https://github.com/pre-commit/pre-commit
[prek]: https://github.com/j178/prek
[black]: https://github.com/psf/black

## Requirements

- Python 3.11+
- No runtime dependencies outside the standard library

## Installation

Install the CLI with uv:

```bash
uv tool install vercheck
```

Or run it directly without installing:

```bash
uvx vercheck --help
```

## CI

Use Vercheck in CI to validate release tags or package versions before publishing:

```yaml
jobs:
  release-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uvx vercheck "$GITHUB_REF_NAME" --py=src/mypkg/about.py
```

For TOML-based checks:

```yaml
jobs:
  release-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uvx vercheck "$GITHUB_REF_NAME" --toml=pyproject.toml
```

## Pre-commit

Vercheck works as a [pre-commit]/[prek] hook.

```yaml
repos:
  - repo: https://github.com/cleder/vercheck
    rev: v0.4.0
    hooks:
      - id: vercheck
      - id: vercheck-py
        args: [--py=src/mypkg/about.py]
```

## Command-line usage

```bash
uvx vercheck 0.2.0
uvx vercheck 0.2.0 --toml
uvx vercheck 0.2.0 --py=src/mypkg/about.py
```

Use `--toml` to compare against a TOML manifest, `--py` to compare against a module's `__version__` attribute, and omit the version argument to validate the declared version in place.

You can pass multiple `--toml` entries when you want to validate more than one manifest at once.
All resolved versions must agree, which is useful for Maturin-style setups that keep the version in both `pyproject.toml` and `Cargo.toml`.

If the version is not under the built-in `project.version` (for `pyproject.toml`) or `package.version` (`Cargo.toml`) default, pass an explicit TOML key path.

```bash
uvx vercheck 0.2.0 --toml=pyproject.toml:tool.poetry.version
uvx vercheck 0.2.0 --toml=some.toml:custom.nested.key
```

> Put the version argument before `--toml` or `--py`.

## Why use it

Version strings are easy to get wrong.
Vercheck helps you confirm that:

- a release tag matches a valid PEP 440 version string;
- a package version in a manifest matches the version you intend to ship; and
- a module-level `__version__` stays consistent with your release.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license].

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

## Related

[dynamic-versioning](https://pypi.org/project/dynamic-versioning/)

[pypi]: https://pypi.org/
[file an issue]: https://github.com/cleder/vercheck/issues

<!-- github-only -->

[license]: https://github.com/cleder/vercheck/blob/main/LICENSE
[contributor guide]: https://github.com/cleder/vercheck/blob/main/CONTRIBUTING.md
