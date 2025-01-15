"""Tests for `molpro.py`."""

from pathlib import Path

import pytest

from helpro.molpro.inp import write


@pytest.mark.parametrize(
    ("method", "basis", "core"),
    [
        ("DF-HF", "cc-pVDZ", False),
        ("DF-UHF", "cc-pVDZ", False),
        ("DF-MP2", "cc-pVDZ", False),
        ("DF-MP2", "cc-pVDZ", True),
        ("KSRPA_DIRPA", "cc-pVDZ", False),
    ],
)
def test_inp(*, method: str, basis: str, core: bool, tmp_path: Path) -> None:
    """Test."""
    str_core = "active" if core else "frozen"
    p = Path(__file__).parent / "data" / method / basis / str_core / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    write(method=method, basis=basis, core=core, fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref
