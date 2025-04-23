#!/usr/bin/env python
"""Run atoms."""

from contextlib import chdir
from itertools import product
from pathlib import Path

import numpy as np
from ase import Atoms

from helpro.molpro.inp import MolproInputWriter


def run(miw: MolproInputWriter, number: int) -> None:
    """Run."""
    charges = [0, 1, -1]
    multiplicities = [1, 2, 3, 4, 5]
    for charge, multiplicity in product(charges, multiplicities):
        if (number + charge) % 2 == multiplicity % 2:
            continue
        print(charge, multiplicity)
        miw.charge = charge
        miw.multiplicity = multiplicity
        directory = Path(f"c{charge:+1d}", f"m{multiplicity:+1d}")
        directory.mkdir(parents=True, exist_ok=True)
        with chdir(directory):
            # molpro does not recognize ASE extented xyz
            atoms = Atoms([number])
            atoms.write("initial.xyz", format="xyz")
            miw.write()


def main() -> None:
    """Run main."""
    numbers = [1, 6, 7, 8]  # H, C, N, O
    methods = np.loadtxt("methods.dat", dtype=str, usecols=0, ndmin=1)
    bases = np.loadtxt("bases.dat", dtype=str, usecols=0, ndmin=1)
    cores = ["frozen", "active"]
    for number, method, basis, core in product(numbers, methods, bases, cores):
        print(number, method, basis, core)
        miw = MolproInputWriter(method, basis, core=core)
        directory = Path(str(number), method, basis, core)
        directory.mkdir(parents=True, exist_ok=True)
        with chdir(directory):
            run(miw, number)


if __name__ == "__main__":
    main()
