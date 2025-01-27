"""Tests for `molpro.py`."""

import os
from pathlib import Path

import pytest

from helpro.molpro.inp import write_molpro_inp


def get_parameters_basic() -> list[list[str]]:
    """Get parameters."""
    p = Path(__file__).parent / "data" / "basic"
    parameters = []
    for root, _, files in os.walk(p):
        if "molpro.inp" in files:
            parameters.append(Path(root).parts[-3:])
    return sorted(parameters)


@pytest.mark.parametrize(("method", "basis", "core"), get_parameters_basic())
def test_basic(*, method: str, basis: str, core: str, tmp_path: Path) -> None:
    """Test basic input files."""
    p = Path(__file__).parent / "data" / "basic"
    p = p / method / basis / core / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    write_molpro_inp(method=method, basis=basis, core=core, fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


def get_parameters_charge_and_spin() -> list[list[str]]:
    """Get parameters."""
    p = Path(__file__).parent / "data" / "charge_and_spin"
    parameters = []
    for root, _, files in os.walk(p):
        if "molpro.inp" in files:
            parameters.append(Path(root).parts[-3:])
    return sorted(parameters)


@pytest.mark.parametrize(("method", "basis", "core"), get_parameters_charge_and_spin())
def test_charge_and_spin(*, method: str, basis: str, core: str, tmp_path: Path) -> None:
    """Test CHARGE and SPIN."""
    p = Path(__file__).parent / "data" / "charge_and_spin"
    p = p / method / basis / core / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    write_molpro_inp(method=method, basis=basis, core=core, charge=0, spin=1, fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


def test_options(tmp_path: Path) -> None:
    """Test if options can be provided."""
    lines = (
        r"GPRINT,ORBITALS",
        r"NOSYM",
        r"ANGSTROM",
        r"GEOMETRY=initial.xyz",
        r"BASIS=cc-pVDZ",
        r"{HF}",
        r"COUNTERPOISE",
    )
    sref = "".join(f"{_}\n" for _ in lines)

    p = tmp_path / "molpro.inp"
    write_molpro_inp(method="HF", basis="cc-pVDZ", options="COUNTERPOISE", fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref
