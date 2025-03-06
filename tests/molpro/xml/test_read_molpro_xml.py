"""Tests for `read_molpro_xml`."""

import os
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import pytest
from ase.units import Angstrom, Bohr, Hartree, eV

from helpro.molpro.xml import read_molpro_xml


def test_platform() -> None:
    """Test if `platform` is parsed correctly."""
    method = "DF-MP2"
    system = "Water-Water_1"
    fn = Path(__file__).parent / "data" / system / method / "molpro.xml"
    atoms = read_molpro_xml(fn)
    assert atoms.calc.results["processes"] == 12


def get_parameters_basic(structure: str) -> list[list[str]]:
    """Get parameters."""
    p = Path(__file__).parent / "data" / structure
    parameters = []
    for root, _, files in os.walk(p):
        if "molpro.xml" in files:
            parameters.append(Path(root).parts[-1])
    return sorted(parameters)


class TestsWater:
    """Tests for `Water-Water_1`."""

    @staticmethod
    def _get_refs(method: str) -> tuple[float, ...]:
        return {
            "CCSD_T": (
                -76.2738281304373,
                -0.232746633307032,
            ),
            "DF-KS_PBE": (-76.3591250339732,),
            "DF-MP2": (
                -76.2608078151049,
                -0.219746705130553,
            ),
            "DF-CCSD": (
                -76.2686874681885,
                -0.227626358214198,
            ),
            "DF-CCSD-F12": (
                -76.3235854631977,
                -0.282524353223479,
            ),
            "DF-CCSD_T": (
                -76.2739350470931,
                -0.232873937118761,
            ),
            "DF-CCSD_T-F12": (
                -76.3286262333435,
                -0.287565123369128,
            ),
            "DF-PNO-LMP2": (
                -76.2607935062209,
                -0.219732396246618,
            ),
            "DF-PNO-LMP2-F12": (
                -76.3689942309195,
                -0.306378480967639,
                -76.2823481461985,
            ),
            "DF-PNO-LCCSD": (
                -76.2686742568277,
                -0.227613146853307,
                -76.260793506221,
            ),
            "DF-PNO-LCCSD-F12": (
                -76.3603489497084,
                -0.297733199756563,
                -76.260793506221,
                -76.3689976223071,
            ),
            "DF-PNO-LCCSD_T": (
                -76.2739260170044,
                -0.232864907029982,
                -76.260793506221,
            ),
            "DF-PNO-LCCSD_T-F12": (
                -76.3653940549515,
                -0.302778304999722,
                -76.2607935062209,
                -76.368997622307,
            ),
        }[method]

    @pytest.mark.parametrize("method", get_parameters_basic("Water-Water_1"))
    def test_energies(self, *, method: str) -> None:
        """Test energies."""
        p = Path(__file__).parent / "data" / "Water-Water_1"
        p = p / method / "molpro.xml"
        atoms = read_molpro_xml(p)
        refs = self._get_refs(method)
        results = atoms.calc.results
        keys = ["energy", "correlation_energy", "MP2_energy", "MP2_F12_energy"]
        for key, ref in zip(keys, refs, strict=False):
            assert results[key] * eV / Hartree == pytest.approx(ref)


class TestsC:
    """Tests for `C`."""

    @staticmethod
    def _get_refs(method: str) -> tuple[float, ...]:
        return {
            "CCSD": (
                -37.7593427129361,
                -0.769248314921504e-01,
                -37.7379271468167,
            ),
            "CCSD_T": (
                -37.7603176507539,
                -0.77899769309984e-01,
                -37.7379271468167,
            ),
            "DF-MP2": (
                -37.7379170481495,
                -0.555016934374422e-01,
            ),
            "DF-CCSD": (
                -37.759342716162,
                -0.769248348469655e-01,
                -37.7379270491357,
            ),
            "DF-CCSD_T": (
                -37.7016756252012,
                -0.105689438899101,
                -37.6615986284225,
            ),
            "DF-PNO-LCCSD": (
                -37.7589279344133,
                -0.76512579701223e-01,
                -37.737819142599,
            ),
            "DF-PNO-LCCSD_T": (
                -37.7598961158975,
                -0.774807611854162e-01,
                -37.737819142599,
            ),
        }[method]

    @pytest.mark.parametrize("method", get_parameters_basic("C"))
    def test_energies(self, *, method: str) -> None:
        """Test energies."""
        p = Path(__file__).parent / "data" / "C"
        p = p / method / "molpro.xml"
        atoms = read_molpro_xml(p)
        refs = self._get_refs(method)
        results = atoms.calc.results
        keys = ["energy", "correlation_energy", "MP2_energy", "MP2_F12_energy"]
        for key, ref in zip(keys, refs, strict=False):
            assert results[key] * eV / Hartree == pytest.approx(ref)


def test_forces() -> None:
    """Test if the forces on atoms are parsed correctly."""
    fn = Path(__file__).parent / "data" / "forces" / "molpro.xml"
    atoms = read_molpro_xml(fn)
    gradients_ref = [
        [+0.006814611240, +0.011829455389, -0.000000000101],
        [-0.006814633022, +0.011829463841, -0.000000000023],
        [+0.013665646787, -0.000000029613, +0.000000000082],
        [-0.013665640575, -0.000000008761, -0.000000000114],
        [+0.006814589983, -0.011829452676, +0.000000000051],
        [-0.006814571165, -0.011829453103, +0.000000000105],
        [+0.004988405676, +0.008638615291, -0.000000000020],
        [-0.004988410648, +0.008638610660, -0.000000000001],
        [+0.009969982562, -0.000000010202, +0.000000000025],
        [-0.009969980116, -0.000000004827, +0.000000000009],
        [+0.004988385334, -0.008638592962, -0.000000000005],
        [-0.004988386055, -0.008638593036, -0.000000000008],
    ]
    gradients = atoms.get_forces() * -1.0 * (Bohr / Angstrom) / (Hartree / eV)
    np.testing.assert_allclose(gradients, gradients_ref)


def test_counterpoise() -> None:
    """Test if the counterpoise correction is parsed correctly."""
    fn = Path(__file__).parent / "data" / "counterpoise" / "molpro.xml"
    images = read_molpro_xml(fn, index=":")
    ead = -76.260807815105
    ebd = -76.2607977406707
    eag = -76.2611840871637
    ebg = -76.2616453576753
    ref = (ead - eag) + (ebd - ebg)
    assert ref == pytest.approx(0.00122389)
    assert images[-1].calc.results["CP_correction"] * eV / Hartree == pytest.approx(ref)

    # Test if the energy is corectly updated in the `COUNTERPOISE` jobstep.
    assert images[-1].get_potential_energy() != images[-2].get_potential_energy()


def test_dummy() -> None:
    """Test if ghost atoms are replaced with `X` correctly."""
    fn = Path(__file__).parent / "data" / "ghost" / "molpro.xml"
    atoms = read_molpro_xml(fn)
    symbols_ref = ["C", "H"] * 6 + ["X"] * 12
    assert atoms.get_chemical_symbols() == symbols_ref
