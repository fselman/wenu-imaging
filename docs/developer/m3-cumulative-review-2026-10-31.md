# M3 cumulative review — 31 October 2026

Subsequent [paired inspector qualification](m3-inspector-stages-paired-results-2026-10-31.md)
passed 21/21 on both actual hosts at 0d8f2978a4ef4c78c47f1526b48e03d77351c024.
The [final cumulative review](m3-final-closure-review-2026-10-31.md) recommends M3
closure pending owner acceptance. Earlier gap/target-pending statements below
retain their original baseline context. No M4 implementation starts here.

Subsequent owner-authorized [inspector-stage completion](m3-inspector-stages-2026-10-31.md)
is implemented with agent 21/21 checks. Actual paired target qualification is
pending; this original baseline review remains historical evidence of the gap.
M3 is not yet declared closed.

Reviewed baseline: accepted merged main
`3a61df627edfdbb1ef43cc3c956dff74bd28c066`.
Owner request: review cumulatively, close M3, then review M4. Closure is conditional
on the original gate being met; this review does not redefine that gate.

**Disposition: retain M3/#159 open. The native explicit-path execution gate is
qualified, but the original processing-sequence inspection deliverable is incomplete.**
Complete that bounded inspector integration before recommending M3 closure.
This is an existing requirement, not a new general debugging campaign.

## Method and evidence level

Read the [original M3 requirements](../architecture/proposed/implementation-plan.md#m3--explicit-paths-and-project-visualization-commands),
production path/inspection modules, the actual native path adapter and its callers,
test definitions, paired receipts and issue #159 history. Check GitHub merge state,
Git ancestry and changes after tested revisions. No build, functional test,
observational processing, installation, package/tool change or historical matrix
replay is performed by this review.

All four tested revisions below are ancestors of the reviewed baseline. GitHub
reports PRs #161/#167/#170/#173 merged. The inspector/path modules and inspector
contract are unchanged since their paired-tested revision. Since the latest
safety-tested source, the only change under mefpp2 and the Python package is
`mefpp2/README.cmake.md`; there is no executable-source change in that boundary.

| Increment | Tested source | Accepted merge | Retained target evidence |
|---|---|---|---|
| Inspector, corrected canonical fixtures | `2c820effff393d5ea4e1555439397ef7c7a6cda6` | #161, `ded31e876582dcbe044c2b99167c9d36e8c6ee03` | [15/15 on each target](m3-project-inspection-paired-results-2026-10-30.md) |
| Native explicit paths | `113156b94fe68f7bf2848c93ecd7451551db2984` | #167, `d8f855106edda9639d6a0ad4b2ba2af964a11b84` | [2/2 Mac and Chapman4](m3-native-paths-paired-results-2026-10-30.md) |
| Forced-swap correction and native-path regression | `471f42e19e304e16872291172535e855a2f826d9` | #170, `e2460fb72bdbe69f92c7da8994a81d21928569b5` | [2/2 on each target](qfits-swap-paired-results-2026-10-30.md) |
| Allocation/format safety and native-path regression | `87ed266a109741c4998bfc8c978d07c9306f0091` | #173, reviewed main | [4/4 on each target](native-safety-paired-results-2026-10-30.md) |

These paired receipts are inspected owner-returned terminal evidence, not a new
independent read of all raw target archives. They protect installed module,
configured engine/configuration and checkout state. Agent C17/sanitizer evidence
is separate; no broader memory, concurrency, scientific or Phase 3 acceptance is
inferred. Retain all failed and corrected runs at the receipt locations.

## Original requirement checklist

| Original requirement | As-is implementation/evidence | Disposition |
|---|---|---|
| Explicit input/list/calibration/configuration and output/work/log paths through adapters, context, loaders and writers | `mef_paths.c/.h`, production `mef_bb_load`/`mef_engine`, `_at` loaders and output helpers. Actual C executable processes OCAM/WFI tiny fixtures; Python is only the test driver | Met at the native execution boundary |
| Resolve user arguments once; document-relative references use their declared base | Native canonicalization captures invocation paths; Python `PathResolver.argument/reference` uses explicit bases. Existing M2 composition handles containing-file configuration references | Met for implemented formats; ASDF resolver remains M7 |
| Legacy relative lists retain original execution base; unknown bases reported | Native explicit mode requires `--list-base` for relative members. Inspector records/reports unknown bases and keeps ordered raw membership | Met |
| New path has no mandatory parent/library chdir or local PAF discovery | C explicit mode requires selected PAF/output/work, resolves before processing and preserves cwd. Inspector also has no chdir. Legacy Pycavi wrappers remain compatibility clients | Met for the new native/inspection path; replacing notebook execution is M9, not an invented new M3 prerequisite |
| Separate read-only raw/calibration roots and writable output/scratch/log | Native paired tests protect bytes/modes/mtimes, empty unrelated callers and selected output paths; input/calibration reuse is exercised | Met within documented serial/private-attempt limits |
| Detect output collisions and preserve legacy FITS provenance bounds | Distinct same-basename/duplicate selections and existing output sentinels are rejected. Full paths remain in logs rather than being inserted into unsafe legacy cards | Met; #125 remains separate |
| Same request from two unrelated caller directories preserves pixels and relevant metadata | Native tests compare full calibration/science, calibration reuse and split profiles; independent arrays plus exact legacy/explicit pixels/cards/order | Met; generated identifiers are normalized only as documented |
| Recursive read-only project inspection from any caller | `inspect_project` and outer CLI share the path. Paired fixture tests cover nested membership, links and explicit configs | Met |
| Preserve raw metadata, mapping authority and conflicts | Selected CFG raw/interpreted values, primary/local HDU fields, selected cards, duplicate/conflicting-card diagnostics and reported-unverified authority | Met for the bounded legacy adapter; hardware identity is M4 |
| Instrument/target/filter/exposure, detector coverage, partitions and ordered membership | Per-HDU rows, dimensions, EXTNAME and selected columns; ordered repeated members and canonical shared assets retained | Met as reported header/layout evidence, not physical identity validation |
| Calibrations and products in a processing sequence, including preprocessing, normalization and WCS | List roles exist, but file/link rows are generic `unclassified-file`/`linked-reference`. Product-category cards are captured without constructing those stage/association views | **Incomplete: original M3 deliverable** |
| Overview and drill-down by partition/exposure/detector/stage; selected columns/filter/sort/export | Current controls work for list-role/header rows. `--stage` cannot select a represented preprocessing/normalization/WCS sequence because those roles are not built | Existing views qualified; stage-sequence integration incomplete |
| Counts, shared calibration references, missing products, attempts and honest completion/failure evidence | Links are flat references; log/marker entries are `present-uninterpreted`, completion `unknown`. Honest unknown is correct, but the promised associated-product/missing-stage overview is not represented | Partly met; needs bounded evidence-linked stage records, not success inferred from names |
| Incomplete/malformed/dangling/cyclic projects, diagnostics and bounded traversal; no arrays/writes/bulk hashes/reductions | 15 paired groups include limits, alias/cycle/malformed cases and traps on image/table payload access, plus preservation assertions | Met for current inspector; extend only for missing stage views |
| Preserve compatibility/rollback and old products | Legacy path, arenas, lists/links and installed selections retained; new native runs use isolated attempts | Preserved |

## Why the remaining inspector gap is real

The original M3 text explicitly requires associated calibration products followed
by native preprocessing, normalization and WCS products, with stage drill-down
and available attempt/completion evidence. It is not satisfied by merely printing
the words “normalization/WCS completion: unverified”.

Current source in `Pycavi2/pycavi/pycavi_project.py` establishes the limit:

- `LIST_ROLES` categorizes six input list names, not generated product stages.
- `headers` captures `PRODCATG`/`ESO PRO CATG` and selected cards; it does not
  build processing-stage relationships from them.
- `walk` gives discovered FITS generic file/link roles and records markers/logs
  without interpreting their contents. There is no linked per-exposure
  preprocessing/normalization/WCS overview.
- The contract's nested-membership case requires those marker/log completion
  states to remain unknown; it does not test explicit product-stage evidence.

This is source-confirmed missing functionality, not a newly executed runtime
failure. Existing tests passed their declared narrower contract. Do not label
their truthful unknown states defective or turn ordinary historical logs into
validated product receipts.

## Review validation

The seven changed/new files are Markdown only. All relative file links resolve
and changed-file whitespace checks pass. The four accepted PR review heads are
ancestors of reviewed main and each has exactly the same Git tree as its merge.
The inspector source/contract comparison and latest native-source comparison
described above pass. These are read-only source/document checks, not a new
functional run or proof that the missing inspector functionality exists.

## Smallest completion increment, within original M3

1. Extend the read-only legacy adapter to represent declared calibration and
   per-exposure processing/product references, together with the evidence source
   for every relation. Reuse existing instrument configuration, list/link and
   product metadata semantics. Do not run association selection or normalize
   observations during inspection.
2. Present calibration -> preprocessing -> normalization -> WCS stage views,
   showing missing, unresolved and existing-unverified references explicitly.
   Where the legacy material supplies no trustworthy relation, show unknown;
   do not manufacture a connection or certify processing from suffixes.
3. Attach available explicit attempt/result evidence with its source and limits.
   Absence of evidence remains unknown. Planned, existing-unverified and actual
   validated/published evidence must not collapse into “file exists = success”.
   Do not introduce a new durable store, ASDF runtime or full executor here.
4. Add focused synthetic inspection controls for shared/missing calibrations,
   distinct exposure stage references, misleading suffix/log text, conflicting
   evidence and deterministic stage drill-down. Retain existing no-array/no-write,
   caller-base and coverage assertions. This exercises `inspect_project`/CLI,
   ConfigParser and Astropy headers; it launches no native engine or solver.
5. Qualify the changed inspector once on selected Intel Mac and representative
   Chapman, retain evidence, then repeat the cumulative documentation review.
   Reuse native-path/safety evidence unless relevant code actually changes.

Do not add #23/#24 timing fixes, #64/#66 build bookkeeping, #125/#128 general FITS
work or another allocator matrix as closure prerequisites. The original missing
inspector requirement is tracked by existing #159; no duplicate defect ticket is
needed. No original requirement is moved to M7/M9 merely to close M3.

## Scope boundaries and M4 handoff

ESO OB start, template start and exposure/shutter-open start are separate fields;
OB/template IDs are grouping/provenance, not native processing prerequisites.
Pycavi owns grouping/association with support for ESO and other schemes. mefpp
receives selected input/calibration lists and basic compatibility checks. This
review performs no timestamp replacement or new grouping-policy implementation.

The retained legacy Python wrapper's staging/chdir is not evidence that the new C
explicit path failed. Notebook/shared executor replacement remains M8/M9. Likewise
grouped numerical adapters belong to M5/M6, physical detector mapping to M4,
ASDF persistence to M7 and Python bindings to M10.

The [M4 readiness review](m4-readiness-review-2026-10-31.md) records the next
original milestone and its current boundaries. It is preparatory source review,
not M3 acceptance, M4 implementation or milestone advancement. Recommend M3
closure only after the missing inspector boundary is qualified and reviewed.
