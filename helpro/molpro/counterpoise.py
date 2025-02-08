"""Counterpoise."""

from pathlib import Path

import numpy as np
from ase import Atoms

from helpro.molpro.inp import MolproInputWriter
from helpro.utils import cd


def tag_multimer(multimer: Atoms, monomers: list[Atoms]) -> list[int]:
    """Tag multimer."""
    n0 = len(multimer)
    tags = np.full(n0, -1)
    n1 = 0
    for i, monomer in enumerate(monomers):
        n = len(monomer)
        tags[n1 : n1 + n] = i + 1
        n1 += n
    if n0 != n1:
        raise RuntimeError(n0, n1)
    return tags


def counterpoise(
    miw: MolproInputWriter,
    tags: list[int],
    fname: str | None = None,
) -> list[Path]:
    """Counterpoise.

    Parameters
    ----------
    miw : MolproInputWriter
        MolproInputWriter.
    tags : list[int]
        Tags based on monomers.
    fname : str, default: "molpro.inp"
        Input file name.

    Returns
    -------
    directories : list[Path]
        Directories for the counterpoise correction.

    """
    if fname is None:
        fname = "molpro.inp"

    directories = []
    for index in np.unique(tags):
        dummies = [i + 1 for i, tag in enumerate(tags) if tag != index]
        for skip in [False, True]:
            directory = f"CP{index}S" if skip else f"CP{index}G"
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            with cd(directory):
                miw.geometry.dummies = dummies
                miw.geometry.skip = skip
                miw.write(fname)
            directories.append(directory)
    return directories
