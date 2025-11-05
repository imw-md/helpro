"""Tests for `read_molpro_out`."""

import os
from pathlib import Path

import pytest
from ase.units import Angstrom, Bohr, Hartree, eV

from helpro.molpro.out import read_molpro_out


def get_parameters_basic(structure: str) -> list[list[str]]:
    """Get parameters.

    Returns
    -------
    parameters : list[list[str]]

    """
    p = Path(__file__).parent / "data" / structure
    parameters = []
    for root, _, files in os.walk(p):
        if "molpro.out" in files:
            parameters.append(Path(root).parts[-1])
    return sorted(parameters)


class TestsWater:
    """Tests for `Water-Water_1`."""

    @staticmethod
    def _get_refs(method: str) -> tuple[float, ...]:
        return {
            "DF-KS_PBE": (-76.359125033973,),
        }[method]

    @staticmethod
    def _get_geometry_refs(method: str) -> tuple[float, ...]:
        return {
            "DF-KS_PBE": (-1.326958228,),
        }[method]

    @pytest.mark.parametrize("method", get_parameters_basic("Water-Water_1"))
    def test_energies(self, *, method: str) -> None:
        """Test energies."""
        p = Path(__file__).parent / "data" / "Water-Water_1"
        p = p / method / "molpro.out"
        atoms = read_molpro_out(p)
        refs = self._get_refs(method)
        results = atoms.calc.results
        keys = ["energy", "correlation_energy", "MP2_energy", "MP2_F12_energy"]
        for key, ref in zip(keys, refs, strict=False):
            assert results[key] * eV / Hartree == pytest.approx(ref)

    @pytest.mark.parametrize("method", get_parameters_basic("Water-Water_1"))
    def test_geometry(self, *, method: str) -> None:
        """Test geometry."""
        p = Path(__file__).parent / "data" / "Water-Water_1"
        p = p / method / "molpro.out"
        atoms = read_molpro_out(p)
        refs = self._get_geometry_refs(method)
        assert atoms.positions[0, 0] * Angstrom / Bohr == pytest.approx(refs[0])
