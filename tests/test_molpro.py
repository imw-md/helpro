"""Tests for `molpro.py`."""

from pathlib import Path

from helpro.molpro import write


def test_molpro() -> None:
    """Test."""
    p = Path(__file__).parent / "molpro.inp.ref"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()
    write(method="DF-HF", basis="cc-pVDZ")
    p = Path("molpro.inp")
    with p.open("r", encoding="utf-8") as f:
        s = f.read()
    assert s == sref
