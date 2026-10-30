# M3 inspector canonical fixture correction — 30 October 2026

Subsequent corrected target verification passed 15/15 on both Mac and Chapman
at 2c820effff393d5ea4e1555439397ef7c7a6cda6, with protected installed files and
checkouts unchanged. See [paired results](m3-project-inspection-paired-results-2026-10-30.md). Earlier draft/target-pending
statements in this retained receipt are historical; full M3 remains open.

PR #161 remains draft. [#162](https://github.com/fselman/wenu-imaging/issues/162)
records an actual test-fixture portability failure at implementation
`a1a95c700a7bb7755cf81ac8e2213b3adc754f96`. Production inspector, path resolver,
console metadata, native code and installed software are unchanged by this fix.

## Actual target evidence at the original revision

| Target | Result | Preserved work directory |
|---|---|---|
| Intel Mac | 14/14 passed, 3.597 s; protected installed files and checkout unchanged | `/Users/fselman/Software/build/wenu-imaging/mac-m3-project-inspection-w9u1xfvl` |
| Chapman4 | 14 groups ran, two failures and one error, 3.517 s; protected installed files unchanged | `/home/fselman/Software/build/wenu-imaging/chapman-m3-project-inspection-u77iwgab` |

Mac detailed fixtures: `m3 project inspection 39tyinyq`.
Chapman detailed fixtures: `m3 project inspection gzmqps47`.
This is inspected owner-returned output, not transferred/hash-audited archives.
The Chapman wrapper raised after the test failure, so its final checkout check
never ran. Do not claim post-run checkout verification; inspect/guard it before
updating. Preserve the failed work directory and original Mac success.

## Source-confirmed cause and bounded correction

`PathResolver` explicitly returns canonical paths. Chapman's established `/home`
path resolves to `/home1`. Test `setUp` retained lexical mkdtemp paths, while its
assertions expected those strings to equal the resolver's canonical output.
Consequently:

- `test_path_bases` compared canonical `/home1` to lexical `/home`.
- `test_actual_instrument_mappings_and_cfg_authority` did the same for a CFG root.
- `test_fits_errors_duplicate_cards_and_header_conflicts` searched for a lexical
  asset path and raised StopIteration when the canonical path was correctly stored.

The correction resolves only the generated fixture directory identity at setup.
It changes no production path semantics or scientific setting. A fifteenth test
explicitly supplies symlinked invocation, project and member bases. It requires
canonical resolved identities, retained literal link targets, one deduplicated
asset and equality with the same inspection through direct canonical bases.

## Actual agent reproduction and verification

A private work-parent alias `m3-alias-parent` points to `m3-canonical-parent` under
`/workspace/scratch/555b377cf948`. No system/home alias was changed.

| Driver | Actual result | Generated fixture directory under the alias |
|---|---|---|
| Original 14-group driver | Reproduced two failures and one error, 4.229 s | `m3 project inspection 290t0n0v` |
| Corrected 15-group driver | 15/15 passed, 4.539 s | `m3 project inspection hg0_yse2` |

[Retained agent logs, reports and source hashes](fixtures/agent-m3-canonical-fixtures-2026-10-30/README.md)
identify both attempts. The corrected run exercises all earlier metadata/path,
CLI/package-entry, no-write/cwd, array-read and error controls through the aliased
work-parent, plus the new regression. No extra native build or historical matrix
was run. Syntax, whitespace, links and unchanged-production-source checks passed.

## Next gate

Repeat only the focused corrected 15-group driver on the selected Mac and
representative Chapman Python in fresh private exports. No reinstall, engine
activation or C toolchain qualification is needed. Preserve protected-file and
checkout checks even on failure where possible. Actual corrected target results
remain pending; #162 and entry-placement #160 stay open for their target gates.
Original M3 tracker #159 retains execution routing and full inspection coverage.
This correction does not complete M3 or authorize merge/cleanup.
