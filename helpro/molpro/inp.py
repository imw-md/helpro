"""Molpro."""

from pathlib import Path

from .bases import bases_all
from .methods import methods_all


def parse_dft_method(method: str) -> str:
    """Parse a DFT method."""
    dispersion = method.split("-")[-1].replace("_BJ", ",BJ")
    is_dispersion = dispersion in {"D2", "D3", "D3,BJ", "D4"}
    if is_dispersion:
        ks, xc = method.split("_")[:2]
        xc = xc.split("-")[0]
        return f"{{{ks},{xc};DISP,{dispersion}}}"
    ks, xc = method.split("_")
    return f"{{{ks},{xc}}}"


def parse_rpa_method(method: str, *, core: str) -> str:
    """Parse an RPA method."""
    props = methods_all[method]
    lines = []
    if props.xc:
        if props.is_spin_u:
            ref = f"DF-UKS_{props.xc}" if props.is_df else f"UKS_{props.xc}"
        else:
            ref = f"DF-KS_{props.xc}" if props.is_df else f"KS_{props.xc}"
        lines.append(parse_dft_method(ref))
    else:
        if props.is_spin_u:
            ref = "DF-UHF" if props.is_df else "UHF"
        else:
            ref = "DF-HF" if props.is_df else "HF"
        lines.append(f"{{{ref}}}")
    rpa = method.split("_")[-1]
    orb = "2200.2" if props.is_spin_u else "2100.2"
    if props.is_ksrpa:
        str_core = ",CORE=0" if core == "active" else ""
        lines.append(f"{{KSRPA;{rpa},ORB={orb}{str_core}}}")
    elif props.is_acfd:
        if core == "active":
            msg = "The active-core calculation is not available for AFCD."
            raise RuntimeError(msg)
        lines.append(f"{{ACFD;{rpa},ORB={orb}}}")
    else:
        raise RuntimeError(method)
    return "\n".join(lines)


def make_method_lines(method: str, *, core: str) -> str:
    """Make method lines."""
    props = methods_all[method]

    str_core = ";CORE" if core == "active" and not props.is_hf else ""
    lines = []
    if props.is_ks:
        lines.append(parse_dft_method(method))
        return "\n".join(lines)
    if props.is_ksrpa or props.is_acfd:
        lines.append(parse_rpa_method(method, core=core))
        return "\n".join(lines)
    if props.is_hf:
        lines.append(f"{{{method}}}")
        return "\n".join(lines)

    lines.append("{DF-HF}" if props.is_df else "{HF}")
    if props.is_pno and props.is_f12:
        lines.append(f"{{DF-CABS{str_core}}}")
    method = method.replace("CCSD_T", "CCSD(T)")
    method = method.replace("DF-PNO", "PNO")
    lines.append(f"{{{method}{str_core}}}")

    return "\n".join(lines)


def parse_heavy_basis(basis: str) -> str:
    """Parse heavy basis."""
    if basis.startswith("heavy-"):
        basis = basis.replace("heavy-", "")
        basis_hydrogen = basis.replace("aug-", "")
        return f"{basis},H={basis_hydrogen}"
    return basis


def make_basis_lines(method: str, basis: str) -> list[str]:
    """Make basis lines."""
    props = methods_all[method]
    if props.is_ksrpa:
        lines = (
            r"{",
            r"SET,ORBITAL",
            f"DEFAULT={basis}",
            r"SET,MP2FIT",
            f"DEFAULT={basis}",
            r"}",
        )
        return "\n".join(lines)
    if props.is_acfd:
        lines = (
            r"{",
            r"SET,ORBITAL",
            f"DEFAULT={basis}",
            r"SET,RI,CONTEXT=MP2FIT",
            f"DEFAULT={basis}",
            r"}",
        )
        return "\n".join(lines)
    return basis


def write_molpro_inp(
    method: str,
    basis: str,
    geometry: str = "initial.xyz",
    *,
    core: str = "active",
    fname: str = "molpro.inp",
) -> None:
    """Write MOLPRO input.

    Parameters
    ----------
    method : str
        Method.
    basis : str
        Basis set.
    geometry : str, default: "initial.xyz"
        Geometry file.
    core : {"active", "frozen"}, default: "active"
        Whether the core is active or frozen.
    fname : str, default: "molpro.inp"
        Input file name.

    """
    if method not in methods_all:
        raise ValueError(method)

    if basis not in bases_all:
        raise ValueError(basis)

    basis = parse_heavy_basis(basis)

    lines = (
        r"GPRINT,ORBITALS",
        r"NOSYM",
        r"ANGSTROM",
        f"GEOMETRY={geometry}",
        r"BASIS=__basis__",
        r"__method__",
    )
    lines = tuple(f"{_}\n" for _ in lines)

    p = Path(fname)
    with p.open("w", encoding="utf-8") as f:
        for line in lines:
            if "__basis__" in line:
                basis_lines = make_basis_lines(method, basis)
                f.write(line.replace("__basis__", basis_lines))
            elif "__method__" in line:
                method_lines = make_method_lines(method, core=core)
                f.write(line.replace("__method__", method_lines))
            else:
                f.write(line)
