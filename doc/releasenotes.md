# Release Notes

https://semver.org/

https://keepachangelog.com/

## 0.6.0 (2025-06-18)

- Added `((heavy-)aug-)cc-p(wC)VXZ(-F12)` basis sets
- Added `F12MethodOptions`
- Added examples `1.0_atoms`
- Changed `spin` to `multiplicity`
- Fixed `read_molpro_xml` for open-shell `DF-MP2-F12`

## 0.5.0 (2025-03-07)

- Added command-line `helpro`
- Added examples `0.0_basic` and `0.1_python`
- Fixed `read_molpro_xml` for `DF-CCSD-F12` and `DF-CCSD(T)-F12`

## 0.4.0 (2025-02-08)

- Added `read_molpro_xml`
- Added `counterpoise`
- Changed `write_molpro_inp` to `MolproInputWriter`

## 0.3.0 (2025-01-27)

- Added `CHARGE` and `SPIN`
- Fixed typo for `is_acfd`

## 0.2.0 (2025-01-17)

- Added `read_molpro_out`
- Added RPA with the HF reference to `write_molpro_inp`
- Changed `core` to be `str`

## 0.1.0 (2025-01-16)

- Initial release
