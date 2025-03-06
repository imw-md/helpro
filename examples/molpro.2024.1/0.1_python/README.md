# 0.1_python

When dealing with multiple MOLPRO calculations,
it would be more efficient to use HELPRO as a Python package, as shown in this example.

<!--
cp ~/Documents/projects/2022/CCSD_MLIP_AF/data/tblite-ase/mdn_reoriented/ChemSpider_3D/1/937/0.0/ase.xyz .
-->

Suppose we want to compute several configurations in `ase.xyz`.
Suppose further we want to compute them with several methods and several basis sets.

The directory tree for these calculations can be generated with `1.run_helpro.py`.
This script reads `methods.dat` and `bases.dat`.
`methods.dat` contains method names like
```
DF-MP2
DF-PNO-LMP2
```
`bases.dat` contains basis-set names like
```
cc-pVDZ
aug-cc-pVDZ
```
This script also consider both the `frozen` and the `active` cores.
This script also reads `ase.xyz` and prepare directories for every 20 configurations.
After running `1.run_helpro.py`, you will find a directory tree like below.
```
├── DF-MP2
│   ├── aug-cc-pVDZ
│   │   ├── active
│   │   │   ├── 00000
│   │   │   │   ├── initial.xyz
│   │   │   │   └── molpro.inp
│   │   │   ├── 00020
│   │   │   │   ├── initial.xyz
│   │   │   │   └── molpro.inp

│   │   └── frozen
│   │       ├── 00000
│   │       │   ├── initial.xyz
│   │       │   └── molpro.inp
│   │       ├── 00020
│   │       │   ├── initial.xyz
│   │       │   └── molpro.inp

│   └── cc-pVDZ
│       ├── active
│       │   ├── 00000
│       │   │   ├── initial.xyz
│       │   │   └── molpro.inp
│       │   ├── 00020
│       │   │   ├── initial.xyz
│       │   │   └── molpro.inp

│       └── frozen
│           ├── 00000
│           │   ├── initial.xyz
│           │   └── molpro.inp
│           ├── 00020
│           │   ├── initial.xyz
│           │   └── molpro.inp

├── DF-PNO-LMP2
│   ├── aug-cc-pVDZ
│   │   ├── active
│   │   │   ├── 00000
│   │   │   │   ├── initial.xyz
│   │   │   │   └── molpro.inp
│   │   │   ├── 00020
│   │   │   │   ├── initial.xyz
│   │   │   │   └── molpro.inp

│   │   └── frozen
│   │       ├── 00000
│   │       │   ├── initial.xyz
│   │       │   └── molpro.inp
│   │       ├── 00020
│   │       │   ├── initial.xyz
│   │       │   └── molpro.inp

│   └── cc-pVDZ
│       ├── active
│       │   ├── 00000
│       │   │   ├── initial.xyz
│       │   │   └── molpro.inp
│       │   ├── 00020
│       │   │   ├── initial.xyz
│       │   │   └── molpro.inp

│       └── frozen
│           ├── 00000
│           │   ├── initial.xyz
│           │   └── molpro.inp
│           ├── 00020
│           │   ├── initial.xyz
│           │   └── molpro.inp

```
We then collect directories where the calculations are not run using `make_job_list.py`.
This makes a `jobList` file.
```
./DF-MP2/aug-cc-pVDZ/active/00000
./DF-MP2/aug-cc-pVDZ/active/00020
./DF-MP2/aug-cc-pVDZ/active/00040
./DF-MP2/aug-cc-pVDZ/active/00060
./DF-MP2/aug-cc-pVDZ/active/00080
./DF-MP2/aug-cc-pVDZ/active/00100
./DF-MP2/aug-cc-pVDZ/frozen/00000
./DF-MP2/aug-cc-pVDZ/frozen/00020
./DF-MP2/aug-cc-pVDZ/frozen/00040
./DF-MP2/aug-cc-pVDZ/frozen/00060
./DF-MP2/aug-cc-pVDZ/frozen/00080
./DF-MP2/aug-cc-pVDZ/frozen/00100
./DF-MP2/cc-pVDZ/active/00000
./DF-MP2/cc-pVDZ/active/00020
./DF-MP2/cc-pVDZ/active/00040
./DF-MP2/cc-pVDZ/active/00060
./DF-MP2/cc-pVDZ/active/00080
./DF-MP2/cc-pVDZ/active/00100
./DF-MP2/cc-pVDZ/frozen/00000
./DF-MP2/cc-pVDZ/frozen/00020
./DF-MP2/cc-pVDZ/frozen/00040
./DF-MP2/cc-pVDZ/frozen/00060
./DF-MP2/cc-pVDZ/frozen/00080
./DF-MP2/cc-pVDZ/frozen/00100
./DF-PNO-LMP2/aug-cc-pVDZ/active/00000
./DF-PNO-LMP2/aug-cc-pVDZ/active/00020
./DF-PNO-LMP2/aug-cc-pVDZ/active/00040
./DF-PNO-LMP2/aug-cc-pVDZ/active/00060
./DF-PNO-LMP2/aug-cc-pVDZ/active/00080
./DF-PNO-LMP2/aug-cc-pVDZ/active/00100
./DF-PNO-LMP2/aug-cc-pVDZ/frozen/00000
./DF-PNO-LMP2/aug-cc-pVDZ/frozen/00020
./DF-PNO-LMP2/aug-cc-pVDZ/frozen/00040
./DF-PNO-LMP2/aug-cc-pVDZ/frozen/00060
./DF-PNO-LMP2/aug-cc-pVDZ/frozen/00080
./DF-PNO-LMP2/aug-cc-pVDZ/frozen/00100
./DF-PNO-LMP2/cc-pVDZ/active/00000
./DF-PNO-LMP2/cc-pVDZ/active/00020
./DF-PNO-LMP2/cc-pVDZ/active/00040
./DF-PNO-LMP2/cc-pVDZ/active/00060
./DF-PNO-LMP2/cc-pVDZ/active/00080
./DF-PNO-LMP2/cc-pVDZ/active/00100
./DF-PNO-LMP2/cc-pVDZ/frozen/00000
./DF-PNO-LMP2/cc-pVDZ/frozen/00020
./DF-PNO-LMP2/cc-pVDZ/frozen/00040
./DF-PNO-LMP2/cc-pVDZ/frozen/00060
./DF-PNO-LMP2/cc-pVDZ/frozen/00080
./DF-PNO-LMP2/cc-pVDZ/frozen/00100
```
To run the calculations efficiently, we use `submit.py` in the `bin` directory.
This reads the directories in `jobList`, visits each directory written in `jobList`,
and submit a certain job script.

For later convenience, we put this script close to the home directory.
```
mkdir -p ~/bin
cp -p ../../bin/submit.py ~/bin
```

We then run `submit.py` as below.
```
~/bin/submit.py ~/slurm/molpro.2024.1.0_012_384_2d.sh
```
This submits the MOLPRO job for each directory in `jobList`.

Once all the calculations are finished, we need to collect the results.
This will be done in the `energies` directory.
