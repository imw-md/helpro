"""Data for MOLPRO."""

methods = (
    "HF",
    "MP2",
    "CCSD",
    "CCSD_T",
    "DF-HF",
    "DF-MP2",
    "DF-CCSD",
    "DF-CCSD_T",
    "DF-MP2-F12",
    "DF-CCSD-F12",
    "DF-CCSD_T-F12",
    "DF-PNO-LMP2",
    "DF-PNO-LCCSD",
    "DF-PNO-LCCSD_T",
    "DF-PNO-LMP2-F12",
    "DF-PNO-LCCSD-F12",
    "DF-PNO-LCCSD_T-F12",
)

methods_dft = (
    "KS_LDA",
    "KS_PBE",
    "KS_PBE-D2",
    "KS_PBE-D3",
    "KS_PBE-D3_BJ",
    "KS_PBE-D4",
    "DF-KS_LDA",
    "DF-KS_PBE",
    "DF-KS_PBE-D2",
    "DF-KS_PBE-D3",
    "DF-KS_PBE-D3_BJ",
    "DF-KS_PBE-D4",
)

methods_rpa = (
    "KSRPA_DIRPA",
    "KSRPA_RPAX2",
    # "KSRPA_ACFDT",
    # "KSRPA_RIRPA",  # equivalent to ACFD_RIRPA
    "ACFD_RIRPA",
    # "RPATDDFT",
)

all_methods = methods + methods_dft + methods_rpa

all_bases = (
    "cc-pVDZ",
    "cc-pVTZ",
    "cc-pVQZ",
    "cc-pV5Z",
    "cc-pV6Z",
    "heavy-aug-cc-pVDZ",
    "heavy-aug-cc-pVTZ",
    "heavy-aug-cc-pVQZ",
    "heavy-aug-cc-pV5Z",
    "heavy-aug-cc-pV6Z",
    "aug-cc-pVDZ",
    "aug-cc-pVTZ",
    "aug-cc-pVQZ",
    "aug-cc-pV5Z",
    "aug-cc-pV6Z",
)
