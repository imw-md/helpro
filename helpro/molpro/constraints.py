"""Module for constraints."""

import numpy as np
from ase import Atoms
from ase.constraints import FixAtoms, FixCartesian


def convert_constraints_ase2molpro(atoms: Atoms, fmt: str = "") -> str:
    """Convert ASE `FixConstraint` objects to the constraint string in MOLORO OPTG.

    https://www.molpro.net/manual/doku.php?id=geometry_optimization_optg#defining_constraints

    Returns
    -------
    str
        Constraint string in MOLPRO OPTG.

    """
    lines = []
    for constr in atoms.constraints:
        if isinstance(constr, FixAtoms | FixCartesian):
            if isinstance(constr, FixAtoms):
                mask = range(3)
            elif isinstance(constr, FixCartesian):
                mask = np.where(constr.mask)[0]
            for i in constr.index:
                for j in mask:
                    value = atoms.positions[i, j]
                    tmp = (
                        "CONSTRAINT",
                        f"{value:{fmt}}",
                        "ANGSTROM",
                        "CARTESIAN",
                        f"{j + 1}",
                        f"{i + 1}",
                    )
                    lines.append(",".join(tmp))
    return "\n".join(lines)
