# 0.1_python

Suppose you have finished the calculations in `molpro.2024.1/0.1_python`.
It is inefficient and error-prone to fetch the results by hand.

`0.extract_out.py` (or `0.extract_xml.py`) does this job.
It prints `energies_out.csv` (or `energies_xml.csv`).

Both `0.extract_out.py` and `0.extract_xml.py` should give essentially the same results.
If not, there may be a bug in the parsers.
It is therefore encouraged to do both and cross-check.

The generated `energies_out.csv` (or `energies_xml.csv`) can be used for comparison
among the investigated methods and basis sets.
For example, the results can be plotted using `seaborn` in `1.plot.py`.
