# Pre-commit hooks run in Compliance-only mode, never Comparison mode

**Status**: accepted

`.pre-commit-hooks.yaml` exposes two hook ids, `vercheck` (`--toml` auto-detect) and `vercheck-py` (`--py`, no default path), both invoked with `pass_filenames: false` since vercheck's argparse accepts only one positional and errors on any extra filenames pre-commit would otherwise pass.
Neither hook ever supplies a Target version: the only version worth comparing against at commit time is the release tag, which doesn't exist yet mid-development — that comparison remains a CI-only concern (per the existing `vercheck $TAG --py=...` CI recipe in the README).
The hooks therefore only ever check that the resolved source(s) are PEP-440 compliant and mutually agree (Compliance-only mode), catching manifest typos before they're committed.

`vercheck-py` ships with no default `--py` value, since there's no discoverable default module path across arbitrary repos; until a consumer supplies `args: [--py=path/to/module.py]`, the hook deliberately fails ("nothing to check") rather than silently no-op'ing, so misconfiguration is caught immediately rather than passing vacuously.

## Considered Options

- Let hook consumers pass a literal Target version via `args:` for comparison mode — rejected: any hardcoded version goes stale the moment the source is bumped, silently defeating the check's purpose.
- Give `vercheck-py` a fallback default (e.g. `src/<package>/__init__.py`) guessed from repo layout — rejected: no reliable convention exists across repos, and guessing wrong would silently check the wrong file, echoing the exact "guessing which file to sniff" problem ADR 0001 already removed from the CLI itself.
