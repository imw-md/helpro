"""Tests for `molpro.py`."""

from pathlib import Path

import pytest

from helpro.molpro.inp import write


@pytest.mark.parametrize(("method", "basis"), [("DF-HF", "cc-pVDZ")])
def test_inp(method: str, basis: str, tmp_path: Path) -> None:
    """Test."""
    p = Path(__file__).parent / "data" / method / basis / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    write(method=method, basis=basis, fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref
