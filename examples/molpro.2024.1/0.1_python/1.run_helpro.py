#!/usr/bin/env python
"""Run S66x8."""

from itertools import product
from pathlib import Path

import ase.io
import numpy as np
from ase import Atoms

from helpro.molpro.inp import MolproInputWriter
from helpro.utils import cd

home = Path.home()
cwd = Path.cwd()
parent = home / "codes/refdata/20_s66x8"


def run(miw: MolproInputWriter, images: list[Atoms]) -> None:
    """Run monomers."""
    for i in range(0, len(images), 20):
        print(i)
        directory = Path(f"{i:05d}")
        directory.mkdir(parents=True, exist_ok=True)
        with cd(directory):
            # molpro does not recognize ASE extented xyz
            ase.io.write("initial.xyz", images[i], format="xyz")
            miw.write()


def main() -> None:
    """Run main."""
    methods = np.loadtxt(cwd / "methods.dat", dtype=str, usecols=0, ndmin=1)
    bases = np.loadtxt(cwd / "bases.dat", dtype=str, usecols=0, ndmin=1)
    cores = ["frozen", "active"]
    images = ase.io.read("ase.xyz", index=":")
    for method, basis, core in product(methods, bases, cores):
        print(method, basis, core)
        miw = MolproInputWriter(method, basis, core=core)
        directory = Path(method, basis, core)
        directory.mkdir(parents=True, exist_ok=True)
        with cd(directory):
            run(miw, images)


if __name__ == "__main__":
    main()
