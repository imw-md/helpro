"""Data for MOLPRO."""

from dataclasses import dataclass, replace

dispersions = ("", "D2", "D3", "D3_BJ", "D4")


@dataclass(frozen=True, kw_only=True)
class Method:
    """Method properties."""

    name: str
    is_df: bool = False
    is_f12: bool = False
    is_hf: bool = False  # whether this is the HF method
    is_pno: bool = False
    is_spin_u: bool = False
    xc: str = ""
    ref: str = ""  # reference method name for post-HF and post-KS


@dataclass(frozen=True, kw_only=True)
class DFTMethod(Method):
    """DFT Method."""

    dispersion: str = ""


@dataclass(frozen=True, kw_only=True)
class RPAMethod(Method):
    """RPA Method."""

    is_acfd: bool = False


def _make_methods_hf() -> dict[str, Method]:
    """Make HF methods.

    Returns
    -------
    dict[str, Method]
        HF methods.

    """
    methods = {}

    names_basic = ("HF",)

    names = names_basic
    kwargs = {"is_hf": True}
    methods.update({k: Method(name=k, **kwargs) for k in names})

    names = tuple(f"R{_}" for _ in names_basic)
    kwargs = {"is_hf": True}
    methods.update({k: Method(name=k, **kwargs) for k in names})

    names = tuple(f"U{_}" for _ in names_basic)
    kwargs = {"is_hf": True, "is_spin_u": True}
    methods.update({k: Method(name=k, **kwargs) for k in names})

    methods_df = {}
    for k, v in methods.items():
        methods_df[f"DF-{k}"] = replace(v, name=f"DF-{k}", is_df=True)

    return methods | methods_df


def _make_methods_post_hf() -> dict[str, Method]:
    """Make post-HF methods.

    Returns
    -------
    dict[str, Method]
        Post-HF methods.

    """
    methods = {}

    names_ps = (
        "MP2",
        "CCSD",
        "CCSD_T",
    )
    kwargs = {"ref": "HF"}
    methods.update({_: Method(name=_, **kwargs) for _ in names_ps})

    names = tuple(f"DF-{_}" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True}
    methods.update({_: Method(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-{_}-F12" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True, "is_f12": True}
    methods.update({_: Method(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-PNO-L{_}" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True, "is_pno": True}
    methods.update({_: Method(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-PNO-L{_}-F12" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True, "is_f12": True, "is_pno": True}
    methods.update({_: Method(name=_, **kwargs) for _ in names})

    return methods


def _make_methods_dft() -> dict[str, DFTMethod]:
    """Make DFT methods.

    https://www.molpro.net/manual/doku.php?id=the_density_functional_program

    Returns
    -------
    dict[str, DFTMethod]
        DFT methods.

    Notes
    -----
    - `DF` is not available for `UKS`; only `CF` is availble.
    - It makes less sense to add the dispersion correction to LDA
      because LDA already has an overbinding nature.

    """
    methods = {}

    xcs = ("LDA", "PBE")
    for xc in xcs:
        for dispersion in dispersions:
            sep = "-" if dispersion else ""
            if xc == "LDA" and dispersion:
                continue
            name = f"KS_{xc}{sep}{dispersion}"
            kwargs = {"xc": xc, "dispersion": dispersion}
            methods[name] = DFTMethod(name=name, **kwargs)

            name = f"RKS_{xc}{sep}{dispersion}"
            methods[name] = DFTMethod(name=name, **kwargs)

            name = f"UKS_{xc}{sep}{dispersion}"
            kwargs.update(is_spin_u=True)
            methods[name] = DFTMethod(name=name, **kwargs)

            kwargs.update(is_df=True, is_spin_u=False)

            name = f"DF-KS_{xc}{sep}{dispersion}"
            methods[name] = DFTMethod(name=name, **kwargs)

            name = f"DF-RKS_{xc}{sep}{dispersion}"
            methods[name] = DFTMethod(name=name, **kwargs)

    return methods


def _make_methods_rpa() -> dict[str, RPAMethod]:
    """Make RPA methods.

    https://www.molpro.net/manual/doku.php?id=kohn-sham_random-phase_approximation

    Returns
    -------
    dict[str, RPAMethod]
        RPA methods.

    Notes
    -----
    - `KSRPA_ACFDT` does not work well with the present MOLPRO.
    - `RPATDDFT` does not work with `DF-KS`.
    - `KSRPA_RIRPA` is equivalent to `ACFD_RIRPA`.

    """
    methods = {}

    xcs = ("", "LDA", "PBE")  # "" is for the HF method.
    for xc in xcs:
        # KSRPA
        names = (
            "DIRPA",
            "RPAX2",
            # "ACFDT",
        )
        ref = f"KS_{xc}" if xc else "HF"
        kwargs = {"ref": ref, "xc": xc}
        d = {f"{ref}_{_}": RPAMethod(name=_, **kwargs) for _ in names}
        methods.update(d)

        names = ("URPAX2",)
        kwargs.update(ref=f"U{ref}", is_spin_u=True)
        d = {f"U{ref}_{_}": RPAMethod(name=_, **kwargs) for _ in names}
        methods.update(d)

        # ACFD
        names = ("RIRPA",)
        kwargs = {"ref": ref, "is_acfd": True, "xc": xc}
        d = {f"{ref}_{_}": RPAMethod(name=_, **kwargs) for _ in names}
        methods.update(d)

        names = ("URIRPA",)
        kwargs.update(is_spin_u=True)
        d = {f"U{ref}_{_}": RPAMethod(name=_, **kwargs) for _ in names}
        methods.update(d)

    def _replace_df(v: RPAMethod) -> RPAMethod:
        return replace(v, ref=f"DF-{v.ref}", is_df=True)

    methods.update({f"DF-{k}": _replace_df(v) for k, v in methods.items()})

    return methods


def _get_methods_all() -> dict[str, Method]:
    """Get methods."""
    return (
        _make_methods_hf()
        | _make_methods_post_hf()
        | _make_methods_dft()
        | _make_methods_rpa()
    )


methods_all = _get_methods_all()
