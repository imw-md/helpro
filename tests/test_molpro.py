"""Tests for `molpro.py`."""

from pathlib import Path

from helpro.molpro.inp import write


def test_molpro(tmp_path: Path) -> None:
    """Test."""
    p = Path(__file__).parent / "molpro.inp.ref"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    write(method="DF-HF", basis="cc-pVDZ", fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref
