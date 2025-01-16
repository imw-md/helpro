"""Parser for MOLPRO output."""

from pathlib import Path

import numpy as np
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.units import Angstrom, Bohr, Hartree, eV


def read_molpro_out(fd: str | Path) -> Atoms:
    """Read MOLPRO output.

    Parameters
    ----------
    fd : str
        File name or path.

    Returns
    -------
    Atoms
        ASE Atoms object.

    """
    numbers = []
    positions = []
    energy = float("nan")
    forces = None
    p = Path(fd)
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "ATOMIC COORDINATES":
                for _ in range(3):
                    next(f)
                while True:
                    line_coordinates = next(f)
                    if not line_coordinates.strip():
                        break
                    _, _, n, x, y, z = line_coordinates.split()
                    numbers.append(int(float(n)))
                    positions.append([float(x), float(y), float(z)])
            elif "energy=" in line:
                energy = float(line.split()[-1])
                energy *= Hartree / eV
            elif "dE/dx" in line:
                next(f)
                forces = []
                while True:
                    line_gradients = next(f)
                    if not line_gradients.strip():
                        break
                    forces.append([float(_) for _ in line_gradients.split()[-3:]])
                forces = np.array(forces)
                forces *= -1.0 * (Hartree / eV) / (Bohr / Angstrom)

    atoms = Atoms(numbers=numbers, positions=positions)
    atoms.calc = SinglePointCalculator(atoms, energy=energy, forces=forces)
    return atoms
