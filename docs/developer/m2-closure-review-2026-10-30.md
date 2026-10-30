# M2 cumulative closure review — 30 October 2026

Reviewed as-is baseline: accepted merged `main`
`c0bbcc5866b49d64fad6498a029429b35ada9953`. The owner returned clean, synchronized
Mac and Chapman main at that commit after PR #153 integration and branch cleanup.
Authorization for this increment: proceed with the cumulative M2 closure review.

**Disposition: keep M2 open.** The native effective-value gate and the delivered
migration/provenance lane have qualified evidence, but the original reusable
project-domain/subset requirement is not fully integrated. Record this remaining
work as [#155](https://github.com/fselman/wenu-imaging/issues/155). This review does
not revoke accepted increments, report a numerical regression, close M2, start M3
or silently narrow the approved milestone.

## Review method and controlling contract

Read the merged source, CMake target definitions, the five paired target receipts,
original [M2 deliverables/gate](../architecture/proposed/implementation-plan.md#m2--toml-subsets-and-configuration-migration)
and [one-loader/subset design](../architecture/proposed/pycavi-mefpp.md#2-toml-subsets-and-one-effective-configuration).
Checked the accepted commit graph and post-test documentation deltas. This is
source/evidence inspection, not a new executable test or an independent target
archive audit. No build, historical matrix replay, installation, reduction,
scientific validation or external-tool qualification was performed.

The M2 milestone map names deterministic configuration resolution; its detailed
requirements also specify reusable project/composition, instrument/detector,
association, processing, recipe, execution, quality and product/profile domains.
The design explicitly calls these reusable subsets under one loader. Passing the
native numeric checks alone does not remove that requirement.

## Requirement-by-requirement disposition

| Original M2 requirement | As-is implementation/evidence | Disposition |
|---|---|---|
| Versioned domains; separate reduction profile, recipe and product profile | Native schema 3 maps all 151 getter templates into instrument/detector, processing and product domains with explicit units; closed project authoring schema covers the remaining domains and distinct profile identities | Implemented at the declared configuration/authoring boundary; reusable composition integration remains below |
| Small project entry references reusable subsets; fewer files allowed | Native schema 2/3 entry/include graphs work, including single-file input. The combined project entry has inline-only domains and requires a complete standalone native reference | **Partial; closure blocker #155** |
| Containing-file bases, explicit overrides/allowlist, unknown keys, versions and conflicts | C bundle resolves native includes with restricted numeric overrides, closed vocabulary, cycles/resource controls and explicit conflicts. Project native reference/roots have containing-file bases but no reusable project-domain composition rules | Native lane qualified; whole-project composition rules still required by #155 |
| Convert OCAM/WFI examples through the ledger, preserving original text/provenance/hashes | Public migration API invokes the original PAF constructor, emits typed native TOML and verifies exact stored values; converted examples/evidence retain original PAF/CFG bytes, hashes and ledger. CFG values remain compatibility evidence, not invented scientific associations | Implemented/qualified within the documented import boundary |
| Record identical PAF duplicates; reject conflicting definitions without explicit resolution | Both identical WFI master-bias mapping duplicates remain distinct occurrences; different literals need an explicit original-line selection, with no silent first/last winner | Implemented/qualified |
| One immutable configuration for CLI/library; WAD attributes; resolved values/sources recoverable for the plan | Shared Python API/CLI produces owned serialized records, configuration plan fragments and restore checks. Native snapshots own typed values. Project plus standalone native reference can be frozen together; subset graphs can be frozen separately | Implemented for supported paths; combined reusable-project path remains incomplete (#155) |
| PAF/TOML exact scientific settings for both instruments/local overrides; rejection coverage | Actual constructors and selected CLI overrides match 585 OCAM / 249 WFI stored fields, including native types/float bits. Accepted negative cases cover missing/unknown fields, storage/unit/type errors, conflicts, cycles and spaces | Qualified native gate; does not demonstrate the missing combined-project composition path |
| Preserve PAF support/rollback and avoid a second defaults table | Ordinary mefpp/Pycavi still use the legacy path; opt-in helpers are not installed/linked into normal dispatch. No PAF removal, parameter change or new normal engine selection | Preserved |

WAD validation here is scoped to configuration attributes and the native catalog.
The review catalog remains a design/review notation, not a production ASDF schema.
General asset/image/task applicability and persistent exact-version plans are M3–M9
work at their existing boundaries. Their absence is not used to invent additional
M2 blockers. An immutable configuration plan fragment is not an executable plan.

## Source-confirmed blocker: project entry does not compose the qualified subsets

There are two implemented entry paths with a remaining connection missing:

1. `ConfigurationMigration.load_toml` calls the native reader, captures its complete
   source graph and freezes the resolved native configuration. It accepts the
   qualified native `entry.toml` and `local.toml` examples.
2. `ConfigurationMigration.load_project` delegates to the closed project authoring
   loader, which requires all project-domain declarations inline and permits only
   a complete standalone native schema-3 reference.

Exact source anchors at the reviewed baseline:

- `docs/architecture/proposed/m2/project-contracts/catalog.json`: closed project
  root; all declared domains required inline, no project/domain include construct.
- `validate_project.py:30–40`: unknown/missing authoring fields fail.
- `validate_project.py:151–154`: `native_consistency` rejects native `include` and
  `override_keys`, requiring one complete standalone version-3 file.
- `validate_project.py:198–221`: reads only project and optional standalone native
  reference; records their texts/hashes and authoring status.
- `Pycavi2/pycavi/pycavi/pycavi_configuration.py:338–364`: reuses that loader,
  independently requires one native source file, then freezes the project record.
- `mefpp2/ins/mef/common/mef_toml_bundle.c`: the working native composition and
  source-graph implementation; it is not connected to project-domain composition.

For example, replacing a project example's standalone native reference with the
already qualified native `entry.toml` or `local.toml` cannot pass the combined
project loader's explicit guard. A shared recipe or execution-domain subset also
has no project-level include/reference contract. This conclusion follows directly
from the source restrictions; no new failure run is claimed. The accepted tests
use a complete native reference for combined project cases and test native
composition separately. Their success is consistent with this gap.

Do not fix this by removing the guard alone or flattening files before recording
provenance. The integrated loader must reuse the native resolver and compare
readout declarations against its effective typed settings while retaining all
contributing sources and explicit override/conflict decisions.

## Accepted implementation chain and retained qualification

| PR | Increment | Tested implementation | Accepted integration |
|---|---|---|---|
| #147 | Native TOML compatibility reader | `b0ea0897ff2b5257eaf3bae0029b14a11a8f7152` | `0550fb90215c636cc6b881eb67e221c24b5ed876` |
| #148 | Native subset composition/allowlist | `d622bbec7e9784ab9fa6211080cfd4955ff3a08d` | `7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5` |
| #149 | Typed domains, units and owned source records | `920dd13251287c07ca9d9e3355e1cb9afcd38370` | `ed949cab4f70381a1e187c7be691026c7fecf01c` |
| #150 | Project/readout authoring and optional overscan | `3769f5196f9be2c2581673f89c61ae2a472167d3` | `0160ed181cd1e609f5e82cfab7932763b228f698` |
| #151 | Historical as-is architecture snapshot | Documentation-only | `a09bec7e6bc0d3fa8d82245db59aaf3063ac0d94` |
| #153 | Public migration, complete native source provenance and frozen records | `38f4f4d4bd05c4977f1624fc8737431527bdbe8a` | `c0bbcc5866b49d64fad6498a029429b35ada9953` |

GitHub reports #150 as closed rather than merged because its merge endpoint
failed. The accepted integration was a two-parent Git-data merge. Local history
confirms review head `0bc6ae1cd4cab4b30424cdbe957c9816f3fd05d8` is an ancestor of
main, is the second parent of `0160ed1`, and has exactly the same tree
`d854fdafeac07d598a0502e7153fed07e629c0d6` as that merge. Do not mistake the PR
metadata flag for missing source integration.

For #147/#148/#149/#150/#153, source comparison from the tested implementation to
the accepted review head found only Markdown changes (9/9/9/8/8 files respectively).
Retain their original target results; no test replay was needed for those receipts.

| Paired receipt | Retained verification boundary |
|---|---|
| [Native reader](m2-native-toml-paired-results-2026-10-30.md) | Both hosts: 585 OCAM / 249 WFI / 249 edge settings and 41 rejection/recovery cases |
| [Native subsets](m2-toml-subsets-paired-results-2026-10-30.md) | Both hosts: two focused checks, 16 composition profiles and 32 subset rejection/recovery cases |
| [Typed domains](m2-typed-domains-paired-results-2026-10-30.md) | Both hosts: three focused checks; 151 templates, 11 document/lifetime profiles and 25 domain/unit rejection cases |
| [Project/readout](m2-project-contracts-paired-results-2026-10-30.md) | Both hosts: six examples from two directories and 66 authoring rejection/recovery cases |
| [Migration](m2-migration-paired-results-2026-10-30.md) | Both hosts: two focused checks; exact original/local settings, immutable records and 21 migration rejection/recovery cases |

Counts overlap across increments; do not add them into a fabricated unique test
total or claim every historical suite was rerun on final main. Latest target runs
are Mac `mac-m2-migration-p7wrei4c` and Chapman
`chapman-m2-migration-b0zxlakk`, passing 2/2 with protected files/checkouts unchanged.
Earlier detailed paths and source revisions remain in the linked receipts.
Evidence is inspected owner-returned output; it does not imply independently
transferred/hash-audited target archives. Agent C17/scoped sanitizer evidence is
separate from target C90 results. No full dependency OOM/thread-safety/scientific
or Phase 3 acceptance follows. Corrected handoff #154 remains closed and its first
failed attempt remains preserved.

## Next bounded work and later-milestone limits

Complete #155 within the original M2 configuration boundary:

- Define reusable project-domain composition and connect the project entry to the
  accepted native subset resolver. Preserve complete single-file compatibility,
  explicit bases/versions/conflicts, and separate reduction/recipe/product profiles.
- Freeze every contributing project/native source and selection decision into the
  same CLI/library configuration record; preserve readout/header authority limits.
- Qualify focused direct/split/local native references under both project examples,
  shared project-domain reuse, conflicting/missing/unknown definitions, cycles,
  spaces and source/caller mutation/deletion. Reuse accepted numeric references;
  run only affected checks on the selected Mac and representative Chapman tools.
- Return to this checklist before proposing full M2 closure.

No new task execution, cwd-independent FITS/list pipeline, detector/HDU mapper,
scientific association policy, ASDF project publication, new numerical algorithms
or normal engine activation is part of this review. Optional/no-BPM semantics and
required M6a variances remain in force. Geometry-free and multi-amplifier numerical
execution still require the original M4–M6 work. M3 is not started or reordered.

The review document itself is ready for owner review. It records a remaining M2
requirement rather than seeking approval to weaken the gate. It does not implement
#155 or authorize merging/cleaning this documentation branch automatically.
