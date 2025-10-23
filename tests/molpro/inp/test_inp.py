"""Tests for `molpro.py`."""

import os
from pathlib import Path

import pytest

from helpro.molpro.inp import MolproInputWriter
from helpro.molpro.methods import DFTMethod


def get_parameters_basic() -> list[list[str]]:
    """Get parameters.

    Returns
    -------
    parameters : list[list[str]]

    """
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
    miw = MolproInputWriter(method=method, basis=basis, core=core)
    miw.write(fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


@pytest.mark.parametrize("xc", ["PBESOL", "R2SCAN"])
def test_xc(xc: str, tmp_path: Path) -> None:
    """Test user-specified exchange-correlation functionals."""
    name = "DF-KS"
    basis = "cc-pVDZ"
    core = "frozen"
    p = Path(__file__).parent / "data" / "xc"
    p = p / f"{name}_{xc}" / basis / core / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    method = DFTMethod(name=name, xc=xc)
    miw = MolproInputWriter(method=method, basis=basis, core=core)
    miw.write(fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


@pytest.mark.parametrize("xc", ["R2SCAN"])
def test_gridthr(xc: str, tmp_path: Path) -> None:
    """Test GRIDTHR."""
    name = "DF-KS"
    basis = "cc-pVDZ"
    core = "frozen"
    p = Path(__file__).parent / "data" / "gridthr"
    p = p / f"{name}_{xc}" / basis / core / "molpro.inp"
    with p.open("r", encoding="utf-8") as f:
        sref = f.read()

    p = tmp_path / "molpro.inp"
    method = DFTMethod(name=name, xc=xc, gridthr=1e-10)
    miw = MolproInputWriter(method=method, basis=basis, core=core)
    miw.write(fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


def test_cabs_singles(tmp_path: Path) -> None:
    """Test CABS_SINGLES."""
    lines = (
        r"GPRINT,ORBITALS",
        r"NOSYM",
        r"ANGSTROM",
        r"GEOMETRY=initial.xyz",
        r"BASIS=cc-pVDZ",
        r"{DF-HF}",
        r"{DF-MP2-F12,CABS_SINGLES=0}",
    )
    sref = "".join(f"{_}\n" for _ in lines)

    p = tmp_path / "molpro.inp"
    method_options = {"cabs_singles": 0}
    miw = MolproInputWriter(
        method="DF-MP2-F12",
        basis="cc-pVDZ",
        core="frozen",
        method_options=method_options,
    )
    miw.write(fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


def get_parameters_charge_and_spin() -> list[list[str]]:
    """Get parameters.

    Returns
    -------
    parameters : list[list[str]]

    """
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
    miw = MolproInputWriter(
        method=method,
        basis=basis,
        core=core,
        charge=0,
        multiplicity=1,
    )
    miw.write(fname=p)
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
    miw = MolproInputWriter(method="HF", basis="cc-pVDZ", options="COUNTERPOISE")
    miw.write(fname=p)
    with p.open("r", encoding="utf-8") as f:
        s = f.read()

    assert s == sref


def test_template(tmp_path: Path) -> None:
    """Test if `template` can be provided."""
    tpl = (
        r"GPRINT,ORBITALS",
        r"GCOSMO,epsilon=78.3553",
        r"NOSYM",
        r"{{geometry}}",
        r"{{basis}}",
        r"{{method}}",
    )
    path_tpl = tmp_path / "molpro.inp.j2"
    with path_tpl.open("w", encoding="utf-8") as fd:
        fd.writelines("".join(f"{_}\n" for _ in tpl))

    sref = (
        r"GPRINT,ORBITALS",
        r"GCOSMO,epsilon=78.3553",
        r"NOSYM",
        r"ANGSTROM",
        r"GEOMETRY=initial.xyz",
        r"BASIS=cc-pVDZ",
        r"{HF}",
    )
    sref = "".join(f"{_}\n" for _ in sref)

    miw = MolproInputWriter(method="HF", basis="cc-pVDZ", template=path_tpl)
    path = tmp_path / "molpro.inp"
    miw.write(fname=path)
    with path.open("r", encoding="utf-8") as f:
        s = f.read()
    assert s == sref
