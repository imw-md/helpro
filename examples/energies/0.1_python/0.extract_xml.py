#!/usr/bin/env python
"""Extract results."""

import os
from pathlib import Path

import pandas as pd

from helpro.molpro.bases import bases_all
from helpro.molpro.xml import read_molpro_xml

top = Path("../../molpro.2024.1_finished/0.1_python").resolve()


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    """Format ``pd.DataFrame``."""
    for k in df.columns:
        if k == "name":
            df[k] = df[k].str.pad(28)
        elif df[k].dtype == "category":
            df[k] = df[k].str.pad(20)
        elif df[k].dtype == int:
            df[k] = df[k].astype(str).str.pad(4)
        elif df[k].dtype == bool:
            df[k] = df[k].astype(str).str.pad(6)
        elif df[k].dtype == object:
            df[k] = df[k].str.pad(20)
    return df


def collect() -> pd.DataFrame:
    """Collect data."""
    ds = []
    for root, dirs, files in os.walk(top):
        if "molpro.xml" not in files:
            continue
        filename = top / root / "molpro.out"
        print(filename)
        atoms = read_molpro_xml(filename)
        results = atoms.calc.results
        energy = results.get("energy", float("nan"))
        results.pop("free_energy", None)
        results.pop("correlation_energy", None)
        d = {
            "method": root.split(os.sep)[-4],
            "basis": root.split(os.sep)[-3],
            "core": root.split(os.sep)[-2],
            "i": int(root.split(os.sep)[-1]),
            "energy": energy,
        }
        ds.append(d)

    return pd.DataFrame(ds)


def main() -> None:
    """Command."""
    df = collect()
    df["basis"] = pd.Categorical(df["basis"], categories=bases_all, ordered=True)
    df = df.sort_values(["method", "basis", "core", "i"])
    df = format_df(df)
    na_rep = 16 * " "
    filename = "energies_xml.csv"
    df.to_csv(filename, na_rep=na_rep, float_format="%16.9f", index=False)


if __name__ == "__main__":
    main()
