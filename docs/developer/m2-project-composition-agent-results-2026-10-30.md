# M2 project/native composition — agent results — 30 October 2026

Owner accepted/merged PR #156 and instructed “merge, clean, and proceed”. Baseline:
`ea35197a7f074ac1c44289e7bcc94336f92d6681`. This implements the configuration
connection recorded in [#155](https://github.com/fselman/wenu-imaging/issues/155),
within original M2, without starting M3. See the
[composition contract](../architecture/proposed/m2/project-composition.md).

The integrated project loader composes reusable complete project domains and calls
the existing native reader for complete/split/local native configuration. It
preserves all project/native source bytes, hashes, edges and domain origins in
one immutable CLI/library configuration. The closed authoring semantics and
native readout consistency check are reused against resolved stored values.
Project conflicts fail; numeric overrides retain the native allowlist. Separate
purpose/recipe/product profiles and prior authority/readiness limits remain intact.

## Actual agent verification

Linux x86_64, GCC 13.3.0, Python 3.12.14, CMake 3.29.6. Fresh private C90 build
linked normal mefpp and the configuration bridge/probes. Final focused CTest:

| Check | Result |
|---|---|
| native_config_migration | Passed, 13.50 s |
| native_config_project_composition | Passed, 25.63 s |
| Total | 2/2 passed, 39.13 s |

Elapsed times identify attempts, not performance benchmarks. Legacy build warnings
remain; this is not a warning-free compilation claim. All native C/header files,
parser sources and domain catalogs are unchanged. CMake adds only the new test.
Accepted C17/sanitizer/native ownership evidence is reused, not relabeled as new
qualification. No new dependency, installation, engine selection, FITS or numerical
run occurred.

The existing regression checks both original/native/CLI settings and 21 negative
cases through the changed combined-project method. New composition checks cover
18 primary profiles (2 instruments x 3 native reference layouts x 3 project
layouts), native version-1/2 compatibility and both committed examples. Full and
split references agree with the independent retained native settings baseline;
local overrides agree with the real old CLI loader. All 585 OmegaCAM / 249 WFI
fields compare exactly, including stored floating bits.

Twenty-four rejection/recovery cases pass. Successful controls retain shared
profiles across projects, original/resolved path bases, full native source graphs,
all project contributors, deterministic CLI/library bytes from two directories,
CRLF text, independent caller copies, immutable source-deletion recovery and
failed-CLI output preservation. The resolver validates readout declarations
against effective native values, including a contradictory overscan override
that must fail. It does not simply remove the former standalone-file guard.

## Retained evidence and scope

[Evidence directory](fixtures/agent-m2-project-composition-2026-10-30/README.md)
contains the final CTest log, detailed migration/composition reports, relevant
compile records and hashes. Full configure/build logs and generated fixtures
remain under `/workspace/scratch/555b377cf948/project-composition-c90` and its
`test-work` directory. Earlier passing development runs remain separate.

Actual selected-tool Intel Mac and representative shared Chapman C90 checks are
pending. Build normal mefpp plus mef_config_read, config_domains_probe,
config_paf_snapshot and cli_capture_probe, then select only
`^native_config_(migration|project_composition)$`. Preserve installed-file baselines,
checkouts and all earlier evidence; do not replay the historical matrix or repeat
selected-tool qualification. Follow the verified nested-package protection lookup.

#155 remains open for actual target verification and owner review. The earlier
closure review is historical at its stated source baseline. Full M2 closure needs
a cumulative disposition after this increment; two tests alone are not milestone
acceptance. ASDF persistence, executable plans, M3 paths/FITS, detector identity
and numerical optional/multi-amplifier support remain their original work.
