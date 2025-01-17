"""Tests for `molpro.py`."""

import os
from pathlib import Path

import pytest

from helpro.molpro.inp import write_molpro_inp


def get_parameters() -> list[list[str]]:
    """Get parameters."""
    p = Path(__file__).parent / "data"
    parameters = []
    for root, _, files in os.walk(p):
        if "molpro.inp" in files:
            parameters.append(Path(root).parts[-3:])
    return sorted(parameters)


@pytest.mark.parametrize(("method", "basis", "core"), get_parameters())
def test_inp(*, method: str, basis: str, core: str, tmp_path: Path) -> None:
    """Test."""
    p = Path(__file__).parent / "data" / method / basis / core / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    write_molpro_inp(method=method, basis=basis, core=core, fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref
