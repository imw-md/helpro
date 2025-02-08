"""Utilities."""

import contextlib
import os
import typing
from pathlib import Path


@contextlib.contextmanager
def cd(path: str | Path) -> typing.Generator:
    """Change directory temporalily.

    Parameters
    ----------
    path: Path
        Path to directory.

    """
    cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)
