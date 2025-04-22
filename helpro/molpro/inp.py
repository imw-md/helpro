"""Molpro."""

import argparse
from dataclasses import KW_ONLY, dataclass, field
from pathlib import Path

from .bases import bases_all
from .methods import methods_all


def make_wf_directive(charge: int | None, spin: int | None) -> str:
    """Make the WF directive.

    Returns
    -------
    wf : str
        WF directive.

    """
    wf = ""
    if charge is not None or spin is not None:
        wf = ";WF"
        if charge is not None:
            wf += f",CHARGE={charge}"
        if spin is not None:
            wf += f",SPIN={spin}"
    return wf


def parse_dft_method(method: str, wf_directive: str = "") -> str:
    """Parse a DFT method.

    https://www.molpro.net/manual/doku.php?id=the_density_functional_program

    Returns
    -------
    dft : str
        DFT command.

    """
    dispersion = method.split("-")[-1].replace("_BJ", ",BJ")
    is_dispersion = dispersion in {"D2", "D3", "D3,BJ", "D4"}
    ks, xc = method.split("_")[:2]
    disp_directive = ""
    if is_dispersion:
        xc = xc.split("-")[0]
        disp_directive = f";DISP,{dispersion}"
    return f"{{{ks},{xc}{disp_directive}{wf_directive}}}"


def parse_rpa_method(method: str, *, core: str, wf_directive: str) -> str:
    """Parse an RPA method.

    https://www.molpro.net/manual/doku.php?id=kohn-sham_random-phase_approximation

    Returns
    -------
    rpa : str
        RPA command.

    Raises
    ------
    RuntimeError
        If `core=='active'` is specified for AFCD.

    """
    props = methods_all[method]
    lines = []
    if props.xc:
        lines.append(parse_dft_method(props.ref, wf_directive))
    else:
        lines.append(f"{{{props.ref}{wf_directive}}}")
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


def make_method_lines(
    method: str,
    *,
    core: str,
    charge: int | None = None,
    spin: int | None = None,
) -> str:
    """Make method lines.

    Returns
    -------
    command : str
        Command.

    """
    props = methods_all[method]

    str_core = ";CORE" if core == "active" and not props.is_hf else ""
    wf_directive = make_wf_directive(charge, spin)
    lines = []
    if props.is_ks:
        lines.append(parse_dft_method(method, wf_directive=wf_directive))
        return "\n".join(lines)
    if props.is_ksrpa or props.is_acfd:
        lines.append(parse_rpa_method(method, core=core, wf_directive=wf_directive))
        return "\n".join(lines)
    if props.is_hf:
        lines.append(f"{{{method}{wf_directive}}}")
        return "\n".join(lines)

    lines.append(f"{{{props.ref}{wf_directive}}}")
    if props.is_pno and props.is_f12:
        lines.append(f"{{DF-CABS{str_core}}}")
    method = method.replace("CCSD_T", "CCSD(T)")
    method = method.replace("DF-PNO", "PNO")
    lines.append(f"{{{method}{str_core}}}")

    return "\n".join(lines)


def parse_heavy_basis(basis: str) -> str:
    """Parse heavy basis.

    Returns
    -------
    basis : str
        Command for the heavy-augmented basis set.

    """
    if basis.startswith("heavy-"):
        basis = basis.replace("heavy-", "")
        basis_hydrogen = basis.replace("aug-", "")
        return f"{basis},H={basis_hydrogen}"
    return basis


def make_basis_lines(method: str, basis: str) -> list[str]:
    """Make basis lines.

    https://www.molpro.net/manual/doku.php?id=basis_input

    Returns
    -------
    basis : str
        Commnd for the basis set.

    """
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


def validate_options(options: str | list[str] | None) -> list[str]:
    """Validate options.

    Returns
    -------
    options : list[str]
        Validated options.

    Raises
    ------
    ValueError
        If the given option is not recognized by HELPRO.

    """
    if options is None:
        options = []
    if isinstance(options, str):
        options = [options]
    options = [option.upper() for option in options]
    options_all = "FORCES", "OPTG", "COUNTERPOISE"
    for option in options:
        if all(not option.startswith(_) for _ in options_all):
            raise ValueError(option)
    return options


@dataclass(slots=True)
class MolproInputGeometry:
    """Geometry for MOLPRO input file."""

    fname: str = "initial.xyz"
    _: KW_ONLY
    dummies: list[int] | None = None
    skip: bool = False

    def make_lines(self) -> str:
        """Make lines related to `GEOMETRY`.

        Returns
        -------
        geometry : str
            GEOMETRY command.

        """
        lines = [r"ANGSTROM"]
        lines.append(f"GEOMETRY={self.fname}")
        if self.dummies:
            line = "DUMMY,"
            if self.skip:
                line += "SKIP,"
            line += ",".join(str(_) for _ in self.dummies)
            lines.append(line)
        return "\n".join(lines)


@dataclass(slots=True)
class MolproInputWriter:
    """Writer of MOLPRO input file.

    Attributes
    ----------
    method : str
        Method.
    basis : str
        Basis set.
    core : {"active", "frozen"}, default: "active"
        Whether the core is active or frozen.
    charge : int | None, default: None
        Charge.
    spin : int | None, default: None
        Spin.
    options : {"FORCES", "OPTG", "COUNTERPOISE"}
        Option(s).
    geometry : str, default: "initial.xyz"
        Geometry file.

    """

    method: str
    basis: str
    _: KW_ONLY
    core: str = "active"
    geometry: MolproInputGeometry = field(default_factory=MolproInputGeometry)
    charge: int | None = None
    spin: int | None = None
    options: list[str] | str | None = None

    def __post_init__(self) -> None:
        """Post-process attributes."""
        if isinstance(self.geometry, str):
            self.geometry = MolproInputGeometry(self.geometry)

    def write(self, fname: str | None = None) -> None:
        """Write MOLPRO input file.

        Parameters
        ----------
        fname : str, default: "molpro.inp"
            Input file name.

        Raises
        ------
        ValueError
            If the method or the basis set is not recognized by HELPRO.

        """
        if fname is None:
            fname = "molpro.inp"

        if self.method not in methods_all:
            raise ValueError(self.method)

        if self.basis not in bases_all:
            raise ValueError(self.basis)

        self.options = validate_options(self.options)

        lines = (
            r"GPRINT,ORBITALS",
            r"NOSYM",
            self.geometry.make_lines(),
            r"BASIS=__basis__",
            r"__method__",
        )
        lines = tuple(f"{_}\n" for _ in lines)

        basis_lines = make_basis_lines(
            self.method,
            parse_heavy_basis(self.basis),
        )

        method_lines = make_method_lines(
            self.method,
            core=self.core,
            charge=self.charge,
            spin=self.spin,
        )

        p = Path(fname)
        with p.open("w", encoding="utf-8") as f:
            for line in lines:
                if "__basis__" in line:
                    f.write(line.replace("__basis__", basis_lines))
                elif "__method__" in line:
                    f.write(line.replace("__method__", method_lines))
                else:
                    f.write(line)
            for option in self.options:
                f.write(f"{option}\n")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments."""
    parser.add_argument("--method", default="HF")
    parser.add_argument("--basis", default="cc-pVDZ")
    parser.add_argument("--core", default="frozen", choices=("frozen", "active"))
    parser.add_argument("--geometry", default="initial.xyz")
    parser.add_argument("--charge", type=int)
    parser.add_argument("--spin", type=int)


def run(args: argparse.Namespace) -> None:
    """Run."""
    miw = MolproInputWriter(
        method=args.method,
        basis=args.basis,
        core=args.core,
        geometry=args.geometry,
        charge=args.charge,
        spin=args.spin,
    )
    miw.write("molpro.inp")
