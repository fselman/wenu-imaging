# S2-05 BPM ownership baseline — 27 October 2026

Status: prepared, not native-executed. Tracking #75. Base main
`9f09a7d8a9d09c9362c390b9351c2c2d467f986c` includes accepted S2-04 and the full
S2 milestone/prior-agreement rule. Both actual user clones are clean on that
main; prior merged branches are removed and all evidence/installations retained.
No departure from the agreed S2 scope/order/coverage/exit criteria is proposed.

## Purpose, inputs and production path

This is the first bounded S2-05 measurement of unchanged `mef_build_bpm`, not
a new production repair or a declaration that all S2-05 paths are accepted.
Reuse the exact retained and controlled known-response fixture bytes, accepted
#90 driver, reference pixel hashes/counts and 0.5–1.5 thresholds. Each fixture
has three small FITS frames with one 9x18 data extension (9x9 signal and 9-column
overscan), the accepted frame list and OmegaCAM PAF. The driver trims to 9x9,
uses bias=NULL and one extension, and selects flag 0 robust / flag 1 proportional.

Each C90/C17 mode has an ASan/UBSan and separate external-leaks build. Two
fixtures times two constructors give **16 pairs / 32 native invocations** across
four private builds. An original-driver call and an observer call use separate
retained directories and identical inputs. Both run the actual cube loading,
overscan/trim, gain-map constructor, normalization/threshold and production
FITS publication path, followed by the accepted driver cleanup. No Pycavi,
calibration/science reduction, installation or original observational data is used.

## Ownership inventory to measure

- `mef_build_bpm` owns the loaded cube and releases it after the regression.
- Robust regression returns three image pointers; proportional returns two.
  The #90 conditional cleanup is already integrated. Constructor temporaries in
  `src/iproc/detector.c` and the result vector/images are part of this observation.
- The normalized gain image is released after thresholding/publication. The
  returned pixelmap belongs to the caller and the accepted driver deletes it.
- Headers, frame-list state and duplicated metadata strings in the publication
  path need measurement/source attribution. No source inspection alone certifies
  their lifetime; the baseline must expose residual state, if any.
- The caller owns the PAF context, including generated filename strings, and
  destroys it. qfits may retain header-cache entries until purge/process exit.

The new C observer includes the accepted driver byte-for-byte with its entry
point renamed. Only that driver's context constructor/destructor, build call
and returned-mask destructor references are redirected through forwarding
wrappers. Production common/Eclipse/qfits code is unchanged. Wrappers must
observe one returned context, one build, one matching mask release and one
matching context release with no surviving caller owner/mask.

Snapshots: process-start, after-context, before-build, after-build,
after-mask-release, after-context-release, after-driver, after-purge and
after-second-purge. All RAM pointer/byte, mapped-file/reference and swap fields
are recorded. Original post-driver state remains visible. The observer then
calls the existing public qfits cache purge twice; unexplained state after
either purge fails. These diagnostic calls do not alter production policy.

Actual descriptor enumeration uses the previously Mac/Linux-qualified S2-04
implementation unchanged. Count/identity must match the initial state at driver
return and after both purges, with before/after limits recorded. Missing native,
allocator, descriptor or external-leak completion is a failure, even if a
launcher exits zero. Incomplete/crashed attempts and their logs are retained.

## Numerical and resource contract

Every returned and production-saved mask must match the accepted reference
pixel hash exactly, be 9x9 unsigned 8-bit with 79 good / 2 bad pixels, preserve
0/1 polarity, extension identity and no added scaling. Retained fixture bad
positions differ from the controlled fixture: pinned reference hashes preserve
both independently. Production threshold, constructor flag and QC count headers
are checked. Original/observer saved header cards must match except generated
ORIGFILE values; those values and complete output hashes remain recorded in
provenance/logs. Staged input hashes and the complete expected file set are checked.

The runner reports functional findings separately from memory/resource findings.
It continues all declared cases to retain the baseline; a finding is not a pass.
Process-start and both purge boundaries require zero resources, descriptor
boundaries require equal count/identity, instrumented native logs must be free
of ASan/UBSan findings, and all eight external leaks summaries must be zero.
Unexplained ownership cannot be suppressed to obtain a pass. Distinct confirmed
findings are ticketed and investigated before a focused production repair.

## Preservation, preparation and remaining gates

Every new source/build/case/role directory receives provenance before workload
under `~/Software/build/wenu-imaging/mac-stage2-bpm-baseline-*`. Original and
exported sources, all fixture bytes, accepted report and protected selected
engine/configuration hashes must remain unchanged. qfits XMEMORY_MODE=2 and
XMEMORY_MAXPTRS=2000000 are retained and compared against qualified Mac controls.

Agent preparation passed Python syntax, all 11 fixture/driver manifest hashes,
eight fixture/reference checks, eight deliberately altered-pixel rejections,
unchanged qualified descriptor implementation and whitespace checks. A first
Python-only oracle setup incorrectly assumed equal bad-pixel positions for the
two fixtures; the reference assertion stopped it. That attempt is retained as
failed preparation, corrected setup passed, and neither attempt ran native code.
No native Mac or Chapman3 acceptance is claimed by these preparation checks.

Inspect returned actual Mac evidence before preparing unchanged-driver target
verification. Chapman3's compatible external diagnostic gap remains explicit.
This first fixture subset does not certify WFI, non-NULL bias, additional
extensions, error injection, repeated calls or general cache/mmap/swap behavior.
It does not waive those applicable gates. Broader #75/Stage 2 remains open;
S2-06 calibration ownership follows S2-05. Departures require prior agreement
and documentation. Early Phase 3 audit and mandatory review before Stage 2A or
component extraction remain pending. No merge, branch deletion or run cleanup
is authorized by this preparation.
