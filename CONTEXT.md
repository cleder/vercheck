# Vercheck

A command-line tool that validates a version string is PEP-440 compliant and, optionally, that it agrees with the version declared in a project's manifest files.

## Language

**Target version**:
The version string the user is asserting is correct — passed as the optional positional CLI argument. When present, it is checked against one or more resolved sources. When absent, only the resolved source's own version is checked for compliance.
_Avoid_: tag name, version argument

**Version source**:
A place a version string is read from: a TOML manifest (`--toml`) or a Python module's `__version__` (`--py`). Exactly one kind of source may be used per invocation — `--toml` and `--py` are mutually exclusive.

**Compliance-only mode**:
Invocation with no Target version. Only checks that the resolved source's version (or, with no source at all, none — not a valid combination) is PEP-440 compliant. No cross-comparison is performed.
_Avoid_: check-version-number-only (old flag name, being retired)

**Comparison mode**:
Invocation with a Target version given. The Target version must itself be PEP-440 compliant, each resolved source version must be PEP-440 compliant, and all of them must be equal to each other.

**Auto-detect mode**:
Triggered by bare `--toml` (no value). Looks in the current directory for known manifest files (`pyproject.toml`, `Cargo.toml`) and checks whichever are present. If more than one is present, their versions must match each other (and the Target version, if given).

**Explicit mode**:
Triggered by `--toml=path` given one or more times. Checks exactly the named file(s) and performs no auto-detection. If more than one is given, their versions must match each other (and the Target version, if given).

**Key path**:
A dot-delimited address into a TOML file's table structure identifying where the version string lives, e.g. `tool.poetry.version`. Given inline in explicit mode as `file:dotted.key.path` (colon-separated from the filename). Auto-detect mode always uses the built-in default for each manifest kind — there is no way to override the key path without naming the file explicitly.
_Avoid_: attr, module attribute (that's a `--py` concept, not a `--toml` one)

**Manifest default key path**:
The key path used when no override is given: `project.version` for `pyproject.toml`, `package.version` for `Cargo.toml`. `--toml` only ever reads a literal string value at a key path — it never imports or resolves Python module attributes (that indirection is `--py`'s job).

**Mismatch report**:
The single error produced when the set of resolved versions (Target version, if given, plus every source's version) contains more than one distinct value. Lists each contributing source alongside the version it produced, rather than one error per pairwise disagreement.
