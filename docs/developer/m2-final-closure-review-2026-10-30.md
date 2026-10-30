# M2 final cumulative closure review — 30 October 2026

Reviewed as-is baseline: accepted merged main
`09a7aee4d69f04f5aeef954ff87c39d6f870d2d3`, tree
`c41aeab2643bbce3588845868596c2622141fc70`. The owner accepted PR #157 and returned
clean synchronized Mac and Chapman main, with its branch removed from both hosts
and GitHub, then authorized this review.

**Recommendation: accept M2 as complete within its original configuration scope.**
The reusable project/native integration missing in the
[earlier review](m2-closure-review-2026-10-30.md) is now implemented, target-qualified
and accepted through PR #157. No remaining blocker against the original M2
checklist was found. This recommendation is not owner milestone acceptance and
does not start M3 or authorize automatic merge/cleanup of this review branch.

## Review method

Inspect the [original M2 requirements and gate](../architecture/proposed/implementation-plan.md#m2--toml-subsets-and-configuration-migration),
merged Python configuration service, project catalog/validator, native composition
and build boundary, examples, affected test definitions and six paired receipts.
Verify review-head ancestry and documentation-only deltas after the tested
implementations. Preserve the earlier review and architecture snapshots at their
stated historical baselines. The
[latest snapshot](arch_snapshot/arch_snapshot.20261030T141656-0300.md) shows the
implemented configuration, ordinary reduction and bounded M1 service paths.

This is source/evidence inspection and documentation validation. It launches no
functional test, build, installation, reduction, tool qualification or historical
matrix replay. Accepted target results remain evidence at their exact revisions,
not a claim that every old suite ran again on final main.

## Original M2 checklist

| Requirement | As-is implementation and retained evidence | Disposition |
|---|---|---|
| Versioned domains and distinct reduction purpose, recipe and product profile | Native versions 1–3; typed version-3 instrument/detector, processing and product mappings; closed domain-v1 project/association/profile/recipe/execution/quality/readout declarations; project envelopes 1/2 | Met at the configuration boundary |
| Small project entry references reusable subsets; fewer files allowed | `_compose_project` combines complete domain-v1 declarations, accepts complete version-1 projects and version-2 complete/split projects. Both committed instrument projects share profiles and select native local-override graphs | Met; former #155 blocker resolved |
| Containing-file bases, explicit override rules, closed keys, versions and conflict diagnostics | Project includes, roots and native references use their declaring file. Disjoint/identical domains coalesce; conflicting domains fail with source identities; project replacement allowlist is empty. Native numeric overrides use the existing C allowlist/resolver. Cycles, symlink loops and graph limits are checked | Met; no silent last-wins or second numeric/default implementation |
| OCAM/WFI migration examples retain originals, conversion ledger and hashes | `migrate_paf` obtains stored settings through the original constructor, renders typed TOML and compares the native round trip exactly. PAF/CFG text and provenance are retained; CFG strings remain compatibility evidence | Met within the explicit import boundary |
| Identical PAF duplicates retained; conflicts need explicit selection | Both WFI mapping duplicates remain occurrences; conflicting literals require an original-line selection. Invalid/unused selections fail | Met |
| One immutable effective configuration for CLI/library, WAD attributes and recoverable settings/sources | `load_project` calls `load_toml` on the actual native graph, checks effective readout consistency, and freezes all project/native sources and domain contributors. CLI/library bytes agree; records survive caller/source edits and private source deletion; restore verifies identity and stored values | Met at the declared configuration-attribute boundary |
| Exact PAF/TOML settings and selected local overrides, with negative controls | Both instruments retain all 585 OCAM / 249 WFI stored values including float bits; original CLI supplies local override references. Accepted suites cover unknown/missing definitions, versions, types, units, ranges, conflicts, cycles, spaces and recovery; project/native combinations add 18 primary profiles and 24 rejection controls | Qualified by retained paired target evidence |
| Preserve PAF rollback and avoid independent defaults | Ordinary legacy Pycavi/mefpp remain available; config probes default OFF, native reader is not installed/linked into ordinary mefpp. No PAF removal, scientific setting change or installed engine activation | Preserved |

WAD checking remains configuration-attributes/native-catalog checking. A catalog
and immutable configuration fragment do not establish full image/task schemas,
resolved scientific assets or an executable plan. Those later requirements were
not part of the original M2 completion gate and are not added as new blockers.

## Why #155 is resolved

At the earlier baseline, the combined loader required inline project declarations
and one complete standalone native source. Native subsets worked independently.
At this baseline, `ConfigurationMigration._compose_project` defines the project
composition envelope and captures its sources; `load_project` invokes the existing
C reader through `load_toml` for complete, entry and local native references.

The existing `native_consistency` helper receives a complete typed view rendered
from **resolved stored values**. Geometry/subtraction contradictions still fail;
the fix did not merely remove the old standalone-file guard. The standalone
legacy authoring helper keeps its narrower contract; the integrated CLI/library
path is the supported composition route.

ConfigurationMigration and `freeze-project` use the same path. Tests cover both
instruments across full/entry/local native graphs and complete-v1/complete-v2/split
project layouts, shared-domain reuse, source contributors, containing-file bases,
closed versions/keys, graph limits, readout contradictions and saved-record recovery.
Native parsing remains process-isolated; Python recovery does not claim repeated
in-process native hosting or thread safety. Issue #155 is closed with correction
and actual target evidence, independently of this milestone acceptance decision.

## Accepted chain and evidence

| PR | Increment | Tested implementation | Accepted integration |
|---|---|---|---|
| #147 | Native compatibility reader | `b0ea0897ff2b5257eaf3bae0029b14a11a8f7152` | `0550fb90215c636cc6b881eb67e221c24b5ed876` |
| #148 | Native composition | `d622bbec7e9784ab9fa6211080cfd4955ff3a08d` | `7e665da170e2e1af9f96a97e9f5bc2f6ebcfeef5` |
| #149 | Typed domains and owned sources | `920dd13251287c07ca9d9e3355e1cb9afcd38370` | `ed949cab4f70381a1e187c7be691026c7fecf01c` |
| #150 | Project/readout authoring | `3769f5196f9be2c2581673f89c61ae2a472167d3` | `0160ed181cd1e609f5e82cfab7932763b228f698` |
| #153 | Migration and frozen provenance | `38f4f4d4bd05c4977f1624fc8737431527bdbe8a` | `c0bbcc5866b49d64fad6498a029429b35ada9953` |
| #157 | Integrated project/native composition | `d0ab19e91b46e6fe6e21c541af99c21ed35029b4` | `09a7aee4d69f04f5aeef954ff87c39d6f870d2d3` |

Each accepted review head is an ancestor of final main. Post-test review deltas
are Markdown only (9/9/9/8/8/12 files respectively). PR #157 accepted review
`c98e760fd0594a277d94271dd1075037d929eda7` and its merge have identical files.
PR #150's GitHub closed flag is historical merge-endpoint metadata; its accepted
source integration is present in ancestry, as explained by the earlier review.
PRs #151/#156 preserve historical snapshot/review documentation.

| Paired receipt | Retained boundary |
|---|---|
| [Native reader](m2-native-toml-paired-results-2026-10-30.md) | Exact original settings and 41 negative controls |
| [Native subsets](m2-toml-subsets-paired-results-2026-10-30.md) | 16 composition profiles and 32 subset negative controls |
| [Typed domains](m2-typed-domains-paired-results-2026-10-30.md) | 151 field templates, 11 document/lifetime profiles and 25 domain/unit controls |
| [Project/readout](m2-project-contracts-paired-results-2026-10-30.md) | Six examples from two directories and 66 authoring controls |
| [Migration](m2-migration-paired-results-2026-10-30.md) | Exact migration, duplicate/conflict evidence and 21 rejection controls |
| [Project/native composition](m2-project-composition-paired-results-2026-10-30.md) | Latest regression plus integrated 18-profile/24-control composition suite |

Latest Mac: `mac-m2-project-composition-c04okrlf`, 2/2 passed in 27.97 s.
Latest Chapman: `chapman-m2-project-composition-s5e5inwh`, 2/2 passed in 19.61 s.
Both reported protected installed files/checkouts unchanged. Full paths/log
locations remain in the paired receipt. Times identify runs, not benchmarks.
Counts overlap; no aggregate unique test count is claimed.

Target evidence is inspected owner-returned terminal output, not independently
transferred/hash-audited archives. Agent C17/scoped sanitizer checks remain
separate from target C90 results. No parser/dependency-wide OOM, concurrency,
safe in-process Python hosting, scientific or Phase 3 qualification is implied.
The corrected nested installed-module lookup (#154) and failed attempt remain
preserved; use actual source/host evidence rather than guessing layouts.

## Owner decision: retain JSON for now and follow the plan

After inspecting the snapshot, the owner explicitly instructed: “Keep the JSONs
for the moment. But do not depart from the current plan and good programming
practices.” Retain existing `configuration.json`, `plan-configuration.json` and
`COMPLETE.json` outputs. Human-authored configuration remains TOML. JSON encodes
immutable effective records; it is not essential to immutability itself.

JSON was introduced in PR #153 as an implementation choice, without a separate
prior owner format decision. The owner's present instruction permits retaining
it for now; it does not establish permanent JSON persistence. The existing M7
plan still specifies ASDF project persistence. It currently makes no explicit
promise to remove every JSON file, and this review invents no such requirement
or immediate format rewrite. Any proposed transition/compatibility decision must
be made explicit at its applicable stage before implementation.

Follow the existing plan and sound programming practices: reuse authoritative
parsers and validation, preserve types/units/ownership and diagnostics, validate
changed behavior appropriately, and keep changes bounded. Discuss and record
proposed departures from scope, order, formats or acceptance criteria before
implementing them; implementation convenience does not approve a departure.

## Next decision and preserved limits

Owner acceptance of this recommendation closes M2 at the configuration boundary.
After that acceptance and authorized integration, continue in the existing order
at M3: explicit input/list/calibration/configuration and output/work/log paths,
with a read-only project overview/inspection command and the original gates.
No M3 code, new test run or execution begins from this review alone.

The ordinary reduction path remains unchanged. ASDF persistence stays M7;
optional bindings remain M10; detector identity/layout and new services/variance
stay at their existing milestones. Optional BPM / required M6a variances remain
in force. Unresolved qfits #125 and dependency-memory #144 retain their separate
scope; configuration completion does not close them. Preserve all original data,
private runs and selected installations. This review authorizes no scientific
policy change, activation, automatic merge or branch cleanup.
