# M4 raw-preparation helper receipt — 31 October 2026

Owner-authorized addition to [M4 review #182](https://github.com/fselman/wenu-imaging/issues/182):
review ESO DPR classification and add a guide plus dataset-specific Python
preparation with light checks. [#184](https://github.com/fselman/wenu-imaging/issues/184)
tracks the helper; [PR #183](https://github.com/fselman/wenu-imaging/pull/183)
retains the M4 interface/fixture review and this explicit addition. Baseline review
head: `0e0739f56053a09763804101401a4c6c6b89b660`.

## Delivered scope

- [User guide](../data-preparation.md): reviewed ESO-044156 v8 section 4.4.2.1,
  Tables 9–11 and raw/processed metadata boundary; official ZWO ASI1600 manual
  rev1.5 sections 2/4/6.6; mapping and light-check limits, plan/copy protocol,
  checksum handling and calibration unknowns.
- [Checkout helper](../../Pycavi2/tools/prepare_zwo_bath.py): `role_for`,
  `raw_header`, `inspect`, `inventory`, `apply_plan`, `copy_prepared` and thin CLI.
  Header-only plan inspects all discovered candidates, refusing unknown/conflicting
  inputs; explicit exact-plan apply writes new copies, never updates originals.
  Known flat Light labels need acknowledgement, not silent replacement. Copies
  preserve original nonchecksum cards and complete opaque payload bytes; report
  input/output/payload SHA256 and remove stale primary CHECKSUM/DATASUM from copies.
- No Pycavi processing routines, mefpp/Eclipse/qfits services, C/header files,
  numerical algorithms, installed environments, calibration association or
  observational pixels are exercised/changed by this implementation.

## Agent evidence

[Retained logs/provenance](fixtures/agent-m4-preparation-2026-10-31/README.md).
Existing private agent Python 3.12.14, Astropy 6.1.7, NumPy 1.26.4; no package
installation or upgrade. Nine synthetic groups pass initially in 3.179 s and
after structural-type/compressed-input refusal additions in 0.834 s. Final source
hashes are recorded separately; no exact initial source hash is claimed.

The [test helper](../../Pycavi2/tests/test_zwo_bath_preparation.py) calls the actual
preparation functions and uses sparse synthetic full-shape FITS, not Bath data:

| Control | Verified behavior |
|---|---|
| Roles/metadata | Bias/dark/four lights/four flats produce declared classifications without source writes |
| Copies/scaling | Original source bytes and nonchecksum cards remain exact; payload remains exact; independent Astropy section reads decode 0/32767/65535 correctly |
| Flat conflict | No output before explicit acknowledgement; original Light labels remain, identical DPR not duplicated |
| DPR ambiguity | Existing conflicting/duplicate/alias cards block preparation |
| Light-check failures | Wrong camera/geometry, missing gain/temperature, filter/exposure/type conflicts and Bayer metadata block |
| Stale plans | Wrong report hash or changed source rejects before output creation |
| Unfamiliar files | Unknown directory, symlink, extra payload/HDU and compressed FITS block the batch |
| Header growth/failure | Additional header block preserves data; injected copy I/O failure retains incomplete marker |
| Destinations | Report/copy paths inside inputs rejected; existing output not overwritten |

The synthetic alias input intentionally triggers an Astropy VerifyWarning, and
the source-report protection control prints an expected STOP message. Neither is
an observed Bath defect. Original failed-target evidence is not replaced; no
native/scientific qualification or new defect correction is claimed here.

## Pending actual-target qualification

First inspect the actual Mac checkout/environment, fetch a verified private
source export without changing main, then use the selected Python for the full
Bath `plan`. Retain JSON/digest and inspect every error/warning/classification
count. This should cover the four earlier uninspected FITS if the dataset remains
the same; do not claim a count before receiving results.

After the plan is reviewed, qualify the helper and selected prepared copies on
actual Mac with explicit original/copy/payload checks before any broad copy or
pipeline admission. Representative Chapman helper controls should use the same
bounded synthetic contract if it is to be used there; the Bath dataset is not
assumed present on Chapman. No existing qualification suite replay or native
build/install is required merely to review this guide/helper.

M4 detector/layout runtime work, no-scan calibration services, physical gain/noise,
dark applicability, M6a variance and later association remain separate. DPR
classification is a raw admission requirement, not proof of scientific readiness.
