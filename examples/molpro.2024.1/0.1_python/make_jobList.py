#!/usr/bin/env python
import os
from pathlib import Path

srcs = []
for root, dirs, files in os.walk("."):
    if "molpro.inp" in files and "molpro.xml" not in files:
        srcs.append(root)

srcs = sorted(srcs)

with Path("jobList").open("w", encoding="utf-8") as fd:
    for src in srcs:
        fd.write(src + "\n")
        print(src)
