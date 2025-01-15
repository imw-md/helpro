"""Data for MOLPRO."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class MethodProperties:
    """Method properties."""

    name: str
    is_df: bool = False
    is_f12: bool = False
    is_ks: bool = False
    is_pno: bool = False
    is_rpa: bool = False
    is_unrestricted: bool = False


def _make_methods_basic() -> dict[str, MethodProperties]:
    """Make basic methods.

    Returns
    -------
    dict[str, MethodProperties]
        Basic methods.

    """
    methods = {}

    names_hf = ("HF",)
    names_ps = (
        "MP2",
        "CCSD",
        "CCSD_T",
    )
    kwargs = {}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names_hf + names_ps})

    names = tuple(f"DF-{_}" for _ in names_hf + names_ps)
    kwargs = {"is_df": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-{_}-F12" for _ in names_ps)
    kwargs = {"is_df": True, "is_f12": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-PNO-L{_}" for _ in names_ps)
    kwargs = {"is_df": True, "is_pno": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-PNO-L{_}-F12" for _ in names_ps)
    kwargs = {"is_df": True, "is_f12": True, "is_pno": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    return methods


def _make_methods_dft() -> dict[str, MethodProperties]:
    """Make DFT methods.

    https://www.molpro.net/manual/doku.php?id=the_density_functional_program

    Returns
    -------
    dict[str, MethodProperties]
        DFT methods.

    """
    methods = {}

    names_basic = (
        "KS_LDA",
        "KS_PBE",
        "KS_PBE-D2",
        "KS_PBE-D3",
        "KS_PBE-D3_BJ",
        "KS_PBE-D4",
    )
    kwargs = {"is_ks": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names_basic})

    names_r = tuple(f"R{_}" for _ in names_basic)
    kwargs = {"is_ks": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names_r})

    names_u = tuple(f"U{_}" for _ in names_basic)
    kwargs = {"is_ks": True, "is_unrestricted": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names_u})

    names_df = tuple(f"DF-{_}" for _ in names_basic + names_r)
    kwargs = {"is_df": True, "is_ks": True, "is_unrestricted": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names_df})

    return methods


def _make_methods_rpa() -> dict[str, MethodProperties]:
    """Make RPA methods.

    https://www.molpro.net/manual/doku.php?id=kohn-sham_random-phase_approximation

    Returns
    -------
    dict[str, MethodProperties]
        RPA methods.

    """
    methods = {}

    names = (
        "KSRPA_DIRPA",
        "KSRPA_RPAX2",
        # "KSRPA_ACFDT",
        # "KSRPA_RIRPA",  # equivalent to ACFD_RIRPA
        "ACFD_RIRPA",
        # "RPATDDFT",
    )
    kwargs = {"is_ks": True, "is_rpa": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = (
        "KSRPA_URPAX2",
        "ACFD_URIRPA",
    )
    kwargs = {"is_ks": True, "is_rpa": True, "is_unrestricted": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    return methods


def _get_methods_all() -> dict[str, MethodProperties]:
    """Get methods."""
    return _make_methods_basic() | _make_methods_dft() | _make_methods_rpa()


methods_all = _get_methods_all()

all_bases = (
    "cc-pVDZ",
    "cc-pVTZ",
    "cc-pVQZ",
    "cc-pV5Z",
    "cc-pV6Z",
    "heavy-aug-cc-pVDZ",
    "heavy-aug-cc-pVTZ",
    "heavy-aug-cc-pVQZ",
    "heavy-aug-cc-pV5Z",
    "heavy-aug-cc-pV6Z",
    "aug-cc-pVDZ",
    "aug-cc-pVTZ",
    "aug-cc-pVQZ",
    "aug-cc-pV5Z",
    "aug-cc-pV6Z",
)
