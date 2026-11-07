# Bias recipe and cross-product QC handoff — resume 7 November 2026

Saved at the end of 6 November 2026, America/Santiago. Owner requested saving
state and continuing tomorrow. Start here; do not replay completed reductions,
qualification matrices, builds or viewer generation.

## Start next session

The next task is discussion of bias/calibration QC inspection. The owner needs
time to think about the broader viewer. No new viewer design, implementation,
QC collection format, database or historical-data harvesting has been approved
by this handoff. Do not start those merely because an earlier next-step list
proposed a viewer. For the immediate purpose, inspecting and comparing the
existing product parameters using the suggested table/mosaic/input-detail views
is an acceptable starting point; confirm the concrete scope in the discussion.

## Owner's QC direction

The linearity viewer follows an experiment and is not the general model for
biases, flats and other recipes. For calibration QC:

- Display all stored QC parameters of all relevant products in a recipe's
  product directory, for example cal/bias, rather than only one selected file.
- Compare each product with other project products and, eventually, a database
  of historical measurements which does not yet exist.
- Plot the chosen QC parameters versus JD. A product selector highlights that
  product's measurements with a different symbol in the same comparison plot.
- Harvest each product's parameters once. Selection and plotting reuse the
  harvested measurements instead of repeatedly reading/harvesting files.
- A separate QC collection directory, and eventually a database, are possibilities
  for discussion, not selected implementations or new dependencies.
- Keep harvesting, comparison/plot preparation and product inspection distinct;
  reuse existing plotting components where useful. Preserve measurement units,
  detector/input identities, methods, masks, availability and provenance.

Pending scientific/design decisions include the measurement epoch used for JD
for a combined product, representation of all parameters/arrays, and criteria
for comparing measurements with different definitions or mask policies. Product
creation time must not silently become detector measurement time.

The immediate comparison can use the two retained bias FITS/ASDF pairs below.
Their detector pixels are identical and they share the same ten raw exposures;
they are a consistency comparison, not independent historical detector samples.
Do not mistake the newer creation timestamp for a new acquisition epoch.

## Repository integration and cleanup complete

GitHub main and the actual Mac checkout are at:

    b1f2f50960d64fd17bc1c03fa2bbd70fc9ae1769

Tree:

    addc54a8babb01e80a70540f87b669a352de4eb7

PRs 227, 244, 246, 248, 250, 254, 266, 271, 274 and 275 were merged in dependency
order. Final main exactly equals reviewed head f5b87baadcb63adefb8052e9b56606d81a4a3af5
in file content, and contains every reviewed head as an ancestor. GitHub reported
no review threads, CI status checks or workflow runs; actual Mac qualification
receipts supplied the relevant acceptance evidence, not an invented CI pass.

Actual Mac host: MC02VV0HPHTDG. Checkout:

    /Users/fselman/Developer/wenu-imaging

Origin fetch/push: git@github.com:fselman/wenu-imaging.git. Owner returned clean
main tracking origin/main after guarded fast-forward. All ten merged remote
review branches were deleted atomically with exact-tip leases and ancestry
checks; unrelated branches were preserved. Returned cleanup transcript:
Pasted text(20261107-001511).txt, Library ID libfile_b88e25b483f48191a3313dc2b9d51c7a.
Do not repeat the integration or branch deletion. This new handoff branch is
separate documentation and does not imply a new Mac synchronization.

## Selected executable: relink and smoke check complete

Use the existing mutable source/build pair under:

    /Users/fselman/Software/build/wenu-imaging/mac-standalone-bias-SP3Cgdhb

Source: scalar-qc-c17-source. Build: scalar-qc-qualification-c17/build.
Recipe: build/mefpp2/mefpp_bias_recipe under that qualification directory.
The executable now includes the qualified optional-cleanup correction and
is stamped with merged revision b1f2f50960d64fd17bc1c03fa2bbd70fc9ae1769.

Executable SHA256:

    4fc47f0e33e379864e4850f10ae78f12a22e0b15dce874cc8e23c606b8422e46

All 397 checked production source/build inputs matched merged main. Only
MEFPP_SOURCE_REVISION:STRING changed in the existing cache. No source copying,
new build tree, dependency rebuild or installation occurred. Old executable
SHA256 0bc23761e26754915662375e4f4d804eded1eecfeedb56d2a5e5da3db0fe4984
and the pre-relink cache were retained in recipe-relink-main-b1f2f509.

Pinned tools/settings: /opt/local/bin/cmake; Xcode clang at
/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang;
/usr/bin/make; Unix Makefiles; Release; MEFPP_C_STANDARD=17; SDK
/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX14.2.sdk.
Native libasdf prefix remains
/Users/fselman/Software/build/wenu-imaging/mac-asdf16-streams-o8KPDcUm/libasdf-environment.
No routine reconfiguration or tool substitution. Compiler cache storage type
is STRING, not FILEPATH; check name/value independently of cache type while
preserving the full typed-cache audit. Guard defect #277 is verified closed.

Receipts under scalar-qc-qualification-c17:

- recipe-relink-main-b1f2f509/relink.json — targeted recipe build passed with
  no warnings; old binary/cache retained.
- recipe-relink-main-b1f2f509/smoke/smoke-results.json — one actual native
  two-detector TOML recipe with BPM/MAD/RON explicitly omitted passed in
  3.427 seconds. Existing tiny synthetic raw fixtures and reference products
  were reused. Exact FITS pixels/QC, shared scalar/context mapping, independent
  ASDF validation and producer revision passed. No allocator diagnostics.
  Fixture, cache, executable and main checkout preservation checks passed.
- optional-cleanup-results.json — earlier component cleanup and four in-memory
  BPM/MAD/RON profiles passed at b8ca41f; no need to repeat them.

No observational raw files were accessed by relink/smoke. Installed software and
previous observational products remain unchanged. The retained uninstalled
recipe candidate is ready for future explicitly requested use; this is not
installation, another platform qualification or a new observational reduction.

Use explicit Python interpreters. Astropy:
/Users/fselman/anaconda3/envs/wenu-imaging/bin/python.
Qualified ASDF 6 runtime (retain invoked venv path, not resolved symlink):
/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python.
Default shell Python is base Conda 3.11.7; do not substitute it for these readers.

## Retained real bias products and inputs

Raw, untouched:

    /Users/fselman/Pictures/OCAM/bpm

Ten ordered OMEGA bias frames from 2017-03-13, 09:50:05.624 through 09:56:31.804.
Orchestration:

    /Users/fselman/Pictures/OCAM/test_recipes/orchestration

Reduced products:

    /Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias

Original completed stem: CMDP.2026-11-06T19:22:15.014Z.001.
Expanded scalar-header/recovered stem: CMDP.2026-11-06T21:42:22.830Z.001.
Each has FITS, ASDF and log. Preserve both pairs, failed log, private detector
products and recovery/qualification receipts. Do not overwrite or remove them.

The newer FITS is 1,077,825,600 bytes. All 32 detector pixel payloads match the
original byte for byte. All 864 legacy QC keyword groups match retained
references exactly. All 89,445 new scalar/context cards agree with original QC;
complete recovered ASDF schema, values, array/float bits and provenance were
independently checked. Five extra reason cards explain the per-extension count
variation. Native recovery reused verified original measurements and explicitly
records the original recipe failure; do not claim uninterrupted recipe success.
Recovery receipt: orchestration/bias-scalar-qc-asdf-recovery.json.

## Header/QC facts already checked

Owner read both actual primary headers: PRODCATG='CALIB.MASTER_BIAS';
ESO PRO CATG absent. Leave them unchanged, as explicitly requested. Phase 3
uses PRODCATG, distinct from the ESO pipeline HIERARCH ESO PRO CATG convention;
this does not establish full Phase 3 compliance or validate every category.
Two inherited lowercase-exponent telemetry cards are byte-identical to raw;
strict FITS conformance remains separate from structure/QC agreement.

Newer product: each detector extension has HIERARCH ESO MPP QC RON STD and
HIERARCH ESO MPP QC RON MAD, corresponding to ASDF measurement names read_noise
and read_noise.mad. Both are ADU, from the selected original raw-frame pair
before scan correction, with the difference scatter divided by sqrt(2).
The first two ordered raws were selected explicitly. The older product has
these quantities in ASDF but predates their addition to FITS headers.
The new FITS/ASDF mapping was verified across all 32 detectors.

Do not confuse detector single-exposure RON with master spatial scatter or
master uncertainty. No master variance/covariance plane is supplied. Repeated
RON-MAD near 2.0967 ADU can result from a raw-difference MAD of 2; it is not
proof of identical detector noise. High-offset counts are bias-offset
measurements, not dark-current measurements.

Preserve agreed numerical conventions: detector BPM selects active statistics
and frame means, never electronic scan samples; temporal median preserves
Eclipse lower-middle convention for even stacks; checked QC median averages
the central pair. Legacy master median/stdev with a supplied BPM are masked
checked values cast to float, not inherently unmasked. Explicit master_unmasked
is separate. Frame selection retains STRICTLY L < mean < U; equality is
rejected, and a zero-width band fails the minimum-survivor check. Guide wording
was corrected in both LaTeX/PDF; #276 is merged and closed.

Five detector/input exclusions in this dataset: CCD74/raw-000003,
CCD84/raw-000008, CCD69/raw-000000, CCD77/raw-000004, CCD85/raw-000007.
Other detectors used all ten frames. Input scan QC still includes rejected
frames. Existing FITS QC remains; new scalar diagnostics are in both formats;
arrays/full ancestry remain in ASDF. The common QC record is the source of both
serializations. Do not fabricate missing measurements as numeric zero.

## Documentation and tracking

Accepted guide: docs/developer/bias-recipe-mathematical-guide-v1.tex and .pdf.
Requested block diagram and editable source:
docs/developer/architecture/mefpp/bias-recipe.svg and .dot; accompanying README
links source boundaries and explains normal operation versus explicit recovery.
The diagram and corrected guide are already in merged main.

Overall recipe tracker #245 retains integration, actual Mac sync/cleanup and
relink/smoke completion comments; broader viewer/platform scope is not closed.
External native file-backed ASDF lookup limitation #267 and other independently
tracked issues are not resolved merely by this handoff. The qualified writer
uses its bounded memory-backed readback workaround; keep that behavior.

At resume, read this handoff and obtain fresh Mac state only before a required
local change. No new build, dependency inventory, raw hashing campaign,
observation processing, reference regeneration or viewer launch is needed to
resume the design discussion. This saved-state PR itself is documentation only.
