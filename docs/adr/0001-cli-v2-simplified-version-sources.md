# CLI v2: replace positional filename with `--toml`/`--py` version sources, drop egg-info support, bump Python floor to 3.11+

**Status**: accepted

The original CLI took a required `version` positional plus an optional positional `filename` that vercheck sniffed (`.py` → `__version__`, anything else → `*.egg-info/PKG-INFO`'s `Version:` line) to decide how to read a comparison version.
This guessing was confusing and PKG-INFO/egg-info is a build artifact, not a source of truth developers actually edit.

We replaced it with explicit, mutually exclusive `--toml`/`--py` flags, made the `version` positional itself optional (its absence now means "just check the resolved source for PEP-440 compliance," replacing the separate `--check-version-number-only` flag), and dropped egg-info/PKG-INFO reading entirely.

`--toml` also gained auto-detection (bare `--toml` checks whichever of `pyproject.toml`/`Cargo.toml` exist in the cwd, requiring them to agree) and an explicit `file:dotted.key.path` form for non-default manifests (e.g. Poetry's `tool.poetry.version`).
It intentionally never resolves setuptools' `dynamic`/`attr` indirection — that's what `--py` is for — to keep `--toml` a pure "read a literal string at a key path" operation.

Reading TOML for real (not just the previously-unsupported case) requires a real parser for both `pyproject.toml` and `Cargo.toml`.
`tomllib` is stdlib only from Python 3.11+; adding `tomli` as a runtime dependency would break the tool's "no dependencies outside the standard library" property.
We chose to bump the minimum supported Python to 3.11+ rather than take the dependency, since this is a CLI tool (not a library people pin transitively) and 3.10 support was the more reversible cost.

This is a breaking change to the CLI surface and warrants a major version bump.

## Considered Options

- Auto-resolve setuptools `dynamic`/`attr` inside `--toml` — rejected to keep `--toml` free of Python-import side effects; users on dynamic setuptools versioning use `--py` directly.
- Add `tomli` as a runtime dependency to keep Python 3.10 support — rejected in favor of preserving the zero-dependency property.
