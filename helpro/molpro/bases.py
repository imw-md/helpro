"""Basis sets for MOLPRO."""


def make_basis_sets() -> list[str]:
    """Make basis sets.

    Returns
    -------
    list[str]
        Names of the basis sets.

    """
    bases = []
    cardinals = ["D", "T", "Q", "5", "6"]
    bases.extend([f"cc-pV{c}Z" for c in cardinals])
    bases.extend([f"heavy-aug-cc-pV{c}Z" for c in cardinals])
    bases.extend([f"aug-cc-pV{c}Z" for c in cardinals])
    return bases


bases_all = make_basis_sets()
