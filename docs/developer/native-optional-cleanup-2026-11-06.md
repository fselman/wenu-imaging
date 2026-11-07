# Optional native cleanup diagnostics — 6 November 2026

## Executive summary

Owner instructed addressing #269 after completing bias inspection/recovery.
The patch adds pointer guards at optional release sites; it does not change
allocation ownership, numerical kernels, header values, filename formatting or
the global allocator diagnostic. Source work is stacked on the verified scalar-QC
branch, whose recovered real FITS/ASDF and corrected recipe relink atc1751306
are complete. No raw bias rerun or product modification is needed.

## Changed callers

- mef_clear_names skips NULL elements in partially populated owned name lists.
- mef_bb_clear_work releases nonnull optional scan/statistics/extension-name
  arrays, and still resets every pointer and count unconditionally.
- mef_bb_del releases nonnull optional threshold/statistic/original-name fields.
- mef_create_orig_filename guards the old name for bias/BPM/dome/sky/combined/
  science before the existing strdup replacement. Initial and repeated calls
  retain the existing CMDP/SMDP formatting and ownership behavior.
- qfits_cache_scan's failure path releases nonnull pending name/offset/span
  fields. This is the same caller mismatch observed during the real failed
  expanded-header assembly; success-path cache ownership is unchanged.

xmemory_free itself is untouched. In particular an intentional direct NULL call
still emits its diagnostic. No global logger/allocator suppression or new free
wrapper is introduced. Nonnull releases execute at the same ownership boundaries.

## Focused evidence

The new optional_cleanup_probe.c runs against actual mefp/qfits/xmemory. Its
standalone mode reproduces the old diagnostic/assertion failure; the guarded
version passes under UBSan. It checks empty owner/NULL owner, allocated and
partially populated lists, all12 optional work fields, pointer/count reset,
repeated clear, optional final-owner fields, all six initial/replacement filename
branches, valid PAF construction/destruction, failed construction and malformed
FITS cache failure. Allocator pointer counts return to the initial baseline;
repeated replacement has constant live-pointer count. Intentional free(NULL)
remains diagnostic. Probe capture is test-local and does not hide production
messages. Strict C17 syntax for both changed runtime files and probes passes.

The existing bias_product_qc_probe includes the contract and exposes `cleanup PAF`
without a new CMake target. Its normal argument path retains the existing four
in-memory BPM/MAD/RON numerical/QC copying profiles. The actual Mac gate should
build only that target with the selected cached tools, run the cleanup mode and
normal four profiles, and reject any uncaptured xmem diagnostics. No ASDF recovery,
old fixture matrix or observations need rerunning. Target Mac results remain
pending; do not describe agent UBSan/syntax results as target qualification.

## Build and preservation

Use scalar-qc-c17-source and scalar-qc-qualification-c17/build under the retained
mac-standalone-bias-SP3Cgdhb root. Apply only mefp_lib.c, cache.c, the QC probe and
the new included cleanup test. Keep CMakeCache.txt unchanged; no configure, fresh
source/build tree, dependency rebuild or installation. Record source patch/revision,
compiler/cache identity, attempt logs and results. The existing production recipe
binary remains c1751306 during this component qualification. Relink/version-stamp
it only when accepting the next production candidate; this gate does not process
or alter any already verified product. Keep #269 open through actual Mac evidence.
