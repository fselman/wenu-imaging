# M3 final cumulative closure review — 31 October 2026

31 October owner requested [direct --summary output and aligned titles](m3-inspector-summary-2026-10-31.md)
before M3 closure. Compact exposure rows/diagnostic counts now need no wrapper;
detailed tables also use measured spaces. Agent suite passes 24/24; actual Mac,
then representative Chapman presentation qualification remains pending. Prior
22-group reader and real-tree evidence stay valid; no reader/C/scientific change.
PR #178 stays draft for the added interface gate. No installation or activation;
owner acceptance/merge-clean precedes M4 review.

31 October #180 [corrected paired and real-tree receipt](m3-eso-header-paired-results-2026-10-31.md): source
f7967fd1ee93f2a5a1a4faa227cadd460c054fa5 passed 22/22 on selected Intel Mac
(4.788 s) and representative Chapman4 (2.405 s), with installed files and clean
main preserved. Actual CN Ori redisplay now retains all five 80 s r_SDSS headers,
33 HDUs each, while retaining 36 warnings and one separate missing master-flat
reference. The original-scope M3 closure recommendation is reinstated for owner
acceptance; PR #178 is ready. No test replay/install/host sync for this receipt.
Separate owner merge/cleanup precedes M4 review; earlier held/pending notes are
historical. #181 remains a separate suffix-convention follow-up.

31 October subsequent actual-tree finding #180: nonstandard ESO telemetry
caused strict inspector verification to discard otherwise readable HDU metadata.
The [bounded correction](m3-eso-header-inspection-2026-10-31.md) retains diagnostics and readable fields,
with no fixes to source files or image reads. New regression fails before; agent
corrected suite passes 22/22. Corrected Mac/Chapman qualification and repeated
bounded Chapman tree display remain pending. Hold the earlier M3 closure
recommendation and PR #178 in draft; preserve all earlier evidence. No native,
scientific, installation or M4 work. Earlier 21-group receipts retain their scope.

Accepted native baseline: main `3a61df627edfdbb1ef43cc3c956dff74bd28c066`.
Current corrected inspector candidate: PR #178 source
`f7967fd1ee93f2a5a1a4faa227cadd460c054fa5`, tree
`2a47848d07ce083252abfb38e2d37a1d1b2464a9`.

**Recommendation: accept M3 as complete within its original explicit-path and
legacy project-inspection scope.** The gap in the
[earlier baseline review](m3-cumulative-review-2026-10-31.md) is implemented and
has passed the required paired target gate. No original M3 requirement is waived
or moved to M7/M9 to obtain this recommendation. Owner acceptance and separately
instructed merge/cleanup remain pending; no M4 code starts from this review.

## Original checklist, with the completed boundary

| Original requirement | Completion evidence | Disposition |
|---|---|---|
| Explicit input/list/calibration/configuration and output/work/log routing through adapters, context, loaders/writers | Accepted PR #167 native CLI/engine/path helpers and [paired receipt](m3-native-paths-paired-results-2026-10-30.md), retained native-path regressions through PR #173 | Met |
| Invocation-relative arguments once; declared containing-document/reference bases | Native explicit resolver, Python PathResolver and accepted M2 containing-file configuration resolver; unknown legacy member bases are rejected/reported | Met for supported formats; ASDF persistence/resolution stays M7 |
| Replace mandatory parent/library chdir and local PAF discovery in the new path | New C execution and inspector work from unrelated callers with selected PAF, no parent/library chdir and unchanged cwd | Met; compatibility Python clients remain available, M9 executor replacement stays M9 |
| Separate read-only raw/calibration roots and writable output/work/log locations | Native successful/rejection profiles protect input/calibration/caller state and explicit destinations | Met within documented serial/private-attempt limits |
| Duplicate-basename/output collision protection without new long FITS path cards | Native duplicate/existing-output rejection and legacy metadata comparison; inspector reports ambiguous product expectations without choosing one input | Met; general qfits #125 remains separate |
| Same explicit request from two unrelated directories, equivalent pixels/relevant metadata | Native OCAM/WFI independent arrays and exact legacy/explicit comparisons, 16 successful profiles/14 rejections and 51 CLI cases | Qualified by retained paired results; not rerun by this review |
| Recursive read-only legacy project overview, raw/normalized metadata authority and conflicts | Existing list/link/CFG/header adapter, selected columns, shared canonical assets, duplicate/primary-local conflict diagnostics | Met at the legacy evidence boundary |
| Instrument/target/filter/exposure, reported detector coverage, partitions and ordered membership | Existing mapped fields, per-HDU rows, explicit list source/line/member ordering and preserved repeated memberships | Met; physical detector mapping remains M4 |
| Associated calibration products followed by preprocessing, normalization and WCS stage views | New build_stages integrates declared links/producer roles/category cards, per-exposure expected locations and shared client conventions; in-place normalization explicitly shares its file | Former gap resolved by [21/21 paired qualification](m3-inspector-stages-paired-results-2026-10-31.md) |
| Overview/drill-down by partition/exposure/detector/stage, columns/filter/sort/table/export | Original view controls plus calibration role/relationship/completion columns and exact --exposure input filtering; --stage now selects processing stages | Met by paired CLI/library and caller-independence checks |
| Missing/unbuilt/shared products, recorded attempts and honest completion distinctions | Broken declared links, unavailable expectations, unknown bases, conflicts, reported-unit/header evidence and partition-only uninterpreted logs/markers retain their source and limits | Met for legacy evidence; no file/log/name claim is promoted to validated/published state |
| Incomplete/unreadable/malformed/cyclic references and truthful bounded coverage | Existing traversal/text/header/HDU limits plus bounded stage records and diagnostics; inspector-only no-array/no-write traps and preservation assertions | Met by the 21-group paired suite |
| Preserve numerical behavior and existing products/rollback | Shared pure naming/unit helpers preserve original/updated normalization and WCS function-body arrays/cards on both targets; native source unchanged; installed selections and old arenas remain intact | Met within stated functional scope |

The inspector's location conventions indicate expected paths, explicitly not
verified historical input identity. Only declared links or reported category
evidence establish the stated kind of reference/role; calibration suitability and
successful processing are not inferred. Legacy material without trustworthy
validation/publication records remains unknown. Reading that material must not
create such records. M7 adds durable results/history; it does not retroactively
make old files independently validated. Future dark/linearity/fringe views extend
the same interface when their actual services/records exist, as the plan specifies.

## Cumulative evidence and source continuity

| Boundary | Actual source/evidence | Current review implication |
|---|---|---|
| First inspector | `2c820effff393d5ea4e1555439397ef7c7a6cda6`, 15/15 on both targets, accepted #161 | Its controls are retained in the new 21-group suite |
| Native explicit paths | `113156b94fe68f7bf2848c93ecd7451551db2984`, 2/2 on both, accepted #167 | Original execution gate satisfied |
| Swap correction plus native-path regression | `471f42e19e304e16872291172535e855a2f826d9`, 2/2 on both, accepted #170 | Bounded native path/dependency behavior preserved |
| Allocation/format safety plus native-path regression | `87ed266a109741c4998bfc8c978d07c9306f0091`, 4/4 on both, accepted #173 | Latest native boundary; no new C changes in #178 |
| Completed stage inspector and shared client conventions | `0d8f2978a4ef4c78c47f1526b48e03d77351c024`, Mac 21/21 in 4.639 s, Chapman4 21/21 in 2.702 s | Original missing inspector boundary qualified |
| Nonstandard ESO header correction and actual-tree redisplay | `f7967fd1ee93f2a5a1a4faa227cadd460c054fa5`, Mac 22/22 in 4.788 s, Chapman4 22/22 in 2.405 s; five real science headers each readable through 33 HDUs, warnings retained | #180 correction qualified; no missing-reference repair or compliance claim |

Earlier accepted review/merge ancestry and equal-tree checks are retained in the
baseline review. Current candidate descends from that baseline. New source differs
only at the documented Python inspector/client/test boundaries; no native
executable source has changed since accepted #173. The following receipt/review
commit is Markdown only, verified against the tested candidate. It needs no
rebuild, reinstall, source-matrix replay or target checkout synchronization.

Both actual hosts stayed on clean main `3a61df6`; exact candidate git archives were
tested separately. Returned runner receipts report installed module/configured
engine/config preservation. Target evidence remains owner-returned terminal
output, not independently downloaded raw archives. Agent checks, retained failed
oracle #179 and all target files remain preserved at their recorded locations.

## Scope and next review

ESO OB start, template start and shutter-open exposure start retain distinct
meanings and IDs. Pycavi owns general grouping/association, accommodating ESO and
other schemes; mefpp processes selected science/calibration lists with basic
compatibility checks. No timing fix or grouping policy was introduced here.

Accepted Stage 2/2.1, common mosaic normalization, signal units, optional BPM /
required later M6a variance rule and legacy scientific parameters remain intact.
No installed activation, full installed-package/solver orchestration, detector
identity, whole-engine memory/concurrency, scientific or Phase 3 acceptance is
claimed. #23/#24, #74 residual facilities, #116, #125/#128 and unrelated build or
gain-policy work retain their separate gates, not new M3 closure prerequisites.

After owner acceptance and authorized integration, continue with the
[M4 detector/layout review](m4-readiness-review-2026-10-31.md): explicit detector
identity and per-file mapping, primary/one-extension/MEF support, independent
calibration maps, health/selection/result separation and preserved normalization
reference context. Review concrete interfaces and tiny fixtures before M4 code.
Do not begin M5 services, M7 ASDF persistence, M8 association or M9 executor early.
