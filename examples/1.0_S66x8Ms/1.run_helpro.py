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


def run_monomers(miw: MolproInputWriter) -> None:
    """Run monomers."""
    structures = np.loadtxt(cwd / "structures.dat", dtype=str, usecols=0, ndmin=1)
    for structure in structures:
        print(structure)
        for monomer in [1, 2]:
            directory = Path(structure, f"{monomer}")
            directory.mkdir(parents=True, exist_ok=True)
            with cd(directory):
                xyz = parent / f"{structure}_{monomer}.xyz"
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
            run_monomers(miw)


if __name__ == "__main__":
    main()
