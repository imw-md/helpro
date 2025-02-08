#!/usr/bin/env python
"""List structures in `structures.dat`."""

import os
from pathlib import Path

import numpy as np

home = Path.home()
parent = home / "codes/refdata/20_s66x8"

names = []
for file in parent.iterdir():
    *name, distance = os.path.split(file)[-1].split("_")
    names.append("_".join(name))
names = np.unique(names)
np.savetxt("structures.dat", names, fmt="%s")
