# 0.0_basic

This example shows a basic usage of MOLPRO and HELPRO on JUSTUS2 on command-line.

# Geometry

We need to first make a geometry file for a molecule (`initial.xyz` here).
A simple molecule can be generated using ASE on command-line.

- https://wiki.fysik.dtu.dk/ase/index.html

```
ase build H2O initial.xyz
```
With
```
cat initial.xyz
```
we can see the contents
```
3
Properties=species:S:1:pos:R:3 pbc="F F F"
O        0.00000000       0.00000000       0.29815450
H        0.00000000       0.76323900      -0.29815450
H        0.00000000      -0.76323900      -0.29815450
```
However, this is written in the extended-xyz format, which MOLPRO cannot read.
It is therefore necessary to convert it to the standard-xyz format as
```
ase convert -o xyz -f initial.xyz initial.xyz
```
We can see
```
3

O       0.000000000000000      0.000000000000000      0.298154500000000
H       0.000000000000000      0.763239000000000     -0.298154500000000
H       0.000000000000000     -0.763239000000000     -0.298154500000000
```
You can visualize the structure using, e.g., OVITO.

- https://www.ovito.org/

# Input

We next make a MOLPRO input file (`molpro.inp` here).
A simple MOLPRO input file can be generated using HELPRO as
```
helpro inp
```
This gives
```
GPRINT,ORBITALS
NOSYM
ANGSTROM
GEOMETRY=initial.xyz
BASIS=cc-pVDZ
{HF}
```
A more practical input file can also be generated as
```
helpro inp --method DF-PNO-LCCSD_T-F12 --basis heavy-aug-cc-pVTZ --core active
```
This gives
```
GPRINT,ORBITALS
NOSYM
ANGSTROM
GEOMETRY=initial.xyz
BASIS=aug-cc-pVTZ,H=cc-pVTZ
{DF-HF}
{DF-CABS;CORE}
{PNO-LCCSD(T)-F12;CORE}
```

# Run (local)

MOLPRO is available via the `module` command.

- https://envmodules.github.io/modules/
- https://lmod.readthedocs.io/en/latest/
- https://wiki.bwhpc.de/e/Software_Modules_Lmod

For safety, we first unload all already loaded modules.
```
module purge
```
We next load MOLPRO.
```
module load chem/molpro/2024.1.0
```
We then run MOLPRO. **(Do this way only for very small calculations!!!)**
```
molpro -m 4000 molpro.inp
```
For the above example with `HF` for `H2O`, it will finish within a few seconds.
In `molpro.out`, you see the total energy (in Ha).
```
          HF-SCF
    -76.02602772
 **********************************************************************************************************************************
 Molpro calculation terminated
 ```
 This is converted as −2068.774 eV.
 The same value is found also in `molpro.xml`.
 ```
    <property name="Energy" method="RHF" principal="true" stateSymmetry="1" stateNumber="1"
     value="-76.0260277191245"/>
```

# Run (slurm)

Running jobs on login nodes is highly **discouraged** on any supercomputers.
We therefore usually "submit" jobs to computational nodes.
This is done via a workload manager SLURM on JUSTUS2.

- https://slurm.schedmd.com/
- https://wiki.bwhpc.de/e/JUSTUS2/Jobscripts:_Running_Your_Calculations
- https://wiki.bwhpc.de/e/BwForCluster_JUSTUS_2_Slurm_HOWTO

The batch script `molpro.2024.1.0_012_384_2d.sh` for MOLPRO is in the `slurm` directory.
```
#!/usr/bin/env bash
#SBATCH -J molpro
#SBATCH --nodes=1
#SBATCH -n 12
#SBATCH --time 2-00:00:00
#SBATCH --mem=376GB
#SBATCH --gres=scratch:1024

module purge

module load chem/molpro/2024.1.0

molpro -m 4000 molpro.inp
```
This uses 12 cores in one node in parallel.
You can submit the job as follows.
```
sbatch ../slurm/molpro.2024.1.0_012_384_2d.sh
```
You need to wait until the job starts and finishes.
You can check the status, e.g., as follows.
```
squeue --format="%i %.2t %.10M %.3C %R %Z"
```
This gives, e.g.,
```
JOBID ST       TIME CPU NODELIST(REASON) WORK_DIR
16602055 PD       0:00  12 (Priority) /lustre/home/st/st_us-031401/st_ac135682/codes/helpro/examples/molpro.2024.1/0.0_basic
```
The job should provide essentially the same results as the run on a local node.

> **NOTE:**
> Although JUSTUS2 has 48 cores and, e.g., 384 GB memories per node,
> The script above distributes the 384 GB memories among 12 cores.
> This is because MOLPRO often requires a large amount of memory "per core".
> The setting above may be safe for small up to moderate sizes of molecules,
> but for some cases you might need to tune the parameters by yourself.
