# OCAM EXTNAME binding repair — 4 November 2026

Issue #231, draft PR #227, branch docs/bpm-linearity-pairs-20261103.

The owner approved the two first raw biases, digital exclusion >=65534 ADU and
legacy binary BPM 1=good. Actual Mac first attempt used qualified 6e75a7b binary
SHA256 3b0dca4b0134257eda02f43df1e02b836a39196163564f5bd4f6809c23afe2bd
and corrected 8736e16 configuration. It failed at first flat binding before pixel
loads. Retain /Users/fselman/Pictures/OCAM/wenu-imaging/ccd65-raw-pairs-p0sxrc40,
including approval, device-transition record, source fingerprints, plan and logs.
Checkout/installed_files passed; final runner source checking was not reached.
No measured tables or accepted gain/RON/linearity results exist.

## Cause and bounded change

inspect_header registered EXTNAME as structural slot12 and configured identity
slot15, then rejected equal names before visiting cards. select_card stopped on
its first matching slot. The reviewed OCAM selection legitimately uses EXTNAME
as detector identity; synthetic fixtures used DETID and missed this case.

Allow only this specific alias in configuration validation. The visitor fills both
slots from the same physical card, while its existing seen bits reject a second
physical EXTNAME even when values match. Other duplicate selector options remain
rejected. Identity selectors, raw dimensions, masks, scaling and units retain
existing rules. The command now reports layout status/detail and dimension
mismatches instead of only saying Flat binding failed. No numerical code changes.
The preceding NULL-free warnings are not attributed as the cause or suppressed.

## Validation and next action

New controls reproduced both layout and OCAM-style command failures against the
unmodified source. After repair agent Linux GCC C17 passed native_layout and
native_pair_command 2/2 in1.04s. They verify unsigned16 values, independent identity
mismatch refusal, duplicate EXTNAME refusal, existing ownership/error controls,
OCAM EXTNAME/HIERARCH selectors, absent BUNIT with explicit ADU fallback and binary
1=good BPM. OCAM-style pair/bias tables exactly equal the separate-key fixture;
all immutable synthetic FITS hashes are preserved. This is preparation evidence,
not actual Mac acceptance or a real-data result.

Use the existing protected Mac qualifier with --layout-alias. It exports exact
source, builds only mefpp_pair_measure and layout_probe, checks an exact two-test
inventory and protects clean main c73d9a9e, installed files and exported source.
Default command/orchestration qualification remains available unchanged. No old
numerical test matrix is repeated. Actual Mac gate is pending. Inspect it before
one fresh CCD65 retry with the approved selections and corrected configuration.
Keep #231 open until target qualification and first real binding are verified.

The filesystem device transition is recorded separately: all31 paths changed
16777222 to16777223; all other saved stat fields matched. Earlier metadata is
retained intact. Fresh full before/after fingerprints remain required within a run.
Do not reinterpret stat agreement as an old payload-hash certificate.

No installation, production activation, fitted calibration, merge or cleanup.
