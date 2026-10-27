# S2-03 Mac correction acceptance — 27 October 2026

Actual Intel Mac source: fix/103-getopt-name-bounds at
18a196224ba436ae6d68d43b40c25245bbbf50d3, clean. **Bounded Mac gate passed.**
Chapman3 correction verification is pending; #103 and broader #75 stay open.
Integration order remains baseline PR #102 then correction PR #104; neither is
merged. Preserve all original runs, archives and normal installations.

## Results and semantic comparison

| Lane, each covering C90/C17 and OCAM/WFI | CLI case pairs | Result |
|---|---:|---|
| ASan/UBSan | 112 | All passed; no recorded invalid-access/UB finding |
| Separate uninstrumented leaks/accounting | 112 | All passed; zero unreachable blocks/bytes |
| Focused actual-parser regressions | 13 per build, 52 total | All passed |

Each CLI pair ran the ordinary executable and an observer calling the same
unchanged recipe entry point. All 448 CLI invocations have expected statuses
and diagnostics. Observer contexts have the declared successful-construction
and recipe-destruction counts, matching owner identity, no live owner at return,
and zero qfits registrations/bytes at process start and after CLI return.
Partial-construction internal cleanup remains unmodified and is observed by
accounting rather than counted as a returned context.

All 224 argument/PAF identities, native exits, ownership contracts and final
accounting match the inspected baseline's passing uninstrumented semantic
reference. The 100 instrumented pairs previously blocked by #103 now complete.
All thirteen original Mac-qualified source/driver/fixture hashes are retained,
including the corrected bundled parser. Only its registered-name comparison
changed in production; no numerical/allocator-policy change is made.

The four native parser regression logs each contain all thirteen individual
passes and a zero-failure completion record. They cover exact/prefix/ambiguity,
unknown options, value forms, short options and end-of-options semantics. The
missing-value expectation is the existing ':' contract, not a production change.

## Evidence and preservation

Original successful directory:
`~/Software/build/wenu-imaging/mac-stage2-cli-corrected-92e328bc/`.
Archive: `mac-stage2-cli-corrected-evidence.tar.gz`, SHA256
`f7f0f06945241edf25e41b9815d1a2cc69e370a5f07409db9083f8d6ee558b31`.
Persistent attachment: `libfile_d3077cac53a48191b953036ed7679c71`.
All **930 file identities** verified, including the transfer manifest. Original
448 CLI logs, four parser logs, statuses/diagnostics, accounting boundaries,
staged PAF identities, source hashes and four build records independently checked.

The archive also preserves the stopped attempt at source
4077e6e3eb31a3fc84bd56c6650d04ada93cd7fe in
`~/Software/build/wenu-imaging/mac-stage2-cli-corrected-7pmo1ec_/`.
Its first instrumented parser run passed twelve checks and failed only the
incorrect missing-value assertion (expected '?' instead of ':'); no CLI pair ran.
Original report, log, build record and source hashes are retained/verified.
The original invalid-read baseline remains separately retained as documented
in [the failed-baseline record](stage2-cli-baseline-evidence-2026-10-27.md).

Apple Clang 15.0.0.15000100 and CMake 3.29.3; four Debug C90/C17 builds using
the recorded Xcode SDK/x86_64 target, mode-2 qfits/max pointers 2000000.
ASan/UBSan and uninstrumented leaks lanes remain separate, with no suppressions.
Full flags, tool hashes and per-command provenance are in the report/build records.
The successful report SHA256 is
`a17450679412c1e591aee3a06de163b41add42c6ef8d7382accfaeab57f8acc8`.

Sources/export/checkout, protected selected engine/configuration and original
baseline report remained unchanged. Every run stays under the agreed build
root; no installation, engine switch, image reduction or Pycavi execution ran.
No successful split, same-process repeated stage, cache purge, mapped/swap or
full Stage 2 acceptance is claimed.

## Next: unchanged target verification

`qualify_cli_chapman3.py` imports the same case/PAF preparation functions and
uses the exact Mac-qualified native drivers. It requires all thirteen source
hashes to match the inspected Mac report before running. Two GCC C90/C17 builds
will execute 112 CLI pairs plus 26 focused parser checks, comparing arguments,
PAFs, exits, ownership and final accounting against that Mac reference.
This is uninstrumented functional/qfits-accounting verification. It neither
substitutes old sanitizer libraries nor claims external target memory coverage.
Fresh actual-target provenance and returned evidence remain required.
