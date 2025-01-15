"""Molpro."""

from pathlib import Path

from .data import all_bases, methods_all


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


def make_method_lines(method: str, *, core: bool = True) -> str:
    """Make method lines."""
    props = methods_all[method]

    is_hf = method in {"HF", "DF-HF"}

    str_core = ";CORE" if core and not is_hf else ""
    lines = []
    if props.is_ks:
        return [parse_dft_method(method)]
    if not is_hf:
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


def make_basis_lines(basis: str, *, is_rpa: bool = False) -> list[str]:
    """Make basis lines."""
    if is_rpa:
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


def write(
    method: str,
    basis: str,
    geometry: str = "initial.xyz",
    *,
    core: bool = True,
) -> None:
    """Write."""
    if method not in methods_all:
        raise ValueError(method)

    props = methods_all[method]

    if basis not in all_bases:
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

    p = Path("molpro.inp")
    with p.open("w", encoding="utf-8") as f:
        for line in lines:
            if "__basis__" in line:
                basis_lines = make_basis_lines(basis, is_rpa=props.is_rpa)
                f.write(line.replace("__basis__", basis_lines))
            elif "__method__" in line:
                method_lines = make_method_lines(method, core=core)
                f.write(line.replace("__method__", method_lines))
            else:
                f.write(line)
