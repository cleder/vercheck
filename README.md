# Vercheck

Check if a version number is PEP-440 compliant and optionally compare it against a version specified in a python file or the PKG-INFO metadata file.


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

When you release a new version of your package, checking the version number is a good practice.
You can automate this in your CI/CD pipeline, for example, using [GitHub Actions](https://docs.github.com/en/actions).

```yaml
      - name: Check tag name
        if: >-
          github.event_name == 'push' &&
          startsWith(github.ref, 'refs/tags')
        run: |
          pip install vercheck
          vercheck $GITHUB_REF_NAME src/vercheck/about.py
```

This will check that your tag name is a valid version number and that the version number in the `src/vercheck/about.py` file is the same as the tag name.

## Requirements

- Python >= 3.10, no dependencies outside of the standard library.

## Installation

You can install _Vercheck_ via [pip] from [PyPI]:

```console
$ pip install vercheck
```

## Usage

to get a quick overview of the available commands and options, you can use the `vercheck -h` command.

```console
usage: vercheck [-h] [--check-version-number-only] version [filename]

Check if the version is PEP-440 conformant.

positional arguments:
  version               The version number to compare against.
  filename              The path to the file containing the version information.

options:
  -h, --help            show this help message and exit
  --check-version-number-only
                        Only check if the version number is PEP-440 compliant without trying to retrieve a version from a file.
```

`vercheck` will exit with a non-zero exit code if the version number is not PEP-440 compliant, the file path does not exist or the version number is not equal to the version number in the file.

Examples:

```bash
vercheck 0.2.0 src/vercheck/about.py
```

This will check if the version number is PEP-440 compliant and if the version number is equal to the version number in the `src/vercheck/about.py` file.
It does not provide any output if the version number is PEP-440 compliant and the version number is equal to the version number in the file. If an error is encountered, it will print the error message and exit with a non-zero exit code.

```bash
vercheck 0.2.0 --check-version-number-only
```

This will check if the version number is PEP-440 compliant without trying to retrieve a version from a file.

```bash
vercheck 0.2.0 src
```

or

```bash
vercheck 0.2.0 src/vercheck.egg-info/PKG-INFO
```

This will check if the version number is PEP-440 compliant and if the version number is equal to the version number in the `src/vercheck.egg-info/PKG-INFO` file.
The output will be:

```console
Warning: filename src does not end with '.py'
Checking version in src
Found 'src/vercheck.egg-info'
```

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
