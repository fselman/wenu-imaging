# Native final-MEF assembly — 6 November 2026

## Executive summary

The new native assembler combines completed temporary detector products into one
final MEF without recalculating or converting pixels. It uses the existing qfits
reader/header writer, preserves the selected reference primary and detector cards,
and publishes exclusively after native readback. Eight synthetic groups pass in 0.844s in
the agent environment, including 32 detectors and exact data-byte preservation.
Independent Astropy verification and target compilation remain pending on Mac.
The bias recipe is not connected yet; no observations or viewer are processed.

The preceding native QC writer passed the actual Mac ten-test gate in 2.589s at
`1434606c0287b53c0cf5a16b42bbb96802c0dc8c`: real C ASDF creation, independent
ASDF6 schema/exact-value checks, and all 25 metadata cases. The original native
executable was reused, the failed evidence and clean main preserved, and checker
defect #249 closed. This evidence is recorded in PR #248.

## Decisions reviewed before implementation

The owner approved retaining MEFs, temporary detector separation, a coordination
boundary before assembly, serial operation first, and one ASDF per final FITS.
The source review showed that `mef_bias_publish` writes a one-extension MEF; the
earlier WFI whole-mosaic assembly was Python. Its independent pixel/header checks
are useful acceptance patterns, but the new native engine must work without
Pycavi. The existing operation template and bias arithmetic remain authoritative.

Invoke the eventual real recipe in orchestration, read untouched raw data, and
write FITS/ASDF/logs into the explicitly selected products directory. Keep
`--output-dir` and complete `--output` mutually exclusive. A complete output
supplies the directory and retains its name. Generated products share one recipe
start timestamp with a per-product sequence; ASDF replaces `.fits`. These naming
helpers and native ASDF remain separate tested modules until recipe integration.

## Assembly contract

`mef_mef_assemble` accepts an explicit ordered manifest of completed private
one-extension MEFs, the final absolute FITS path and the logical reference-detector
ID. Each row declares the logical detector, configuration slot, final extension
ordinal, dimensions, BITPIX and scaling. The temporary product's data are in HDU1;
original raw-input HDUs remain separate provenance in the result/native QC.

The recipe caller must construct the complete manifest from its selected detector
set; this module does not discover missing declarations from raw directories or
configuration. It rejects an absent listed product, duplicate IDs/paths/configuration
slots, nonsequential output ordinals, unknown reference, wrong EXTNAME, dimensions,
type/scaling, extra extensions, primary pixels and truncated/inconsistent spans.
Configuration slots are supplied bindings, not inferred from header order. The
caller must hold all completed temporary products stable throughout the call.

Primary-header ownership is explicit: copy the nominated detector product's
primary, retaining its existing reference-detector gain/RON meaning. Do not
average these cards or call them measured mosaic summaries. Copy each extension's
cards, including EXTNAME, EXTVER, units, scaling and detector statistics. Header
edits are limited to final ORIGFILE in every HDU, primary NEXTEND and removal of
CHECKSUM, which becomes stale after edits. DATASUM remains valid because all data
bytes, including padding, are copied unchanged. New CHECKSUM generation is not
implemented or claimed. No general Phase-3 compliance claim follows from assembly.

Headers are rebuilt by enumerating an unmodified source, reusing the established
workaround for qfits_header_del's inconsistent card count (#212). No qfits source
is changed. qfits performs FITS ingestion and wide-span discovery; the assembler
does not implement another production FITS parser. It supports the existing LP64
wide-I/O representation. It bounds manifests at 4096 rows and scanned header bytes
at 1MiB per file; these independent resource limits can reject larger layouts.

The existing one-card FITS-string boundary remains explicit (#125): final
basenames longer than 68 characters, non-ASCII/control characters or quotes are
refused, not truncated. Long directory paths are independent of this basename
limit. Normal automatic CMDP/SMDP names fit. Expanding long-string support is
outside this increment.

## Resource and publication boundary

Only one detector data span is copied at a time using a 64KiB buffer. Manifest
metadata grows with detector count; header objects and existing qfits caches also
consume memory. No claim is made about upstream bias-kernel memory or measured
peak RSS. This design permits serial processing/release of detector arrays into
private products and a later coordination stage before final assembly. Bias adds
no gain harmonization; future flat harmonization is separate processing.

The assembler writes a private sibling, closes it, then uses qfits to verify
primary/extension identity, coverage, dimensions/storage type and byte spans.
It checks input file identities/lengths for changes and publishes with an exclusive
hard link. Existing files, dangling links and absent destination parents fail;
directories are not created and cwd is never changed. Private output is removed
on normal success/failure; caller-owned detector products are never removed.
The caller's stable-input requirement remains essential: stat checks are not
cryptographic identity or protection against adversarial concurrent rewrites.

This is exclusive file publication, not a FITS/ASDF/log transaction or a guarantee
of durability after power loss. No ASDF/log is created here. The eventual recipe
must report complete success only after all required final outputs succeed.
Failed ASDF completion must not silently remove an already complete MEF.

## Verification announced before execution

The stdlib driver compiles the actual new code with strict C17 diagnostics and
links the actual unchanged in-tree qfits sources, using the canonical CMake source
inventory. It generates only the existing platform-header fields from the host ABI;
no dependency is installed and no image engine or Pycavi is called. Legacy qfits
warnings remain visible; only the new module/probe use warnings-as-errors.

Eight synthetic test groups exercise:

1. Exact detector bytes/cards, explicit reference-primary selection and unchanged
   working directory (checked inside the native probe).
2. One 32-detector final MEF with 33 HDUs.
3. Mixed integer/scaled and float64 detector storage, unequal dimensions,
   negative zero and a retained NaN payload, without decoding/re-encoding pixels.
4. Wrong/duplicate detector, configuration, ordinal, dimensions, BITPIX/scaling,
   invalid numeric declarations and unknown reference; no final output allowed.
5. Missing detector files and truncated data; no final output allowed.
6. Extra detector extensions and primary-image data; no final output allowed.
7. Existing final file and dangling link preserved exactly.
8. Missing parent and unrepresentable final basename refused.

Synthetic input files are fingerprinted before/after each operation; private
staging must not remain. A small independent test-fixture reader checks exact
header-card order and stored data bytes without Astropy in the agent environment.
It is not used for production ingestion. The fixtures include valid DATASUM cards.
On Mac, `--astropy-python` independently opens/verifies all three successful
layouts with real Astropy, compares stored data bytes/types, and validates the
retained data checksums. These target checks are prepared, not yet executed.

The CMake option `MEFPP_BUILD_MEF_ASSEMBLER` defaults OFF and exposes only an
isolated library/probe, without recipe activation. CMake is unavailable in the
agent environment, so that build entry is not claimed tested; the direct compiler
route executes the actual same assembler and canonical qfits source list.

## Remaining work

Record actual Mac acceptance, then connect the standalone recipe coordinator:
one start identity/output policy, serial unchanged bias calls, temporary detector
ownership, coordination boundary, native final MEF, collected native ASDF and
logs, and truthful completion. Then run the actual whole-mosaic bias recipe from
orchestration with untouched raw inputs and the chosen products destination.
Owner inspection of these real products precedes saved-plot Bias viewer work.
No installation, merge, cleanup, observations or numerical-policy change occurs
in this increment. Overall #245 remains open.
