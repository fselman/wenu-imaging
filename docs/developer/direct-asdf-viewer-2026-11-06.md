# Direct corrected-ASDF viewer, 6 November 2026

Prepared against b3c2bd854b555633e07457c2c58d06f1bd4f8fe6; refs #243/#235.
Owner authorized retaining 96 products and preparing the viewer first; recipe
design is deferred. [Design](design/direct-asdf-viewer-v1.md).

## Result

`tools/view-pair-qc.py --preparation-batch ... --diagnostics ... --ratios ...`
now uses `pycavi_viewer_data.DisplayReader`. It admits the completed preparation
index and receipt without opening all preparation products for a preliminary
pass. Each selected ASDF then goes through the unchanged common reader once.

The viewer selects saved corrected rows, raw-pair gain/RON, stored line and
ratio diagnostics. It checks selectors, units, stages, index digests, common
measurements, row populations and the immediate links between selected products.
It does not follow their copied calibration trees or replay native transports.
The existing deep audit readers, numerical services and publishers are unchanged.
The legacy raw viewer path remains available with its existing deep checks.

Rendering no longer deep-copies the complete payload. HTML/JSON use compact
serialization. Existing HTML geometry, plots, units, shared axes/cursor and
scientific definitions are retained. No new scientific arithmetic is introduced.
The direct ratio path requires the separately selected line index as well.

Console output identifies each file before reading and reports elapsed load
time after decoding, then announces rendering/writing and the final selected
input fingerprint check. `viewer.json` records the validation scope, decoded
product count, per-product decode/load timings, render/write and total time.
The receipt explicitly says calibration ancestry was not reaudited. ASDF bytes
and small display inputs are fingerprinted; no calibration-history/runtime-wide
hash campaign is performed. The final byte check does not decode ASDF again.

## Agent verification

- Eight injected-common-record Python controls passed in 0.529 s. These test
  selection, exact saved values, digest/stage/unit/common-value/source/sample
  refusal, metadata admission, mosaic integration and progress. The 32-detector
  control called the common reader exactly 96 times with graph/compute readers
  patched to fail. This is not an ASDF throughput benchmark.
- The actual corrected-viewer JavaScript DOM harness passed on generated HTML:
  saved corrected/raw metric values, residual/ratio values, units, stage labels
  and shared axes. This does not verify browser painting.
- `git diff --check` passed.

This workspace has no ASDF dependency. Automated approval review rejected an
attempted private dependency installation under the project's no-install policy;
no successful ASDF installation or real-ASDF test is claimed. Continue with the
retained target runtime; do not provision a replacement or replay old gates.

## Next actual Mac step

First obtain fresh read-only host/checkout/origin/branch/status/interpreter
evidence, then fetch the review branch explicitly. Keep actual clean main and
installations unchanged. Export the exact reviewed commit once into a retained
task directory under `/Users/fselman/Software/build/wenu-imaging` and run:

```sh
# Direct reader and independent real-ASDF equivalence controls (nine tests).
"$private_python" -B "$source/Pycavi2/tests/test_direct_viewer.py" --asdf --work "$checks"
```

`--asdf` adds one test using the existing corrected fixture, publication services
and independent deep readers as a reference. It compares the entire selected
measurement/provenance/diagnostic content, then instruments the direct reader
to require exactly three common reads, no traversal and no numerical calls.
Only synthetic support data are created. This check has not run in the agent
workspace. Use the retained private interpreter:

`/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python`.

After reviewing that result, generate the viewer from the retained real products
with the same interpreter and new source. Inputs:

- Preparation: `/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-roi-batch-NrHHb3bT`.
- Lines: `/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-diagnostics-i92m_n1n/lines/index.json`.
- Ratios: `/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-diagnostics-i92m_n1n/ratios/index.json`.

Use an explicit fresh empty inspection destination; never reuse the stopped
`inspection` directory. Review the console and `viewer.json` for 96 decoded
ASDF products, 32 available detectors, 3200 signal rows and 640 ratio rows, then
open `qc-mosaic.html` for owner inspection. No actual speedup, corrected browser
inspection or scientific acceptance is claimed yet. Do not rerun preparation,
diagnostic computation, old qualification matrices, installation or cleanup.
