# M2 configuration migration — paired target results — 30 October 2026

Intel Mac and representative shared Chapman4 private C90 builds and both focused
configuration CTests passed at implementation
`38f4f4d4bd05c4977f1624fc8737431527bdbe8a` (PR #153). Protected files and review
checkouts remained unchanged. This increment is ready for owner review; full M2
closure remains a separate review/acceptance decision.

The shared Python API/CLI preserves the original PAF/CFG text and hashes,
occurrence/conflict evidence and native subset/override contributions, producing
immutable configuration records. Actual native PAF/TOML settings agree exactly,
including selected local CLI overrides. Separate reduction purpose, ordered recipe
and product requirements remain intact. Ordinary reductions and installed software
are unchanged. See the [migration contract](../architecture/proposed/m2/configuration-migration.md)
and [agent receipt](m2-migration-agent-results-2026-10-30.md).

## Actual target results

| Target | Private work directory | Domains | Migration | Total |
|---|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | /Users/fselman/Software/build/wenu-imaging/mac-m2-migration-p7wrei4c | 25.95 s | 7.98 s | 2/2 passed, 33.94 s |
| Chapman4, shared home | /home/fselman/Software/build/wenu-imaging/chapman-m2-migration-b0zxlakk | 22.58 s | 5.94 s | 2/2 passed, 28.52 s |

Times identify attempts, not comparative benchmarks. Chapman /home resolves to
/home1 in its returned test project and module/engine paths. Both builds used the
already selected Python, CMake/CTest and compiler paths, Debug C90 core and private
C99 parser/shim, two build jobs and niceness 10. No tool/dependency requalification
or installation occurred. The normal mefpp executable and mef_config_read,
config_domains_probe, config_paf_snapshot and cli_capture_probe linked; the normal
numerical engine was not executed.

- `native_config_toml_domains`: existing 11 typed/document/lifetime profiles,
  151 catalog templates and 25 domain/unit rejection/recovery cases; changed
  native document/serialization ownership and allocation controls.
- `native_config_migration`: all 585 OmegaCAM / 249 WFI stored settings, original
  PAF constructor and selected legacy CLI override comparisons, source-preserving
  generated examples, CLI/library equality from two directories, both identical
  WFI duplicates, explicit conflicting-occurrence resolution, frozen records and
  21 rejection/recovery controls. Also checks source/caller independence, saved
  records/tampering, CRLF, parent overrides, resolved symlink edges, project native
  reference integration and exclusive output receipts.

These descriptions come from the exact tested source; the returned terminal
output reports both complete CTest entries passed. Logs and detailed JSON reports
remain under each private work directory (`tests.log`, `build/test-work`, plus
`commands.json`, `protected.json`, `source-commit.txt` and inherited build settings).
This receipt uses inspected owner-returned output, not independently transferred
and hash-audited target archives.

## Preservation and actual package layout

Both hosts reported protected-file and checkout preservation passing. Mac protected
its executable configuration, selected engine and installed reduction module.
Chapman confirmed its actual module at
`/home1/fselman/.conda/envs/wenu-imaging/lib/python3.11/site-packages/pycavi/pycavi/pycavi_associate_reduction.py`
and selected engine at `/home1/fselman/opt/local/mefpp/bin/mefpp`.
The Mac module is similarly beneath the nested `pycavi/pycavi` installed package.

[#154](https://github.com/fselman/wenu-imaging/issues/154) records a handoff error:
the first Mac protection lookup guessed the module was directly under top-level
pycavi. It stopped before export/build/tests, in retained directory
`mac-m2-migration-tk3rgv6i`. The corrected command follows the as-is nested package
and resolves it with PathFinder without importing reduction code. The successful
Mac and Chapman results above qualify that correction. No migration source or
numerical implementation change was needed. Preserve the failed attempt.

Owner clarification: always establish paths/interfaces from as-is source and
actual host evidence; never guess a package or installation layout. This rule
applies to terminal handoffs as well as implementation.

## Scope and next gate

No target C17, sanitizer/LSan, whole-dependency OOM, concurrency, FITS applicability,
scientific reduction or Phase 3 acceptance is claimed. Agent C17/scoped sanitizer
evidence remains separate. CFG values remain explicit compatibility evidence;
asset identities, associations and executable plans are not invented. WAD checking
is scoped to configuration attributes/native catalog; ASDF publication and general
image/task validation remain in their original milestones.

This documentation receipt requires no rebuild or test replay. Preserve both
private runs and earlier evidence. Owner review precedes separately authorized
merge/cleanup; full M2 closure requires its cumulative review rather than assuming
that two passing CTests close the milestone.
