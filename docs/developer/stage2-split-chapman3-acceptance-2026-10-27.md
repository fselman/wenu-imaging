# S2-04 Chapman3 split/cache acceptance — 27 October 2026

## Actual target verification

Clean branch `test/stage2-split-ownership`, source
`7ef74b72f107be5a4f87aa24b31b3fe4de747ef0`, Linux Chapman3, GCC 10.2.1 and
CMake 3.29.6. Both uninstrumented C90/C17 builds complete all ten variants for
OmegaCAM/WFI: **40 ordinary/observer pairs, 80 native invocations**. All
functional and qfits-accounting gates pass; no installation or observational
processing ran. The Mac-qualified native observer/fixtures, production sources,
Mac accounting parser/runner and private CMake target wiring are unchanged.

All **80 role directories** were independently read back: exact expected signed
16-bit detector pixels, FITS metadata/scaling/padding, output sets and partial
publication behavior; staged inputs/sentinels remain unchanged. Ordinary and
observer products match each other and the inspected Mac reference exactly.
Expected native exits and one returned context/one destruction with no mismatch
or live owner pass in all 40 observer logs.

All **120 descriptor boundaries** (CLI return and both cache purges) preserve
count and identity. All observers retain the original three descriptors; the
soft limit changes from 1024 to the hard limit 4096, as expected from unchanged
xmemory initialization. Linux /proc/self/fd enumeration completes independently
of that policy; Mac /dev/fd enumeration was separately qualified.

The original after-cli state is preserved: **32 cases** retain five RAM
registrations whose bytes exactly match the queried filename including NUL and
four integer arrays for the cached headers; eight missing/non-FITS cases have
zero. Absolute cases use the actual target pathname length. All **80 allocator
boundaries after the first/second public cache purge are zero** for RAM,
mapped-file/reference and swap fields. No production cleanup repair or cache
suppression is required by these observed states.

## Evidence retained and inspected

Original target directory:
`~/Software/build/wenu-imaging/chapman3-stage2-split-dnoik6zg/`.
Archive `chapman3-stage2-split-evidence.tar.gz`, SHA256
`fbdf35705b488edc22d460a1dea79ae90251243ff77308a04da3d16e6880c861`.
Mac transfer directory:
`~/Software/build/wenu-imaging/chapman3-split-transfer-0fcd86f8/`.
Persistent attachment `libfile_b7b8312d58408191b71e492c7cac2e57`.
All **476 identities** verified, including 475 manifest entries and the manifest.
The archive hash matches the target and verified Mac transfer. Raw logs and all
staged/produced file sets were inspected; all recorded source identities match
the delivered and exported files. Reports, build identities, full transfer
manifest and inspection summary are committed under
`fixtures/chapman3-stage2-split-2026-10-27/`.

The target's inspected Mac reference report hash is
`299895e850c473c21645e8ecc03f21ef785160a6896492cef00198bcd59b3f78`.
Reference/source/export/checkout and protected selected engine/configuration
hashes remain unchanged. Preserve all four original Mac/target run directories,
archives and the transfer copy, including the first failed observer and visible
cache-state baseline. No merge, branch deletion or run cleanup is implied.

## Accepted boundary and next roadmap work

This accepts the **bounded Stage 2 / S2-04 split I/O/publication ownership**
increment: actual Mac C90/C17 ASan/UBSan plus separate external leaks/accounting
(80 pairs), and actual Chapman3 C90/C17 functional/qfits accounting (40 pairs),
with controlled cache attribution and exact shared products. #106 is resolved
for the diagnostic observer; target enumeration is now also verified.

Chapman3 remains uninstrumented. Compatible target external sanitizer/leak-tool
coverage is unavailable and not claimed; zero bookkeeping is not a replacement
for that gate. Broader #75/Stage 2 remains open: S2-05/06 calibration ownership,
S2-07 additional recipes, S2-08 practical injection, S2-09 repeated stages,
S2-10 cache lifetimes/general mmap/swap and conditional S2-11 wrapper checks.
This single-call fixture suite and double purge do not certify those later rows.

Next is review/integration of PR #105 when explicitly requested, synchronization
of both user clones and only authorized Git branch cleanup. After integration,
prepare the bounded S2-05/06 calibration ownership baseline, retaining Mac-first
development and unchanged target drivers/fixtures. No calibration workload has
started here. The early ESO Phase 3 requirements audit remains pending and the
mandatory review before Stage 2A/component extraction still applies.
