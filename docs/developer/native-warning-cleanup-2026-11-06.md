# Native warning cleanup and bias checker correction — 6 November 2026

The owner authorized addressing the warnings revealed by the first standalone
bias build. The retained Mac run `mac-standalone-bias-SP3Cgdhb` at
`f98e8abb8a66a19b10e0973537c8e4ada48ca376` compiled successfully and passed
four native QC-copy profiles. Its eight integration groups had three checker
failures; complete integration acceptance remains pending.

This correction addresses every one of the 63 reported compiler diagnostics
without suppressing warning flags. Actual AppleClang warning clearance requires
the corrected Mac rebuild. It also corrects the three checker defects while
retaining exact pixel, header and QC assertions. No installed files, raw data,
scientific thresholds, bias kernel or rejection policies are changed.

## Warning inventory

Counts are diagnostic occurrences in the owner's original build transcript.

| File under mefpp2 | Count | Correction |
|---|---:|---|
| qfits5/src/fits_h.c | 1 | Remove unused output counter |
| qfits5/src/get_name.c | 2 | Correct reset and directory extraction |
| qfits5/src/md5.c | 1 | Clear the full context after digest finalization |
| qfits5/src/xmemory.c | 3 | Mark debug-only parameters; remove unused result |
| src/iproc/corner.c | 1 | Remove unused, leaked double3 allocation |
| src/iproc/cube_filters.c | 1 | Express exhaustive sky-count branch |
| src/iproc/detector.c | 1 | Remove unused pixel count |
| src/iproc/image_stats.c | 2 | Remove dead uninitialized read; defined entropy bound |
| src/include/irtemp.h | 4 | Spell existing truncated integers explicitly |
| src/iproc/slitposition.c | 1 | Remove unused spectrum size |
| src/spectro/spectro_detect.c | 4 | Remove dead bookkeeping; document ignored parameter |
| src/unix/cmdline.c | 1 | Remove unused argument length |
| src/unix/filename.c | 2 | Correct reset and directory extraction |
| src/unix/filesys.c | 1 | Mark platform-dependent parameter |
| src/unix/getopt.c | 1 | Compare size_t values without narrowing |
| src/unix/iniparser.c | 1 | Remove unused line counter |
| src/unix/ptrace.c | 2 | Mark unused call-site parameters |
| ins/mef/common/mefp_lib.c | 33 | Remove dead bookkeeping, exhaustive validated branch, explicit return |
| ins/mef/common/mef_paths.c | 1 | Match legacy qfits API at the existing const boundary |
| **Total** | **63** | |

The directory review also corrects reversed memchr arguments for trailing slashes
and reserves the terminator at the documented 4096-character limit in both
copies. A redundant array-null check in an alternate allocator branch is removed.
No blanket warning disabling or arbitrary normalization initialization is used.
The sky/dome branch remains exhaustive because unsupported modes are rejected
and bias returns through its existing operation earlier in the function.

All 231 named temperature entries retain their effective integer values, as does
the sentinel; the four original half-degree literals remain in comments (#261).
The historically ignored minimum-spectrum-length argument remains ignored
(#265). Restoring fractional temperature precision or activating a spectral
rejection condition requires a separate scientific decision.

## Checker corrections

- #255: preserve the selected virtual-environment executable path without
  dereferencing its Python symlink.
- #256: generate an unmasked, MAD/RON-omitted reference for the omission case;
  verify measured/unavailable QC from its actual availability flags.
- #257: compare reordered inputs with a normalized-HDU reference bearing the
  same input basename. Provenance cards remain in exact header comparisons.

All references still use the actual native one-detector command. No ASDF writer
is mocked or replaced. There are six tiny reference products covering the three
policies and two detectors; the integration gate still has eight groups and
three independent actual ASDF validations.

## Verification completed in the agent workspace

Actual C probes rebuilt and passed with GCC and undefined-behavior checking
(`-fsanitize=undefined -fno-sanitize-recover=undefined`):

- Four actual bias QC-copy/lifetime profiles, with explicit BPM/MAD/RON choices.
- Both directory helpers: ordinary/root/relative/repeated/trailing separators,
  exactly 4096 characters, over-limit refusal and repeated shorter calls.
- MD5 empty-string and abc known answers and complete final context clearing.
- Entropy zero/one-bit known answers.
- Exact corner-image comparison against the retained original function on two
  deterministic images; only the unused allocation is removed.
- Effective four IR temperature lookups and explicit creation-name return.

Python syntax, selected-interpreter symlink preservation and all named IR table
values also pass. No undefined-behavior report occurred. Existing legacy
NULL-free diagnostics remain visible; they are not compiler warnings or a new
failure, and no general destructor cleanup is included.

Retained evidence: `/workspace/scratch/b0416c2b7710/warning-checks`, including
`reviewed-qc-command.json`, `reviewed-warning-command.json` and corresponding
build/probe logs. The original corner reference SHA256 is
`dda978321f25a04448b8fcbb22ae20f72a9467891ee3e4a1a3940abeb1e3a852`.

## Remaining target verification

Build a fresh uninstalled candidate under the existing retained Mac work root,
using the same compiler/SDK, CMake, Python environments and libasdf prefix. Keep
the original source, build and failed checks untouched. Build the recipe, native
reference adapter, QC-copy probe and focused warning probe. Require no compiler
warnings in the new build log, then run both probes and the corrected eight
integration groups. The original corner function is compiled only as the explicit
test comparison object. No historical component gates need replaying.

Defects #251/#252/#255–#260/#262–#264 remain open pending target verification.
#261 and #265 retain separate scientific-intent questions. Overall #245 and
standalone recipe PR #254 remain pending full integration and actual whole-mosaic
acceptance. No installation, merge, viewer work or retained-evidence cleanup.
