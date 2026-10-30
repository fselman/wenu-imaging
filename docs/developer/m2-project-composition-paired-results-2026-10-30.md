# M2 project/native composition — paired target results — 30 October 2026

Intel Mac and representative shared Chapman4 private C90 builds and both focused
configuration CTests passed at implementation
`d0ab19e91b46e6fe6e21c541af99c21ed35029b4` (PR #157). Both hosts reported protected
installed files and clean review checkouts unchanged. This increment is ready
for owner review. Full M2 closure remains a separate cumulative review and owner
acceptance decision; no merge or M3 work is implied.

A project can now reuse complete project-domain declarations and select the
existing complete, split or local-override native configuration graphs. The shared
CLI/library loader preserves source texts, hashes, include edges and domain origins
in one immutable configuration. Existing complete projects remain supported.
Conflicting project domains fail explicitly; native numeric overrides retain the
existing C resolver and allowlist. Separate purpose, recipe and product profiles,
readout consistency checks and original authority/readiness limits remain intact.
See the [composition contract](../architecture/proposed/m2/project-composition.md)
and [agent receipt](m2-project-composition-agent-results-2026-10-30.md).

## Actual target results

| Target | Migration | Project composition | Total |
|---|---|---|---|
| Intel Mac MC02VV0HPHTDG | Passed, 11.41 s | Passed, 16.55 s | 2/2 passed, 27.97 s |
| Chapman4, shared home | Passed, 6.43 s | Passed, 13.16 s | 2/2 passed, 19.61 s |

Private work directories:

- Mac: `/Users/fselman/Software/build/wenu-imaging/mac-m2-project-composition-c04okrlf`
- Chapman: `/home/fselman/Software/build/wenu-imaging/chapman-m2-project-composition-s5e5inwh`

Times identify attempts, not comparative benchmarks. Chapman returned the resolved
`/home1` build path. Both commands used the already selected Python, compiler and
CMake/CTest paths, Debug C90 core with the existing C99 parser/shim, two build jobs
and niceness 10. They built normal mefpp plus mef_config_read,
config_domains_probe, config_paf_snapshot and cli_capture_probe. The normal
numerical engine was linked but not executed; resources were not decompressed.
No installation or selected-tool/dependency requalification occurred.

## Exercised configuration behavior

The two complete CTest entries passed on each host:

- `native_config_migration`: original PAF/native/CLI comparisons for all 585
  OmegaCAM / 249 WFI stored settings, source/duplicate/conflict retention,
  CLI/library equality, frozen records and 21 rejection/recovery controls.
  Existing combined-project cases exercise the changed loader as a regression.
- `native_config_project_composition`: 18 primary profiles across both instruments,
  three native layouts and three project layouts; native versions 1/2 compatibility
  and committed examples; shared-domain reuse and all contributing sources;
  CLI/library equality from two directories; 24 rejection/recovery controls;
  resolved path bases, CRLF, caller/source independence and saved-record recovery
  after deletion of private source fixtures. Readout contradictions against the
  resolved native settings must fail. Each rejected request is followed by a valid
  request in the same Python process; native parsing remains process-isolated.

These descriptions come from the exact tested source. This receipt records
inspected owner-returned terminal output, not independently transferred and
hash-audited target archives. Full logs and detailed JSON reports remain under
each private work directory: `tests.log`, `build/test-work`, `commands.json`,
`protected.json`, `source-commit.txt` and inherited build settings.

Both targets reported protected installed-file and checkout checks passing.
Protection follows the actual nested installed pycavi/pycavi module without
importing reduction code, and includes executable configuration and configured
engine files. Chapman's selected installed engine remains
`/home1/fselman/opt/local/mefpp/bin/mefpp`.

## Disposition and limits

The implementation and paired checks meet the bounded configuration integration
criteria of [#155](https://github.com/fselman/wenu-imaging/issues/155); the correction
is qualified for review, independently of PR merge and full milestone acceptance.
Preserve all private runs and prior evidence. This documentation receipt changes
no tested source and requires no rebuild or test replay.

Native C/header/parser/catalog files and numerical algorithms are unchanged.
No new target C17/sanitizer, whole-dependency OOM, concurrency, FITS applicability,
header/hardware trust, scientific reduction or Phase 3 acceptance is claimed.
ASDF publication, executable plans and M3 paths/FITS remain their original work.
The earlier cumulative closure review retains its historical source baseline;
full M2 disposition follows owner review of this increment. Merge/cleanup requires
separate owner instruction.
