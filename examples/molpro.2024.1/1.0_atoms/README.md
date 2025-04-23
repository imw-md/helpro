# 1.0_atoms

Suppose we want to obtain free-atom energies with various charges and multiplicities
to compute, e.g., atomization energies of molecules.
We want to compare energies among various multiplicities and would like to take the one
with the lowest energy.

This can be done using a Python script like `1.run_helpro.py`.
This script reads `methods.dat` and `bases.dat`, like `1.0_python`, and also consider
both the `frozen` and the `active` cores.
In addition, there are loops for elements (atomic numbers), charges, and multiplicities.
After running `1.run_helpro.py`, you will find a directory tree like below.
```
.
├── 1
│   ├── DF-HF
│   │   └── cc-pVDZ
│   │       ├── active
│   │       │   ├── c+0
│   │       │   │   ├── m+2
│   │       │   │   │   ├── initial.xyz
│   │       │   │   │   └── molpro.inp
│   │       │   │   └── m+4
│   │       │   │       ├── initial.xyz
│   │       │   │       └── molpro.inp
│   │       │   ├── c+1
│   │       │   │   ├── m+1
│   │       │   │   │   ├── initial.xyz
│   │       │   │   │   └── molpro.inp
│   │       │   │   ├── m+3
│   │       │   │   │   ├── initial.xyz
│   │       │   │   │   └── molpro.inp
│   │       │   │   └── m+5
│   │       │   │       ├── initial.xyz
│   │       │   │       └── molpro.inp
│   │       │   └── c-1
│   │       │       ├── m+1
│   │       │       │   ├── initial.xyz
│   │       │       │   └── molpro.inp
│   │       │       ├── m+3
│   │       │       │   ├── initial.xyz
│   │       │       │   └── molpro.inp
│   │       │       └── m+5
│   │       │           ├── initial.xyz
│   │       │           └── molpro.inp

```

> **NOTE:**
> The multiplicity is defined as 2<i>S</i>+1,
> where <i>S</i> is the total spin angular momentum.
> https://en.wikipedia.org/wiki/Multiplicity_(chemistry)
> On the other hand, the `SPIN` in the MOLPRO `WF` directive is 2<i>S</i>.
> https://www.molpro.net/manual/doku.php?id=the_scf_program&s[]=scf

Once the directory tree is made, MOLPRO calculations can be submitted in a similar way
to `0.1_python`.

Once all the calculations are finished, we can do a post-processing as shown in
`energies/1.0_atoms`.
