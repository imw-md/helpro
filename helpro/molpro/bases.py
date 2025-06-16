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
    for suffix in ["", "-F12"]:
        for prefix in ["", "aug-", "heavy-aug-"]:
            bases.extend([f"{prefix}cc-pV{c}Z{suffix}" for c in cardinals])
    for suffix in [""]:
        for prefix in ["", "aug-", "heavy-aug-"]:
            bases.extend([f"{prefix}cc-pwCV{c}Z{suffix}" for c in cardinals])
    for suffix in ["-F12"]:
        for prefix in [""]:
            bases.extend([f"{prefix}cc-pwCV{c}Z{suffix}" for c in cardinals])
    return bases


bases_all = make_basis_sets()
