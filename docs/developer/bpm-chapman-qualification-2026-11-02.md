# Changed-code BPM qualification on Chapman4

## Mac basis and purpose

Actual Mac revision 022cf3683fe47d4de6a7acac1e3799cb49201d40 passed
native_bias_files and native_bpm_completion in 18.63 s (5.24/13.38 s).
Retained `/Users/fselman/Software/build/wenu-imaging/mac-bpm-complete-Ia5qliwa`.
All four preservation checks passed; main remained clean. Earlier component
receipts remain retained. This qualifies synthetic whole-command completion on
the Mac, not actual data or the Chapman implementation.

The owner authorized proceeding to Chapman validation before actual WFI/OmegaCAM
calibrations. Actual Chapman execution is pending. Runner/docs additions do not
change the Mac-tested native/build/QC component trees: the runner compares their
Git object identities against the exact Mac revision before starting work.
No unchanged Mac replay is needed.

## Selected environment and preserved checkout

Use the selected GCC10.2.1/C17, CMake/CTest3.29.6, make/ar/ranlib paths in
[selected tools](selected-tools.md), imaging Python
`/home/fselman/.conda/envs/wenu-imaging/bin/python`, actual Chapman4/glibc2.17.
ASDF work uses the retained qualified interpreter at:
`/home1/fselman/Software/build/wenu-imaging/chapman4-asdf6-download-crhlZBOC/D2-private-s6qsxbqf/environment/bin/python`.

The latest returned Chapman checkout was the clean bias branch
`feat/m5-bias-template-20261102` at
`07d27330555712ef6bf59a068a578b450e89b4a3`, tracking its HTTPS origin. The new
runner protects that exact state. Fetch the new BPM source and export it into a
fresh retained run; do not switch, pull, merge or install into this checkout.
If its state differs, stop and inspect the returned guard failure.

Reuse the passed Chapman report at
`/home1/fselman/Software/build/wenu-imaging/chapman-m5-asdf16-resume-U4vTGDyf/chapman-qualification.json`.
The runner validates its exact prior revision/platform, passed status, six
preservation flags, ten successful shared-QC controls and interchange result.
It verifies historical QC bytes against their old export and Git, records old/current
source digests, tests the current shared QC module, and checks retained
ASDF6.0.0/asdf-standard1.5.0/NumPy1.26.4/
Astropy6.1.7 identities. No Conda solve/install, interpreter activation, dependency
upgrade, external C interchange replay or private normal-runtime installation.
The new BPM recipe does not link the C ASDF library. The external prefix remains
preserved and its earlier bounded qualification remains retained.

## Single changed-code gate

Purpose: exercise the code added since the previous Chapman bias/ASDF receipt
under real CentOS7/glibc2.17/GCC10 limits. Inputs are generated tiny images only.
Actions: fresh source export and optimized C17 build (two jobs), twelve selected
contracts serially, using the retained ASDF interpreter for sidecars. Niceness
>=10 and one OpenMP/BLAS thread. Pass requires exact test inventory, all tests
successful and every preservation check true.

| Contracts | Changed behavior covered |
| --- | --- |
| native_measurement_stats, native_eclipse_allocation | Mask-aware standard deviation/MAD and affected allocation cleanup |
| native_bias_service, native_bias_files, native_bias_qc_asdf | Updated bias numerical/file/QC composition and shared command regression |
| native_layout | Active/raw mask loading and explicit selected-detector layout |
| native_bpm_response, native_bpm_service, native_bpm_files | Reused Eclipse response fit, byte reasons, service ownership and bound admission |
| native_bpm_publication, native_bpm_completion | Checked integer FITS, prior/coverage preservation, common ASDF and complete-command boundaries |
| shared_qc_asdf | Current ten shared-QC checks, including added owned-extension lifecycle and bias/MAD quantities |

The current ten shared-QC checks run as one CTest entry because their module/test
source changed since the previous Chapman receipt. Standalone C/Python interchange
and the previous normal installation gate are not repeated. Neither C90 nor a second Chapman host
is included. User-confirmed shared tools are selected directly, not rediscovered
or requalified.

The report is `chapman-bpm-qualification.json`, with separate stdout/stderr per
command, source archive identity, old-receipt identity, package versions and exact
test inventory. Build/test progress prints every 30 seconds. Errors retain the
run and report; no automatic fallback or retry. No claim of success before the
owner returns the actual log/report.

## Preservation and acceptance boundary

Compare before/after: clean checkout, configured installed files, production
Python package metadata, retained ASDF prefix, retained external C-library prefix,
exported source and prior receipt bytes. No bytecode creation in retained prefixes.
No source edits, package installation or production activation. Guard preparation
on the agent passed three stdlib controls (wrong-host rejection before work,
exact inventory, passed/protected prior-receipt requirement) in 0.001 s, plus
syntax/whitespace checks. These do not establish target execution.

After actual Chapman success, inventory/select the real calibration sequences
and review the invocation before scientific acceptance. The BPM command currently
uses a selected active master bias; it does not construct it from raw biases.
Full gain/RON/linearity and the shared signed shutter model remain pending.
The formula PDF/LaTeX and initial CCD-style CMOS policy are unchanged. No real
observational/scientific acceptance, installation, activation or merge follows
from a synthetic pass alone.

## First BPM attempt and corrected QC source boundary

Owner-returned b6b5fea26b3e271e8bb25465732f4ab9d8f9aa2e attempt:
`/home1/fselman/Software/build/wenu-imaging/chapman-bpm-complete-h64m4l9x`.
The prior-source equality guard stopped before source export, build or tests.
No installation was attempted. The early stop did not produce a formal final
preservation report; retain this directory and traceback.

Review against the actual previous4417d7d revision shows unchanged schema but
changed pycavi_qc.py: owned recipe extensions, bias-stage metric names and MAD RON
pair validation. test_shared_qc.py gained extension ownership/sealing checks.
These are already in the Mac-qualified source; the runner incorrectly attempted
to reuse older Chapman source acceptance. The correction preserves dependency
reuse while recording source differences and selecting shared_qc_asdf explicitly.
The old export must still match its own historical source; changed current source
is not rejected or falsely called previously qualified.

Corrected preparation passed four stdlib guard controls in0.001s and all ten
current shared-QC checks on the agent in0.449s, with no network attempts. These
are not Chapman acceptance. Native/build/QC sources remain identical to the
Mac-qualified revision; only runner, guard tests and documentation change. Retry
once in a fresh retained directory; expected12/12 CTest entries and all seven
preservation checks. No Conda/dependency installation or C-library replay.
