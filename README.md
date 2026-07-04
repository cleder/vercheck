# Vercheck

Check if a version number is PEP-440 compliant and optionally compare it against a version declared in a TOML manifest (`pyproject.toml`, `Cargo.toml`, or any other `file:key.path`) or a Python module's `__version__` attribute.


[![PyPI](https://img.shields.io/pypi/v/vercheck.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/vercheck.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/vercheck)][pypi status]
[![License](https://img.shields.io/pypi/l/vercheck)][license]

[![Read the documentation at https://vercheck.readthedocs.io/](https://img.shields.io/readthedocs/vercheck/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/cleder/vercheck/workflows/Tests/badge.svg?branch=main)][tests]
[![Codecov](https://codecov.io/gh/cleder/vercheck/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/vercheck/
[read the docs]: https://vercheck.readthedocs.io/
[tests]: https://github.com/cleder/vercheck/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/cleder/vercheck
[pre-commit]: https://github.com/pre-commit/pre-commit
[prek]: https://github.com/j178/prek
[black]: https://github.com/psf/black

## Rationale

When you use a Python package, you may want to check a package's [version](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#version).
To check the Python package/library, a `__version__` attribute is a common practice recommended by [PEP 396](https://peps.python.org/pep-0396/).

```python
import package_name
print(package_name.__version__)
```

Module version numbers _SHOULD_ conform to the normalized version format specified in
[PEP 440](https://peps.python.org/pep-0440/)
The canonical public version identifiers __MUST__ comply with the following scheme:

```
[N!]N(.N)*[{a|b|rc}N][.postN][.devN]
```

Hard-coding the version of your package in the `pyproject.toml` may not be ideal, as it requires you to update it manually and if you want your package to have access to its own version, you will have to add a global variable with the version to a source package. This means you will have to manually keep those versions in sync.
A common approach is using [dynamic metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#static-vs-dynamic-metadata).

```toml
[project]
name = "mypkg"
dynamic = "version"

[tool.setuptools.dynamic.version]
attr = "mypkg.about.__version__"
```

The recommended way to implement that `__version__` attribute is to read it back from your package's own installed metadata, rather than hard-coding a second copy of the version string:

```python
from importlib.metadata import version

__version__ = version("mypkg")
```

This way there is exactly one source of truth — whatever your build backend wrote into `pyproject.toml` at build time — and `vercheck 0.2.0 --py=src/mypkg/about.py` still works unchanged, since `--py` only cares that the module exposes a `__version__` string.

If you use [Poetry](https://python-poetry.org/) instead, the version lives at `tool.poetry.version` rather than `project.version`:

```toml
[tool.poetry]
name = "mypkg"
version = "0.2.0"
```

Check it with `vercheck 0.2.0 --toml=pyproject.toml:tool.poetry.version` — see the [Usage](#usage) examples below.

When you release a new version of your package, checking the version number is a good practice.
You can automate this in your CI/CD pipeline, for example, using [GitHub Actions](https://docs.github.com/en/actions).

```yaml
      - name: Check tag name
        if: >-
          github.event_name == 'push' &&
          startsWith(github.ref, 'refs/tags')
        run: |
          pip install vercheck
          vercheck $GITHUB_REF_NAME --py=src/vercheck/about.py
```

This will check that your tag name is a valid version number and that the version number in the `src/vercheck/about.py` file is the same as the tag name.

## Requirements

- Python >= 3.11, no dependencies outside of the standard library.

## Installation

You can install _Vercheck_ via [pip] from [PyPI]:

```console
$ pip install vercheck
```

## Usage

to get a quick overview of the available commands and options, you can use the `vercheck -h` command.

```console
usage: vercheck [-h] [--toml [FILE[:KEY.PATH]]] [--py FILE] [version]

Check if a version is PEP-440 compliant.

positional arguments:
  version               The version number to check. If omitted, only the
                         resolved --toml/--py source is checked for PEP-440
                         compliance.

options:
  -h, --help             show this help message and exit
  --toml [FILE[:KEY.PATH]]
                         Check the version in a TOML manifest. With no value,
                         auto-detects 'pyproject.toml'/'Cargo.toml' in the
                         current directory; if more than one is found, they
                         must agree. With a value, checks exactly that file
                         (default key path 'project.version'/'package.version',
                         or 'file:dotted.key.path' to override). Repeatable.
  --py FILE              Check the __version__ attribute of a Python module.
```

> **Order matters:** always put `version` before `--toml`/`--py` — argparse otherwise
> swallows the next token as the flag's value (e.g. `vercheck --toml 0.1.0` treats
> `0.1.0` as the TOML spec, not the version to check).

`vercheck` will exit with a non-zero exit code if any resolved version is not PEP-440 compliant, a given file/key path does not exist, or the resolved versions do not all agree.

`--toml` and `--py` are mutually exclusive.

Examples:

```bash
vercheck 0.2.0
```

Just checks that `0.2.0` is PEP-440 compliant. No comparison, no output on success.

```bash
vercheck 0.2.0 --toml
```

Checks `0.2.0` against whichever of `pyproject.toml`/`Cargo.toml` are present in the current directory (all of them, if more than one exists — they must agree with each other and with `0.2.0`).

```bash
vercheck --toml
```

Checks that the auto-detected manifest's own version is PEP-440 compliant (and that multiple manifests, if present, agree with each other) — no literal version to compare against.

```bash
vercheck 0.2.0 --toml=Cargo.toml
```

Checks `0.2.0` against exactly `Cargo.toml`'s `package.version`, skipping auto-detection.

```bash
vercheck 0.2.0 --toml=pyproject.toml:tool.poetry.version
```

Checks `0.2.0` against a Poetry-style `pyproject.toml`, where the version lives at `tool.poetry.version` instead of the setuptools-style `project.version` default. `--toml` never resolves setuptools `dynamic`/`attr` indirection — for that, point `--py` at the Python module directly.

```bash
vercheck 0.2.0 --py=src/package/about.py
```

Checks `0.2.0` against the `__version__` attribute defined in `src/package/about.py`.

## Use as a pre-commit hook

_Vercheck_ ships a `.pre-commit-hooks.yaml` manifest, so it works as a [pre-commit] hook — and, since [prek] reads the same manifest format, as a `prek` hook too, with no extra configuration.

Two hook ids are provided, one per version source `vercheck` supports. Both run in compliance-only mode (no Target version — that comparison stays a CI concern, see [Usage](#usage) above) and both set `pass_filenames: false`, since vercheck's CLI never takes filenames from pre-commit's file list.

### `vercheck` — checks pyproject.toml / Cargo.toml

```yaml
repos:
  - repo: https://github.com/cleder/vercheck
    rev: v0.3.0 # replace with the latest tag
    hooks:
      - id: vercheck
```

Runs `vercheck --toml` whenever `pyproject.toml` or `Cargo.toml` changes, auto-detecting whichever is present and checking its version is PEP-440 compliant (agreeing with the other, if both exist).

### `vercheck-py` — checks a Python module's `__version__`

```yaml
repos:
  - repo: https://github.com/cleder/vercheck
    rev: v0.3.0 # replace with the latest tag
    hooks:
      - id: vercheck-py
        args: [--py=src/mypkg/about.py]
        files: ^src/mypkg/about\.py$
```

There's no default module path to guess, so `vercheck-py` fails until you supply `args: [--py=path/to/module.py]`. Add a `files:` override scoped to that path if you only want it to run when that file changes — otherwise it runs on every commit.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Vercheck_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Related

[dynamic-versioning](https://pypi.org/project/dynamic-versioning/)

[pypi]: https://pypi.org/
[file an issue]: https://github.com/cleder/vercheck/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/cleder/vercheck/blob/main/LICENSE
[contributor guide]: https://github.com/cleder/vercheck/blob/main/CONTRIBUTING.md
