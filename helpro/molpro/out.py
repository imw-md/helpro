"""Parser for MOLPRO output."""

from pathlib import Path

from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.units import Hartree, eV


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
    atoms = Atoms(numbers=numbers, positions=positions)
    atoms.calc = SinglePointCalculator(atoms, energy=energy)
    return atoms
