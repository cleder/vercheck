"""Nox sessions."""

import tempfile
from typing import Any

import nox
from nox.sessions import Session

package = "vercheck"
locations = ["src", "tests", "noxfile.py"]
nox.needs_version = ">= 2023.4.22"
nox.options.sessions = ["tests", "lint", "mypy", "coverage"]
python_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "uv",
            "pip",
            "compile",
            f"--output={requirements.name}",
            "--extra=dev",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "-xvs"]
    session.run("uv", "pip", "install", "-e", ".[tests]", external=True)
    session.run("pytest", *args)


@nox.session(python=["3.10"])
def lint(session: Session) -> None:
    """Lint using ruff."""
    args = session.posargs or locations
    session.run("uv", "pip", "install", "-e", ".[linting]", external=True)
    session.run("ruff", "check", *args)


@nox.session(python=["3.10"])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.run("uv", "pip", "install", "-e", ".[typing]", external=True)
    session.run("mypy", *args)


@nox.session(python=["3.10"])
def coverage(session: Session) -> None:
    """Run the test suite and check coverage."""
    session.run("uv", "pip", "install", "-e", ".[tests]", external=True)
    session.run("pytest", "--cov=src", "--cov=tests", "--cov-report=xml")
    session.run("coverage", "report", "--fail-under=100")


@nox.session(python=["3.10"])
def pre_commit(session: Session) -> None:
    """Run pre-commit hooks."""
    session.run("uv", "pip", "install", "pre-commit", external=True)
    args = session.posargs or ["run", "--all-files"]
    session.run("pre-commit", *args)


@nox.session(python=["3.10"])
def build(session: Session) -> None:
    """Build the package."""
    session.run("uv", "pip", "install", "build", "twine", external=True)
    session.run("rm", "-rf", "dist", "build", external=True)
    session.run("python", "-m", "build")
    session.run("twine", "check", "dist/*")


@nox.session(python=["3.10"])
def docs(session: Session) -> None:
    """Build the documentation."""
    session.run("uv", "pip", "install", "sphinx", "sphinx-rtd-theme", external=True)
    session.run("sphinx-build", "docs", "docs/_build")


@nox.session(python=python_versions)
def check(session: Session) -> None:
    """Check the package with vercheck."""
    session.run("uv", "pip", "install", "-e", ".", external=True)
    # Get current version from about.py
    session.run("vercheck", "0.3.0", "src/vercheck/about.py")
