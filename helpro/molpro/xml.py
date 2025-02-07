"""Module for MOLPRO xml formats."""

import abc
import warnings
import xml.etree.ElementTree as ET

import numpy as np
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.units import Angstrom, Bohr, Hartree, eV
from ase.utils import string2index

namespaces = {
    "": "http://www.molpro.net/schema/molpro-output",
    "cml": "http://www.xml-cml.org/schema",
}


class MolproXMLParser:
    """Parser of `molpro.xml`."""

    def __init__(self) -> None:
        """Initialize."""
        self.platform = {}

    @property
    def is_angstrom(self) -> bool:
        """Return whether the geometry is given in Ångstrom."""
        return self._is_angstrom

    @is_angstrom.setter
    def is_angstrom(self, is_angstrom: bool) -> None:
        self._is_angstrom = is_angstrom

    def parse_platform(self, platform: ET.Element) -> dict:
        """Parse "platform" element."""
        version = platform.find("version", namespaces)
        parallel = platform.find("parallel", namespaces)
        self.platform = {
            "major": int(version.attrib["major"]),
            "minor": int(version.attrib["minor"]),
            "processes": int(parallel.attrib["processes"]),
            "nodes": int(parallel.attrib["nodes"]),
            "openmp": int(parallel.attrib["openmp"]),
        }

    def parse_energy(
        self,
        jobstep: ET.Element,
        command: str,
    ) -> tuple[dict[str, float], Atoms | None]:
        """Parse energy."""
        results = {}
        command = jobstep.attrib["command"]

        child = jobstep.find("cml:molecule", namespaces)
        if child is not None:
            atoms = self.parse_atom_array_tag(child.find("cml:atomArray", namespaces))
        else:
            atoms = None

        energy_parser = get_energy_parsers()[command](namespaces)
        results = energy_parser.fetch(jobstep)
        for child in jobstep.findall("property", namespaces):
            if child.attrib["name"] == "EREL":
                keyr = "relativistic_correction"
                results[keyr] = float(child.attrib["value"].split()[-1])
        results = {k: v * (Hartree / eV) for k, v in results.items()}
        if "energy" in results:
            results["free_energy"] = results["energy"]
        parameters = {"command": command}

        if len(jobstep.findall("error", namespaces)) != 0:
            for child in jobstep.findall("error", namespaces):
                warnings.warn(child.attrib["message"], stacklevel=1)
                if child.attrib["type"] == "Warning":
                    results = {}

        return atoms, parameters, results

    def parse_atom_array_tag(self, atom_array: ET.Element) -> Atoms:
        """Parse "atomArray" tag."""
        symbols = []
        positions = []
        for child in atom_array:
            symbols.append(child.attrib["elementType"])
            positions.append([float(child.attrib[_]) for _ in ["x3", "y3", "z3"]])
        if not self.is_angstrom:
            positions = np.array(positions) / Angstrom
        return Atoms(symbols=symbols, positions=positions)

    def parse_counterpoise(self, jobstep: ET.Element, command: str) -> float:
        """Parse the COUNTERPOISE jobstep.

        The COUNTERPOISE jobstep consists of four sets of subjobsteps (for a dimer).

        The order of the monomer calculations depends on the Molpro version.

        In 2021.3:

        - 1st monomer without ghost atoms
        - 2nd monomer without ghost atoms
        - 1st monomer with ghost atoms
        - 2nd monomer with ghost atoms

        In 2024.1:

        - 1st monomer with ghost atoms
        - 2nd monomer with ghost atoms
        - 1st monomer without ghost atoms
        - 2nd monomer without ghost atoms

        Returns
        -------
        float
            Counterpoise correction.

        """
        subjobsteps = jobstep.findall("jobstep", namespaces)
        subjobsteps = [_ for _ in subjobsteps if _.attrib["command"] == command]

        # monomer
        if len(subjobsteps) == 0:
            return 0.0

        # check number of monomers
        if len(subjobsteps) != 4:
            raise RuntimeError

        list_results = [self.parse_energy(_, command)[-1] for _ in subjobsteps]

        for results in list_results:
            if "energy" not in results:
                warnings.warn("The energy is not available.", stacklevel=1)
                return float("nan")

        dea = list_results[2]["energy"] - list_results[0]["energy"]
        deb = list_results[3]["energy"] - list_results[1]["energy"]
        if self.platform["major"] == 2021:
            dea *= -1.0
            deb *= -1.0
        return dea + deb

    def parse_forces(self, jobstep: ET.Element) -> np.ndarray:
        """Parse `gradient`."""
        child = jobstep.find("gradient", namespaces)
        gradient = np.array(child.text.split(), dtype=float).reshape(-1, 3)
        return gradient * -1.0 * (Hartree / eV) / (Bohr / Angstrom)


def read_molpro_xml(filename: str, index: int | slice | str = -1) -> Atoms:
    """Read MOLPRO xml file."""
    try:
        tree = ET.parse(filename)
    except ET.ParseError:
        atoms = Atoms()
        atoms.calc = SinglePointCalculator(atoms)
        d = {
            "major": -1,
            "minor": -1,
            "processes": -1,
            "nodes": -1,
            "openmp": -1,
        }
        atoms.calc.results.update(d)
        return atoms
    root = tree.getroot()
    job = root.find("job", namespaces)
    is_angstrom = parse_input_tag(job)

    parser = MolproXMLParser()
    parser.is_angstrom = is_angstrom

    parser.parse_platform(job.find("platform", namespaces))

    energy_parsers = get_energy_parsers()

    commands = []
    info = {}
    atoms = None
    images = []
    cpu_time = 0.0
    real_time = 0.0
    for jobstep in job.findall("jobstep", namespaces):
        command = jobstep.attrib["command"]
        if command in energy_parsers:
            _, parameters, energies = parser.parse_energy(jobstep, command)
            atoms = atoms.copy() if _ is None else _  # copy previous one if absent
            calc = SinglePointCalculator(atoms)
            calc.parameters = parameters
            calc.results.update(energies)
            atoms.calc = calc
            images.append(atoms)
        elif command == "COUNTERPOISE":
            atoms = images[-1]
            correction = parser.parse_counterpoise(jobstep, commands[-1])
            atoms.calc.results["CP_correction"] = correction
            atoms.calc.results["energy"] += correction
        elif command == "FORCES":
            atoms = images[-1]
            atoms.calc.results["forces"] = parser.parse_forces(jobstep)
        commands.append(command)

        time = jobstep.find("time", namespaces)
        if time is not None:
            cpu_time += float(time.attrib.get("cpu", float("nan")))
            real_time += float(time.attrib.get("real", float("nan")))

        storage = jobstep.find("storage", namespaces)
        if storage is not None:
            for attrib in ["sf", "df", "eaf", "ga"]:
                info[attrib] = float(storage.attrib[attrib])

    info["cpu_time"] = cpu_time
    info["real_time"] = real_time

    info.update(parser.platform)

    images[-1].calc.results.update(info)

    if isinstance(index, str):
        index = string2index(index)

    return images[index]


class EnergyParser(abc.ABC):
    """Parser of an energy-computing jobstep."""

    keym = "MP2_energy"
    key_mp2_f12 = "MP2_F12_energy"
    keyc = "correlation_energy"
    keyt = "energy"

    def __init__(self, namespaces: dict[str, str]):
        self.namespaces = namespaces

    @abc.abstractmethod
    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        """Fetch energy values."""


class EnergyParserSCF(EnergyParser):
    """Parser for HF and KS."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            if name == "Energy":
                results[self.keyt] = float(child.attrib["value"].split()[-1])
        return results


class EnergyParserMP2(EnergyParser):
    """Parser for DF-MP2."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            method = child.attrib.get("method")
            value = float(child.attrib["value"].split()[-1])
            if name == "correlation energy":
                results[self.keyc] = value
            if name == "energy" and method == "DF-RMP2 correlation":
                results[self.keyc] = value
            if name == "total energy":  # MP2, MP2-F12
                results[self.keyt] = value
            if name == "energy" and method == "DF-RMP2":  # RMP2
                results[self.keyt] = value
        return results


class EnergyParserCCSD(EnergyParser):
    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            method = child.attrib.get("method")
            value = float(child.attrib["value"].split()[-1])
            if name == "total energy" and method == "MP2":
                results[self.keym] = value
            if name == "energy" and method == "RHF-RMP2":
                results[self.keym] = value
            if name == "correlation energy" and method == "CCSD":
                results[self.keyc] = value
            if name == "energy" and method == "UCCSD correlation":
                results[self.keyc] = value
            if name == "total energy" and method == "CCSD":
                results[self.keyt] = value
            if name == "energy" and method == "RHF-UCCSD":
                results[self.keyt] = value
        return results


class EnergyParserCCSDT(EnergyParser):
    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            method = child.attrib.get("method")
            value = float(child.attrib["value"].split()[-1])
            if name == "total energy" and method == "MP2":
                results[self.keym] = value
            if name == "energy" and method in "RHF-RMP2":
                results[self.keym] = value
            if name == "correlation energy" and method == "Total":
                results[self.keyc] = value
            if name == "energy" and method == "Total correlation":
                results[self.keyc] = value
            if name == "total energy" and method == "CCSD(T)":
                results[self.keyt] = value  # RCCSD(T)
            if name == "energy" and method == "RHF-UCCSD(T)":
                results[self.keyt] = value  # UCCSD(T)
        return results


class EnergyParserPNO(EnergyParser):
    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        command = jobstep.attrib["command"]
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            method = child.attrib.get("method")
            value = float(child.attrib["value"].split()[-1])
            if method == "PNO-LMP2 total energy":
                results[self.keym] = value
            if method == f"{command} correlation energy":
                results[self.keyc] = value
            if method == "PNO-RCCSD correlation energy":
                results[self.keyc] = value
            if method == f"{command} total energy":
                results[self.keyt] = value
            if method == "PNO-RCCSD total energy":
                results[self.keyt] = value
        return results


class EnergyParserPNOLMP2F12(EnergyParser):
    """Parser for PNO-LMP2-F12."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            method = child.attrib.get("method")
            if method == "PNO-LMP2 total energy":
                results[self.keym] = float(child.attrib["value"].split()[-1])
            if method == "PNO-LMP2-F12(PNO) corr. energy":
                results[self.keyc] = float(child.attrib["value"].split()[-1])
            if method == "PNO-LMP2-F12(PNO) total energy":
                results[self.key_mp2_f12] = float(child.attrib["value"].split()[-1])
                results[self.keyt] = float(child.attrib["value"].split()[-1])
        return results


class EnergyParserPNOLCCSDF12(EnergyParser):
    """Parser for PNO-LCCSD-F12."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            method = child.attrib.get("method")
            if method == "PNO-LMP2 total energy":
                # PNO-LMP2 energy with LCCSD domains
                results[self.keym] = float(child.attrib["value"].split()[-1])
            if method == "PNO-LMP2-F12 total energy":
                # PNO-LMP2-F12 energy with LCCSD domains
                results[self.key_mp2_f12] = float(child.attrib["value"].split()[-1])
            if method == "PNO-LCCSD-F12b correlation energy":
                results[self.keyc] = float(child.attrib["value"].split()[-1])
            if method == "PNO-LCCSD-F12b total energy":
                results[self.keyt] = float(child.attrib["value"].split()[-1])
        return results


class EnergyParserPNOLCCSDT(EnergyParser):
    """Parser for PNO-LCCSD(T)."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        command = "PNO-LCCSD(T)"
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            method = child.attrib.get("method")
            if method == "PNO-LMP2 total energy":
                results[self.keym] = float(child.attrib["value"].split()[-1])
            if name == "corr. energy" and method == command:
                results[self.keyc] = float(child.attrib["value"].split()[-1])
            if name == "total energy" and method == command:
                results[self.keyt] = float(child.attrib["value"].split()[-1])
        return results


class EnergyParserPNOLCCSDTF12(EnergyParser):
    """Parser for PNO-LCCSD(T)-F12."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            method = child.attrib.get("method")
            if method == "PNO-LMP2 total energy":
                results[self.keym] = float(child.attrib["value"].split()[-1])
            if method == "PNO-LMP2-F12 total energy":
                # PNO-LMP2-F12 energy with LCCSD domains
                results[self.key_mp2_f12] = float(child.attrib["value"].split()[-1])
            if name == "corr. energy":
                results[self.keyc] = float(child.attrib["value"].split()[-1])
            if name == "total energy":
                results[self.keyt] = float(child.attrib["value"].split()[-1])
        return results


class EnergyParserRPA(EnergyParser):
    """Parser for RPA."""

    def fetch(self, jobstep: ET.Element) -> dict[str, float]:
        results = {self.keyt: float("nan")}
        for child in jobstep.findall("property", self.namespaces):
            name = child.attrib["name"]
            if name == "Total Energy":
                results[self.keyt] = float(child.attrib["value"].split()[-1])
        return results


def get_energy_parsers() -> dict[str, EnergyParser]:
    """Get energy parsers."""
    d = {
        ("HF-SCF", "DF-HF-SCF", "KS-SCF", "DF-KS-SCF"): EnergyParserSCF,
        ("DF-MP2", "DF-MP2-F12"): EnergyParserMP2,
        ("CCSD", "DF-CCSD"): EnergyParserCCSD,
        ("CCSD(T)", "DF-CCSD(T)"): EnergyParserCCSDT,
        ("PNO-LMP2", "PNO-LCCSD"): EnergyParserPNO,
        ("PNO-LMP2-F12",): EnergyParserPNOLMP2F12,
        ("PNO-LCCSD(T)",): EnergyParserPNOLCCSDT,
        ("PNO-LCCSD-F12",): EnergyParserPNOLCCSDF12,
        ("PNO-LCCSD(T)-F12",): EnergyParserPNOLCCSDTF12,
        ("KSRPA", "ACFD"): EnergyParserRPA,
    }
    return {_: v for k, v in d.items() for _ in k}


def parse_input_tag(job: ET.Element) -> bool:
    """Parse "input" tag."""
    is_angstrom = False
    input_tag = job.find("input", namespaces)
    for child in input_tag:
        if child.text is not None and child.text.upper() == "ANGSTROM":
            is_angstrom = True
    return is_angstrom
