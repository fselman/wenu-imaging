# S2-05 supplied-bias ownership qualification — 28 October 2026

Additional agent preparation, 28 October 2026: the existing PR #115 source
`465848f493abff0a8af85f0319f96c6ec6c0d727` now passes independent Astropy
fixture/product-oracle checks (16 constructed products, 48 deliberate corruption
rejections) and C90/C17 syntax-only checks for both retained new drivers. No
production source, native driver, fixture or Mac qualification runner changed.
Actual native Mac qualification remains pending. This supplements the older
Astropy-unavailable preparation statement below; it is not native acceptance.

Status: preparation complete; actual native Mac execution pending. Baseline main
`bf1c6afe0063ae62833efd04a9109ae5a3982cef`, after merged PR #114. Fernando
reports both hosts synchronized and authorized continuing S2-05. The most recent
handoff reports a corrected DRAM ECC hardware event on Chapman3; continue Mac
work and obtain administrator/host status before resuming target workloads.
Tracking: #75; this bounded increment does not complete S2-05 or advance S2-06.

## Scope and fixed contracts

Exercise the existing non-NULL bias branch in `mef_build_bpm`, following accepted
populated-metadata qualification. Preserve production C/header/build files,
allocator mode, numerical algorithms, 0.5–1.5 thresholds, existing NULL-bias
fixtures/drivers/runners, installations and every prior evidence directory.
A distinct test driver supplies a caller-owned 9x9 bias image loaded with native
`image_load`, checks its dimensions and every pixel after the constructor returns,
and releases it exactly once. The forwarding observer retains context/mask,
descriptor, nine accounting boundaries and two controlled public cache purges.

The additive fixture helper starts with the accepted populated-metadata frames.
Only their 9x9 science region changes: add `16 + 8*y + 2*x`, with zero-based
`[y,x]=[4,5]` replaced by 4096. All additions and subtractions are exactly
representable in float32. Headers, overscan columns, padding, PAF and frame-list
bytes are preserved. A deterministic primary-image `bias.fits` stores the same
9x9 pattern. The manifest pins all six staged input hashes for each fixture kind.
This synthetic trimmed image tests supplied-bias consumption/lifetime; it does
not construct or scientifically qualify a master bias or change provenance policy.

Production path: PAF context -> `image_load` -> `mef_build_bpm` ->
`mef_cube_load` -> `mef_cube_overscan_correction` -> `cube_sub_im` ->
`cube_create_gainmap_robust` or `cube_create_gainmap_proportional` -> existing
normalization/threshold/publication -> mask/context and caller bias release.
No Pycavi function is invoked.

## Mac matrix and required result

16 ordinary/observer pairs (32 native calls): C90/C17, ASan/UBSan and separate
external-leaks lanes, retained/known-response fixtures, robust/proportional flags.
The runner checks the accepted metadata report and all its selected source
identities before exporting source and appending private, non-installed targets.
It retains production XMEMORY_MODE=2 / XMEMORY_MAXPTRS=2000000.

Required: every returned/saved mask matches all 81 accepted pixels, 79 good /
2 bad; 0/1 polarity, BITPIX=8, extension identity, geometry, scaling, thresholds,
QC and ordered canonical headers match accepted populated-metadata output exactly.
Only generated ORIGFILE timestamps are recorded separately, as in the accepted
oracle. First-frame metadata remains authoritative. Native/tool exits must pass,
the supplied bias must survive unchanged and be caller-released, and owners and
descriptors must balance. Process-start and both purge states must have zero
tracked resources; intermediate states remain visible. ASan/UBSan findings,
nonzero external leaks or missing observations fail the gate.

## Test explanation and section correspondence

The runner's section comments map to these actions:

- Host/environment/source guards: require the known Intel Mac, existing Python
  prefix, niceness >=10 and clean checkout; read actual branch/commit identity.
- Fixture/reference/control identity verification: read immutable source fixtures,
  accepted #90/metadata reports and qualified allocator/tool controls; require hashes.
- Retained provenance: create source/build/case/role manifests before workload,
  under `~/Software/build/wenu-imaging/mac-stage2-bpm-bias-*`.
- Export/private targets: export the tested commit, verify selected bytes, append
  only diagnostic CMake targets in the private copy; preserve source identities.
- Tool inventory and C90/C17 diagnostic builds: record tool versions/hashes and
  configure/build each lane; generate instrumented debug symbols on Mac.
- Supplied-bias processing: stage both deterministic fixture kinds and invoke the
  actual native driver/forwarding observer for both regression flags.
- Output, supplied-bias lifetime and metadata verification: read all actual FITS
  products with the existing Astropy oracles, compare exact masks/canonical headers
  to accepted metadata results and require the 81-pixel borrowed-bias marker.
- Resource/descriptor/double-purge/external-leak verification: inspect actual native
  log boundaries and separate leaks summary; require the stated zero/balance gates.
- Preservation and final status: verify sources/export, references, checkout,
  selected installed engine/configuration and inputs remain unchanged; retain logs,
  failed/interrupted attempts and final provenance. A launch alone is not acceptance.

## Agent preparation evidence

Python syntax for both new helpers passes. All 29 accepted metadata source/fixture
identities remain unchanged. Both derived fixture kinds stage deterministically;
all six frames recover exactly after subtraction. Headers, overscan, padding,
PAF and lists remain unchanged, and the supplied FITS pixel payload matches the
pattern. An independent NumPy proportional-fit calculation shows that omitting
subtraction changes each fixture's mask; this calculation does not exercise native
mefpp and is not its acceptance. Raw retained preparation inputs and provenance
are in `fixtures/agent-stage2-bpm-bias-preparation-2026-10-28/`.

The first sensitivity check failed because the 4096 residual was placed at [4,4],
an already-bad pixel in the known-response fixture. The failed report and staged
inputs are preserved in `fixtures/agent-stage2-bpm-bias-preparation-failed-2026-10-28/`.
Moving it to [4,5], good in both inputs, passes the same check without weakening
it. This was a rejected preparation fixture, not an observed production defect.
Astropy is unavailable in the agent environment; new native output readback and
all actual Mac diagnostics remain unexecuted. No native build/installation or
observational processing was performed in agent preparation.

## Handoff and remaining gates

Obtain fresh read-only actual-Mac Git/environment evidence before fetching or
switching to this review branch. Then synchronize by guarded fast-forward and
launch `mefpp2/tests/qualify_bpm_bias.py` with the qualified compiler, SDK and
CMake paths, existing Python prefix and `nice -n 10`. Inspect the complete run
and retain evidence before declaring any acceptance. Prepare unchanged qualified
Chapman3 verification only after Mac inspection and resolution of the host hold.
No installation or source editing on the user computer is required for this gate.

Full S2-05/#75, WFI/multiple extensions, remaining shared-helper/error/repeat/cache
coverage and compatible target external diagnostics remain open. No gate is
waived; no departure from agreed scope/order/completion criteria or S2-06 advance
is approved. Preserve all runs/archives/transfer copies/installations. No merge
or branch deletion is authorized; mandatory review precedes Stage 2A/extraction.

## Additional fixture/oracle checks — 28 October 2026

`mefpp2/tests/check_bpm_bias_preparation.py` independently reads both deterministic
fixture kinds with Astropy: exact bias pixels/type, float32 cancellation back to
the accepted science pixels, unchanged overscan, raw populated headers and padding.
The declared input hashes match the existing manifest. An independent median-ratio
calculation checks the known-good proportional sentinel at [4,5]. Robust masks
with fitted intercepts can be insensitive to additive offsets; a robust mask alone
is not evidence that subtraction occurred. No production estimator is exercised
by this Python calculation.

All 16 metadata case mappings pass constructed-product readback with the existing
`bpm_bias_cases.verify` / accepted metadata and mask oracles. Each case rejects
a deliberately changed mask pixel, first-frame metadata value and bias pixel
(48 total). Rejected bytes, restored constructed inputs/products, provenance and
source identities are retained. This checks the output oracle, not mefpp.

Both existing new C drivers pass GCC C90/C17 syntax-only checks using private
Linux platform declarations. No linking, native constructor, Mac compiler,
installation or observational processing ran. The full evidence archive and
member hashes are committed under
`fixtures/agent-stage2-bpm-bias-oracle-2026-10-28/`. All earlier preparation and
acceptance evidence remains preserved.

Fresh user preflight identifies the clean Mac checkout as
`/Users/fselman/Developer/wenu-imaging`, main at bf1c6afe, existing Python prefix
`/Users/fselman/anaconda3`. Chapman3 was also clean at bf1c6afe. Chapman4 currently
lacks the shared-home mount; Fernando will request IT repair and prefers
Chapman3 continuation. No target workload has started here; resolve the recorded
host-status obligation before later target execution. Mac qualification is next.
