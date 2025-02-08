#!/usr/bin/env python
"""Run S66x8."""

import shutil
from itertools import product
from pathlib import Path

import numpy as np

from helpro.molpro.inp import MolproInputWriter
from helpro.utils import cd

home = Path.home()
cwd = Path.cwd()
parent = home / "codes/refdata/20_s66x8"


def run_dimers(miw: MolproInputWriter) -> None:
    """Run dimers."""
    structures = np.loadtxt(cwd / "structures.dat", dtype=str, usecols=0, ndmin=1)
    for structure in structures:
        print(structure)
        for dimer in [0.90, 0.95, 1.00, 1.05, 1.10, 1.25, 1.50, 2.00]:
            directory = Path(structure, f"{dimer:.2f}")
            directory.mkdir(parents=True, exist_ok=True)
            with cd(directory):
                xyz = parent / f"{structure}_{dimer:.2f}.xyz"
                shutil.copy2(xyz, "initial.xyz")
                miw.write()


def main() -> None:
    """Run main."""
    methods = np.loadtxt(cwd / "methods.dat", dtype=str, usecols=0, ndmin=1)
    bases = np.loadtxt(cwd / "bases.dat", dtype=str, usecols=0, ndmin=1)
    cores = ["frozen", "active"]
    for method, basis, core in product(methods, bases, cores):
        print(method, basis, core)
        miw = MolproInputWriter(method, basis, core=core)
        directory = Path(method, basis, core)
        directory.mkdir(parents=True, exist_ok=True)
        with cd(directory):
            run_dimers(miw)


if __name__ == "__main__":
    main()
