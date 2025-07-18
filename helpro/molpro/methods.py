"""Data for MOLPRO."""

from dataclasses import dataclass, replace


@dataclass(frozen=True, kw_only=True)
class MethodProperties:
    """Method properties."""

    name: str
    is_acfd: bool = False
    is_df: bool = False
    is_f12: bool = False
    is_hf: bool = False  # whether this is the HF method
    is_ks: bool = False
    is_ksrpa: bool = False
    is_pno: bool = False
    is_spin_u: bool = False
    xc: str = ""
    ref: str = ""  # reference method name for post-HF and post-KS


def _make_methods_hf() -> dict[str, MethodProperties]:
    """Make HF methods.

    Returns
    -------
    dict[str, MethodProperties]
        HF methods.

    """
    methods = {}

    names_basic = ("HF",)

    names = names_basic
    kwargs = {"is_hf": True}
    methods.update({k: MethodProperties(name=k, **kwargs) for k in names})

    names = tuple(f"R{_}" for _ in names_basic)
    kwargs = {"is_hf": True}
    methods.update({k: MethodProperties(name=k, **kwargs) for k in names})

    names = tuple(f"U{_}" for _ in names_basic)
    kwargs = {"is_hf": True, "is_spin_u": True}
    methods.update({k: MethodProperties(name=k, **kwargs) for k in names})

    methods.update({f"DF-{k}": replace(v, is_df=True) for k, v in methods.items()})

    return methods


def _make_methods_post_hf() -> dict[str, MethodProperties]:
    """Make post-HF methods.

    Returns
    -------
    dict[str, MethodProperties]
        Post-HF methods.

    """
    methods = {}

    names_ps = (
        "MP2",
        "CCSD",
        "CCSD_T",
    )
    kwargs = {"ref": "HF"}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names_ps})

    names = tuple(f"DF-{_}" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-{_}-F12" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True, "is_f12": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-PNO-L{_}" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True, "is_pno": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    names = tuple(f"DF-PNO-L{_}-F12" for _ in names_ps)
    kwargs = {"ref": "DF-HF", "is_df": True, "is_f12": True, "is_pno": True}
    methods.update({_: MethodProperties(name=_, **kwargs) for _ in names})

    return methods


def _make_methods_dft() -> dict[str, MethodProperties]:
    """Make DFT methods.

    https://www.molpro.net/manual/doku.php?id=the_density_functional_program

    Returns
    -------
    dict[str, MethodProperties]
        DFT methods.

    Notes
    -----
    - `DF` is not available for `UKS`; only `CF` is availble.
    - It makes less sense to add the dispersion correction to LDA
      because LDA already has an overbinding nature.

    """
    methods = {}

    xcs = ("LDA", "PBE")
    dispersions = ("", "-D2", "-D3", "-D3_BJ", "-D4")
    for xc in xcs:
        for dispersion in dispersions:
            if xc == "LDA" and dispersion:
                continue
            name = f"KS_{xc}{dispersion}"
            kwargs = {"is_ks": True, "xc": xc}
            methods[name] = MethodProperties(name=name, **kwargs)

            name = f"RKS_{xc}{dispersion}"
            methods[name] = MethodProperties(name=name, **kwargs)

            name = f"UKS_{xc}{dispersion}"
            kwargs.update(is_spin_u=True)
            methods[name] = MethodProperties(name=name, **kwargs)

            kwargs.update(is_df=True, is_spin_u=False)

            name = f"DF-KS_{xc}{dispersion}"
            methods[name] = MethodProperties(name=name, **kwargs)

            name = f"DF-RKS_{xc}{dispersion}"
            methods[name] = MethodProperties(name=name, **kwargs)

    return methods


def _make_methods_rpa() -> dict[str, MethodProperties]:
    """Make RPA methods.

    https://www.molpro.net/manual/doku.php?id=kohn-sham_random-phase_approximation

    Returns
    -------
    dict[str, MethodProperties]
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
        kwargs = {"ref": ref, "is_ksrpa": True, "xc": xc}
        d = {f"{ref}_{_}": MethodProperties(name=_, **kwargs) for _ in names}
        methods.update(d)

        names = ("URPAX2",)
        kwargs.update(ref=f"U{ref}", is_spin_u=True)
        d = {f"U{ref}_{_}": MethodProperties(name=_, **kwargs) for _ in names}
        methods.update(d)

        # ACFD
        names = ("RIRPA",)
        kwargs = {"ref": ref, "is_acfd": True, "xc": xc}
        d = {f"{ref}_{_}": MethodProperties(name=_, **kwargs) for _ in names}
        methods.update(d)

        names = ("URIRPA",)
        kwargs.update(is_spin_u=True)
        d = {f"U{ref}_{_}": MethodProperties(name=_, **kwargs) for _ in names}
        methods.update(d)

    def _replace_df(v: MethodProperties) -> MethodProperties:
        return replace(v, ref=f"DF-{v.ref}", is_df=True)

    methods.update({f"DF-{k}": _replace_df(v) for k, v in methods.items()})

    return methods


def _get_methods_all() -> dict[str, MethodProperties]:
    """Get methods."""
    return (
        _make_methods_hf()
        | _make_methods_post_hf()
        | _make_methods_dft()
        | _make_methods_rpa()
    )


methods_all = _get_methods_all()
