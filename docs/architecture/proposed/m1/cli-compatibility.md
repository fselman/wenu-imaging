# M1 legacy CLI compatibility capture

Owner instruction: proceed with the legacy CLI/list/save-flag/effective-override
adapter after accepted PR #138 and clean Mac/shared Chapman main
`a58291a1f980fa1563ef89b49e01de4e4d47796c` (29 October 2026).

## Boundary and implementation

`mef_cli_request.h/.c` adds an owned, inspectable compatibility capture of an
already successful `mef_bb_load` call. It does not implement another option
parser. The production recipe's loader and command-line conversions remain
unchanged. `mef_cli_fields.def` maps nine nullable binding strings and eight
integer flags/derived values to the actual legacy members.

The capture independently owns:
- original ordered argv tokens, before getopt's pointer permutation;
- the explicit absolute invocation base directory;
- selected PAF, bias/BPM/dome/sky/MFF/science/split bindings and MFF output;
- raw verification/extension/subtraction/save/saturation flags and median area;
- the existing typed configuration snapshot, copied after CLI overrides.

All strings/arrays are copied. The original legacy object and argv may disappear
immediately afterward. Occupied output/error owners are rejected unchanged;
partial construction has one cleanup path, NULL-safe destruction and per-object
allocation. An independently owned optional error may be NULL under secondary
OOM; the primary returned status is authoritative. Accessor views are const and
borrowed until capture destruction. Allocator user data/callbacks outlive all
objects using them. No global mutable state is introduced by the capture.

Bindings remain byte-for-byte lexical values, including NULL versus empty,
relative paths, spaces, quotes and UTF-8. No path normalization, file/list type
inference, list expansion, selection/sorting/deduplication, FITS interpretation
or cwd/environment mutation occurs. The base is supplied explicitly by the
caller, not inferred by the library. Original argv/source correspondence is a
caller contract, not an independent parse performed by the capture.

Some legacy fields cross the old config/request boundary: configured BPM and
output-MFF names are constructor defaults that can be replaced by CLI bindings.
The bridge deliberately preserves the effective fields in both its raw binding
view and existing configuration snapshot, rather than reconstructing defaults.
Numeric overrides copy their final stored C values at full precision; they are
not reparsed through earlier float-temporary PAF conversions. Repeated options,
positional output precedence and permissive/partial legacy conversions remain
as implemented by the original loader. The known `--ksize` missing-handler defect
#133 is retained, explicitly tested as a rejected command, and not repaired here.

## Why this is separate from mef_request

One legacy invocation can describe a sequence of calibration creation and science
steps. The current `mef_request` describes one operation with resolved per-image
identities/HDU selectors. The bridge therefore does not fabricate a single
operation, image IDs or a detector mapping from an unresolved list filename.
In particular, legacy xtnum=0 means all extensions; it must not be translated
into the new image-reference hdu_index=0, which identifies a primary image.

The bridge is an internal transitional boundary, not a frozen WAD/ASDF/TOML
schema or an installed ABI. Connecting it to resolved operation requests and
the existing image/list reader remains the next integration step. The general
path/file-discovery replacement still belongs to M3. No new asset resolver,
graph/cascade engine, calibration association policy or numerical service is
implemented by this capture. Normal mefpp does not use it yet.

## Diagnostic defect found during verification: #139

The first ASan/UBSan run stopped at the old `-d` display: default xtnum=0 indexed
`bb->ccd[-1]` while reading RON in `mef_bb_dump`. The read occurred eight bytes
before the detector allocation, before the new capture function ran. Ordinary
C90/C17 runs did not detect it and are not evidence of memory safety.

The correction is limited to diagnostic bounds handling in `mefp_lib.c`:
nonpositive selectors use the first representative CCD (consistent with the
existing display and all-extension selector); valid positive RON selection is
unchanged; unavailable contexts or excessive selectors produce a diagnostic
without dereferencing the array. Other display values, CLI conversions, raw
selectors and numerical calculations are unchanged. The source diff is retained
and tracked in [#139](https://github.com/fselman/wenu-imaging/issues/139).

The normal `-d` option still prints and then continues into the engine. Do not
use the production executable as a supposedly dump-only checker. The private
test program calls only the old loader and owned capture; it never calls the
production main or engine. This correction is not a new QC estimator or a change
to configured gains/RON used in reduction. #139 remains open pending target
verification; do not discard the failed first sanitizer evidence.

## Tests and build isolation

The existing `MEFPP_BUILD_CONFIG_PROBES` option remains OFF by default. When
enabled, the isolated library includes the new capture module; CMake adds the
`cli_capture_probe` executable and `native_cli_capture` CTest. The normal CLI
parser/recipe source is not moved or duplicated. The test includes that exact
source with its main renamed, calls the real loader, checks a separately written
binding comparison, then destroys the legacy object and overwrites original
argument strings before inspecting the surviving owned capture.

Agent Ubuntu/GCC 13.3 C90/C17 runs pass 51 cases: twelve retained pilot command
forms, defaults/full/repeated/partial/empty/display variants for OCAM and WFI,
bounded display selectors, fourteen rejected inputs and five informational
exits without a default PAF. Thirty-two cases produce captures; the remainder
preserve loader error/informational behavior and produce none.

Every successful capture case checks its effective config at full stored bits
against both the pre-destruction legacy snapshot and the independent source map
with explicit expected overrides. Bindings, original argv and median area are
checked independently. Text-only sentinel lists retain their hashes, including
duplicate/unsorted member lines. No list contents or real FITS are processed.

Allocation controls cover 118–173 successful-construction allocation positions
per capture case (4,058 positions across the 32 capture cases), each with transient
and persistent OOM; all checked owner counts return to zero. Twenty ownership
cycles per case, invalid allocator/output/base/argv controls and stream errors
also pass. The new adapter core passes strict C90/C17 syntax with
`-pedantic-errors -Wall -Wextra -Werror`; existing legacy compile warnings are
retained and not described as a warning-free native build.

After the diagnostic correction, all 51 cases pass under C90 ASan/UBSan with
`ASAN_OPTIONS=detect_leaks=0` and `UBSAN_OPTIONS=halt_on_error=1`. No LeakSanitizer
pass or whole-engine memory acceptance is claimed. Original failure and fixed
reports/selected logs/link commands are retained under
`docs/developer/fixtures/m1-cli-agent-2026-10-29/`.

Actual Mac/representative Chapman CMake builds and the three focused CTests
remain pending. Use the established absolute tool paths; no tool installation
or repeat qualification between copycat Chapman hosts. No user installation,
normal execution configuration, notebook, raw input or accepted product has
changed. Next: target verification, then bridge-to-operation integration and one
real operation through the accepted common pattern; M1 is not complete.
