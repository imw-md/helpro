# HELPRO

This is our internal software to pre- and post-process MOLPRO calculations.

## Installation

The latest version is available from GitHub.

```
pip install git+https://github.com:imw-md/helpro.git
```

If you wish to join development, you should have source codes of the package
and install it in the editable mode as

```
git clone git@github.com:imw-md/helpro.git
cd helpro
pip install -e .
```

## Usage

```
helpro inp --method HF --basis cc-pVDZ
```

```python
from helpro.molpro.inp import MolproInputWriter

miw = MolproInputWriter(method="HF", basis="cc-pVDZ")
miw.write()
```

## Author

Yuji Ikeda
