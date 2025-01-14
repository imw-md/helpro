"""Molpro."""

from pathlib import Path

methods = (
    "HF",
    "MP2",
    "CCSD",
    "CCSD_T",
    "DF-HF",
    "DF-MP2",
    "DF-CCSD",
    "DF-CCSD_T",
    "DF-MP2-F12",
    "DF-CCSD-F12",
    "DF-CCSD_T-F12",
    "DF-PNO-LMP2",
    "DF-PNO-LCCSD",
    "DF-PNO-LCCSD_T",
    "DF-PNO-LMP2-F12",
    "DF-PNO-LCCSD-F12",
    "DF-PNO-LCCSD_T-F12",
)

methods_dft = (
    "KS_LDA",
    "KS_PBE",
    "KS_PBE-D2",
    "KS_PBE-D3",
    "KS_PBE-D3_BJ",
    "KS_PBE-D4",
    "DF-KS_LDA",
    "DF-KS_PBE",
    "DF-KS_PBE-D2",
    "DF-KS_PBE-D3",
    "DF-KS_PBE-D3_BJ",
    "DF-KS_PBE-D4",
)

methods_rpa = (
    "KSRPA_DIRPA",
    "KSRPA_RPAX2",
    # "KSRPA_ACFDT",
    # "KSRPA_RIRPA",  # equivalent to ACFD_RIRPA
    "ACFD_RIRPA",
    # "RPATDDFT",
)

methods += methods_dft + methods_rpa

bases = (
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
    is_hf = method in {"HF", "DF-HF"}
    is_df = method.startswith("DF-")
    is_dft = method.replace("DF-", "").startswith("KS")
    is_pno = method.replace("DF-", "").startswith("PNO")
    is_f12 = method.endswith("-F12")
    str_core = ";CORE" if core and not is_hf else ""
    lines = []
    if is_dft:
        return [parse_dft_method(method)]
    if not is_hf:
        lines.append("{DF-HF}" if is_df else "{HF}")
    if is_pno and is_f12:
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
    is_rpa = method in methods_rpa
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
                basis_lines = make_basis_lines(basis, is_rpa=is_rpa)
                f.write(line.replace("__basis__", basis_lines))
            elif "__method__" in line:
                method_lines = make_method_lines(method, core=core)
                f.write(line.replace("__method__", method_lines))
            else:
                f.write(line)
