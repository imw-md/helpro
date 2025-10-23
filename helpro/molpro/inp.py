"""Molpro."""

import argparse
from dataclasses import KW_ONLY, dataclass, field
from pathlib import Path

from .bases import bases_all
from .methods import (
    DFTMethod,
    Method,
    PostHFMethod,
    RPAMethod,
    dispersions,
    make_method_dft,
    methods_all,
    names_dft,
)


def make_wf_directive(charge: int | None, multiplicity: int | None) -> str:
    """Make the WF directive.

    Parameters
    ----------
    charge : int, optional
        Charge.

    multiplicity : int, optional
        Spin multiplicity.

    Returns
    -------
    wf : str
        WF directive.

    """
    wf = ""
    if charge is not None or multiplicity is not None:
        wf = ";WF"
        if charge is not None:
            wf += f",CHARGE={charge}"
        if multiplicity is not None:
            wf += f",SPIN={multiplicity - 1}"
    return wf


def parse_dft_method(method: DFTMethod, wf_directive: str = "") -> str:
    """Parse a DFT method.

    https://www.molpro.net/manual/doku.php?id=the_density_functional_program

    Returns
    -------
    dft : DFTMethod
        DFT command.

    Raises
    ------
    RuntimeError
        If `method` cannot be parsed.

    """
    dispersion = method.dispersion.replace("_BJ", ",BJ")
    is_dispersion = dispersion in {"D2", "D3", "D3,BJ", "D4"}
    for name in names_dft:
        if method.name.startswith(name):
            ks = name
            break
    else:
        raise RuntimeError(method)
    xc = method.xc
    option = f",GRIDTHR={method.gridthr:G}" if method.gridthr else ""
    disp_directive = f";DISP,{dispersion}" if is_dispersion else ""
    return f"{{{ks},{xc}{option}{disp_directive}{wf_directive}}}"


def parse_rpa_method(method: RPAMethod, *, core: str, wf_directive: str) -> str:
    """Parse an RPA method.

    https://www.molpro.net/manual/doku.php?id=kohn-sham_random-phase_approximation

    Returns
    -------
    rpa : RPAMethod
        RPA command.

    Raises
    ------
    RuntimeError
        If `core=='active'` is specified for AFCD.

    """
    lines = []
    if method.xc:
        method_dft = DFTMethod(
            name=method.ref,
            xc=method.xc,
            is_df=method.is_df,
            is_spin_u=method.is_spin_u,
        )
        lines.append(parse_dft_method(method_dft, wf_directive))
    else:
        lines.append(f"{{{method.ref}{wf_directive}}}")
    rpa = method.name.split("_")[-1]
    orb = "2200.2" if method.is_spin_u else "2100.2"
    if method.is_acfd:
        if core == "active":
            msg = "The active-core calculation is not available for AFCD."
            raise RuntimeError(msg)
        lines.append(f"{{ACFD;{rpa},ORB={orb}}}")
    else:
        str_core = ",CORE=0" if core == "active" else ""
        lines.append(f"{{KSRPA;{rpa},ORB={orb}{str_core}}}")
    return "\n".join(lines)


def parse_post_hf_method(method: PostHFMethod, *, core: str, wf_directive: str) -> str:
    """Parse a post-HF method."""
    option = ""
    if method.cabs_singles is not None and not method.is_pno and method.is_f12:
        option += f",CABS_SINGLES={method.cabs_singles}"
    if method.core_singles is not None and not method.is_pno and method.is_f12:
        option += f",CORE_SINGLES={method.core_singles}"

    str_core = ";CORE" if core == "active" and not method.is_hf else ""

    lines = []
    lines.append(f"{{{method.ref}{wf_directive}}}")
    if method.is_pno and method.is_f12:
        lines.append(f"{{DF-CABS{str_core}}}")
    name = method.name.replace("CCSD_T", "CCSD(T)")
    name = method.name.replace("DF-PNO", "PNO")
    lines.append(f"{{{name}{option}{str_core}}}")
    return "\n".join(lines)


def make_method_lines(
    method: Method,
    *,
    core: str,
    charge: int | None = None,
    multiplicity: int | None = None,
) -> str:
    """Make method lines.

    Parameters
    ----------
    method : Method
        Method.
    core : {'frozen', 'active'}
        Core-electron excitation.
    charge : int, optional
        Charge.
    multiplicity : int, optional
        Spin multiplicity.

    Returns
    -------
    command : str
        Command.

    Raises
    ------
    ValueError
        If `method` cannot be parsed.

    """
    wf_directive = make_wf_directive(charge, multiplicity)
    lines = []
    if isinstance(method, DFTMethod):
        lines.append(parse_dft_method(method, wf_directive=wf_directive))
        return "\n".join(lines)
    if isinstance(method, RPAMethod):
        lines.append(parse_rpa_method(method, core=core, wf_directive=wf_directive))
        return "\n".join(lines)
    if method.is_hf:
        lines.append(f"{{{method.name}{wf_directive}}}")
        return "\n".join(lines)
    if isinstance(method, PostHFMethod):
        lines.append(parse_post_hf_method(method, core=core, wf_directive=wf_directive))
        return "\n".join(lines)
    raise ValueError(method)


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


def make_basis_lines(method: Method, basis: str) -> list[str]:
    """Make basis lines.

    https://www.molpro.net/manual/doku.php?id=basis_input

    Returns
    -------
    basis : str
        Commnd for the basis set.

    """
    basis = parse_heavy_basis(basis)

    if isinstance(method, RPAMethod):
        if method.is_acfd:
            lines = (
                r"BASIS={",
                r"SET,ORBITAL",
                f"DEFAULT={basis}",
                r"SET,RI,CONTEXT=MP2FIT",
                f"DEFAULT={basis}",
                r"}",
            )
        else:
            lines = (
                r"BASIS={",
                r"SET,ORBITAL",
                f"DEFAULT={basis}",
                r"SET,MP2FIT",
                f"DEFAULT={basis}",
                r"}",
            )
        return "\n".join(lines)
    return f"BASIS={basis}"


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
    options_all = "FORCES", "OPTG", "FREQUENCIES", "COUNTERPOISE"
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


def _make_default_template() -> tuple[str]:
    lines = (
        r"GPRINT,ORBITALS",
        r"NOSYM",
        r"{{geometry}}",
        r"{{basis}}",
        r"{{method}}",
    )
    return tuple(f"{_}\n" for _ in lines)


@dataclass(slots=True)
class MolproInputWriter:
    """Writer of MOLPRO input file.

    Attributes
    ----------
    method : str | Method
        Method.
    basis : str
        Basis set.
    core : {"active", "frozen"}, default: "frozen"
        Whether the core is active or frozen.
    method_options : dict
        Method options.
    charge : int | None, default: None
        Charge.
    multiplicity : int | None, default: None
        Spin multiplicity.
    options : {"FORCES", "OPTG", "FREQUENCIES", "COUNTERPOISE"}
        Option(s).
    geometry : str, default: "initial.xyz"
        Geometry file.

    """

    method: str | Method
    basis: str
    _: KW_ONLY
    core: str = "frozen"
    method_options: dict = field(default_factory=dict)
    cabs_singles: int | None = None
    core_singles: int | None = None
    geometry: MolproInputGeometry = field(default_factory=MolproInputGeometry)
    charge: int | None = None
    multiplicity: int | None = None
    options: list[str] | str | None = None
    template: tuple[str] | None = field(default_factory=_make_default_template)

    def __post_init__(self) -> None:
        """Post-process attributes."""
        if isinstance(self.geometry, str):
            self.geometry = MolproInputGeometry(self.geometry)
        if isinstance(self.template, Path | str):
            if isinstance(self.template, str):
                path = Path(self.template)
            else:
                path = self.template
            with path.open(encoding="utf-8") as fd:
                self.template = tuple(fd.readlines())
        elif self.template is None:
            self.template = _make_default_template()

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

        if isinstance(self.method, Method):
            method = self.method
        else:
            method = methods_all[self.method]

        for k, v in self.method_options.items():
            if v is not None:
                setattr(method, k, v)

        if self.basis not in bases_all:
            raise ValueError(self.basis)

        self.options = validate_options(self.options)

        basis_lines = make_basis_lines(method, self.basis)

        method_lines = make_method_lines(
            method,
            core=self.core,
            charge=self.charge,
            multiplicity=self.multiplicity,
        )

        dct = {
            r"{{geometry}}": self.geometry.make_lines(),
            r"{{basis}}": basis_lines,
            r"{{method}}": method_lines,
        }

        p = Path(fname)
        with p.open("w", encoding="utf-8") as f:
            for line in self.template:
                for k, v in dct.items():
                    if k in line:
                        f.write(line.replace(k, v))
                        break
                else:
                    f.write(line)
            for option in self.options:
                f.write(f"{option}\n")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments."""
    parser.add_argument("--method", default="HF")
    parser.add_argument("--xc", default="LDA")
    parser.add_argument("--dispersion", default="", choices=dispersions)
    parser.add_argument("--gridthr", type=float)
    parser.add_argument("--basis", default="cc-pVDZ")
    parser.add_argument("--core", default="frozen", choices=("frozen", "active"))
    parser.add_argument("--cabs-singles", type=int)
    parser.add_argument("--core-singles", type=int)
    parser.add_argument("--geometry", default="initial.xyz")
    parser.add_argument("--charge", type=int)
    parser.add_argument("--multiplicity", type=int)
    parser.add_argument("-t", "--template", help="Template filename")


def run(args: argparse.Namespace) -> None:
    """Run."""
    method_options = {
        "cabs_singles": args.cabs_singles,
        "core_singles": args.core_singles,
    }
    if args.method in names_dft:
        # register the user specified DFT method
        method = make_method_dft(
            name=args.method,
            xc=args.xc,
            dispersion=args.dispersion,
            gridthr=args.gridthr,
        )
    else:
        method = args.method
    miw = MolproInputWriter(
        method=method,
        basis=args.basis,
        core=args.core,
        method_options=method_options,
        geometry=args.geometry,
        charge=args.charge,
        multiplicity=args.multiplicity,
        template=args.template,
    )
    miw.write("molpro.inp")
