# M1 closure review — 29 October 2026

## Decision proposed

Recommend closing **M1: typed configuration and explicit ownership** within its
documented foundation scope. The required template, typed snapshots, owned
lifecycles, compatibility adapters and first concrete operation are implemented,
accepted incrementally and merged. This review finds no remaining M1 foundation
implementation item that needs another test run before owner closure review.

This is a proposed milestone disposition, not owner acceptance of M1 and not
authorization to merge this document or start M2 implementation. After acceptance,
follow the original sequence: M2 TOML, M3 paths/inspection, M4 detector layouts,
M5 remaining calibration extraction and M6 science processing. No extraction is
brought forward. The later variance/QC/linearity/dark/fringe milestones remain
unchanged.

Review baseline: accepted main
`bacfa24fce45c0e7957bbc55f9cb6abfc7027219`, with owner-confirmed clean,
synchronized Mac and shared Chapman checkouts. The
[implementation plan](../architecture/proposed/implementation-plan.md) is
controlling; the M1 section/gate is assessed below without adding or removing
requirements. Earlier dated incremental notes saying M1 was incomplete describe
their historical delivery, not this cumulative review.

## What was reviewed; no new execution

Read the M1 plan/template and implementation contracts, the actual public
internal headers for configuration/runtime/CLI/input/bias, the M0/M0a WAD
review vocabulary, all six paired M1 receipts, and GitHub merge metadata for
PRs #136, #137, #138, #140, #141, #142, #143 and #145.
Confirmed #144 remains open. Reviewed source identities are pinned by the
baseline commit above; no mutable external source determines this disposition.

This is document/source/retained-evidence review. No native build, functional
test, numerical recomputation, tool qualification, package install, project
inspection scan or observational FITS read was executed for closure. Earlier
target receipts are inspected owner-returned terminal evidence, not newly
transferred/hash-audited target archives. Reuse their stated limits.

## M1 deliverables and gate checklist

| M1 requirement | Assessment | Implementation and retained evidence |
|---|---|---|
| Common ANSI-C90 operation template and fixed service names | Met for the foundation | PR #136; [template and checklist](../architecture/proposed/m1/README.md); real bias service in PR #145 exercises the pattern, not just declarations |
| Typed immutable scientific/configuration settings, keeping the PAF adapter | Met within constructor-mapped scope | `mef_config`, private typed detector records, field catalog and original PAF loader; [config contract](../architecture/proposed/m1/config-snapshot.md), PR #137 |
| Separate configuration from request bindings and mutable processing work | Met for the new boundaries; legacy compatibility retained | Config excludes loaded images/cubes, traversal state and work statistics; CLI request preserves raw bindings/flags, resolved request carries selected image/calibration descriptors, context owns independent config/request; old recipe still uses mef_bb |
| WAD conceptual field mapping, units and status semantics | Documented in the crosswalk below | Existing retained field ledger plus actual header vocabulary; no runtime ASDF/WAD schema conformance is claimed or required by this mapping |
| Observable full-stored-precision effective settings | Met | `mef_config_dump`, CLI dump and exact old/adapted comparisons; 585 OCAM, 249 WFI and 249 edge values, both actual PAF constructors and synthetic overrides |
| Owned config/request/context/result/error construction and destruction | Met for new owners | PRs #137/#138; copied arrays/strings, independent contexts, occupied-output guards, NULL-safe/partial cleanup and independent result/error lifetimes |
| Capture real CLI bindings, numeric overrides and informational behavior | Met for compatibility capture, not new dispatch | PR #140 uses the actual loader, original ordered argv and stored post-override settings; all 51 CLI cases pass on both targets; -d remains print-and-continue |
| Resolve legacy file/list members without hidden cwd changes | Met for the explicit M1 adapter | PR #143 reuses the parser, explicit original member base and supplied catalogue; ordered duplicate expansion and seventeen cases from two unrelated directories pass; general resolution remains M3/M4 |
| Explicit calibration roles and selected/omitted BPM state | Met for descriptor validation and first service | PR #142 validates/copies roles and choices; input adapter checks selected file access; bias service permits omission and rejects unsupported selected calibration application |
| One concrete service through validation/calculation/postcondition/qc/ownership pattern | Met within declared one-detector compatibility scope | PR #145 `mef_cal_bias` returns independent owned signal/request/QC, uses the shared legacy bias kernel, preserves scan QC and explicitly reports pre-M6a unavailable variance |
| Success, invalid/occupied output, partial construction, allocation/processing failure and lifetime controls | Met for changed owners and supported processing paths | Accepted focused source-defined controls, per-object accounting, synthetic rejection failures and exact bias comparisons; dependency-wide allocator safety remains explicitly limited by #144 |
| Actual Mac/representative Chapman verification and preserved rollback | Met within retained C90 scope | Latest implementation f5858310e505bfc1b137491dc35676b9245ce674 linked normal engine/probes and passed all five focused tests on both targets; PAFs, installed software, reference products and prior evidence are retained |

The checklist does not equate explicit C state with reentrancy, descriptor
validation with FITS applicability, or a constructed result with a published
product. Nor does it require all calibration/science operations to be extracted
during M1: those remain M5/M6. Individual accepted PRs implemented the boundary
incrementally; their cumulative assessment is the purpose of this review.

## Native-to-WAD conceptual crosswalk

The complete constructor-key/native-target/storage/conversion map already lives
in [effective-settings-baseline.json](../architecture/proposed/m1/effective-settings-baseline.json)
and the [typed-state split](../architecture/proposed/m1/typed-state-split.md).
The table below maps those owners and actual native fields to the existing
[WAD project vocabulary](../architecture/proposed/wad-processing-project.md).
WAD names here describe concepts from that review vocabulary, not newly frozen
JSON properties, tags, schema IDs or a public ABI.

| Native owner/fields | WAD concept | Units, authority and status rule |
|---|---|---|
| `mef_config`: constructor-mapped scalars, small arrays, detector settings and header/prefix strings | Configuration settings and compatibility; instrument/detector and product-mapping domains | Preserve source C types, object bits, legacy parameter/coordinate conventions and original strings. Configured gain/RON remain configured assumptions, not measured QC. This snapshot has no unit-object or source-ledger runtime schema; canonical unit declarations/composition belong to M2 |
| `mef_cli_view`: base_dir, original argv, bindings, save/subtract/selector flags; captured effective config | Configuration sources/compatibility plus request paths and requested recipe behavior | Strings retain bytes and NULL versus empty; flags/derived values preserve actual stored integers. Raw legacy xtnum=0 can mean all extensions; it is not silently converted into primary HDU 0. No executed-correction or publication claim |
| `mef_image_ref`: asset_record_id, detector_id, resolved_path, hdu_index, extname/extver | Asset reference/location and detector/image selector | IDs are opaque supplied identities, never inferred from filename/HDU. Physical HDU index is zero-based, with 0 meaning primary. Metadata support for 0 does not mean the first bias service processes primary images. Paths are explicit absolute Unix paths; existence/applicability are separate checks |
| `mef_request_spec`: operation/version, ordered inputs/calibrations, work/output/log paths | Task operation/version, ordered membership and explicit execution destinations | Preserve order/duplicates. Operation version is not schema, project or asset version. Request construction does not run work, create files, freeze a project plan or independently verify exact-version record resolution |
| `mef_resolved_request_spec`: calibration_roles, bpm_selections | Selected calibration type and explicit per-detector mask choice | Selected and omitted are distinct states; missing selected references fail. Structural role matching is not scientific applicability or evidence of application. No implicit default rediscovery in this boundary |
| `mef_context`: independent config and request; private work owned by operation | Executor's resolved task/configuration state | Configuration/request outlive their callers through copying. Mutable scratch is private to execution. No project graph mutation, ASDF object or scheduler is introduced |
| `mef_result`: operation and copied product-reference descriptors | Returned result/product-reference metadata | Metadata constructor success means valid owned metadata only; it is not completed numerical processing, verified FITS or published project state |
| `mef_bias_input` and `mef_bias_result`: explicitly mapped raw planes, output signal and copied request | Operation-specific image payload and result linked to selected input identities | Raw/result signal is ADU by this operation's contract; shape/type come from the selected in-memory image payload. Configuration detector index is explicitly zero-based and independent of physical HDU. Result is a private in-memory image, not an invented product record/version |
| `mef_bias_qc`: frame_mean_average/sigma, rejection_low/high, product_median/stdev, scan_median/stdev, counts/decisions | Result assessment with retained measurement/selection evidence | Signal/scan statistics are ADU; counts are frames; decisions correspond to original ordered frames. Method is retained legacy bias processing, with strict rejection endpoints and historical lower-median behavior. Final WAD method/version serialization and new estimators remain M5a/M7 |
| `variance_state`, `bpm_selection`, bpm_applied, ron_estimate_available | Uncertainty/mask/correction availability and configured-versus-measured authority | Bias explicitly reports legacy variance unavailable, BPM omitted/not applied and RON estimate unavailable. Unavailable is never zero variance/noise or a scientific quality pass. M6a makes supported new-chain variance required |
| `mef_status`, `mef_error` | Operation outcome/diagnostic for later attempt records | CONFIG/INPUT/UNSUPPORTED/MEMORY/COMPUTATION/IO identify the native failure category. Primary status is authoritative if secondary error allocation fails. CANCELLED is a reserved status, not implemented cancellation. MEF_OK applies to the called function's contract, not project publication or scientific acceptance |

Generic native image descriptors deliberately do not yet contain a complete
WAD image record with shape/type/unit objects, correction history, variance/mask
selectors, content identities and provenance. Those remain their existing
M2/M4/M6/M6a/M7 adapters/contracts. This is a field-to-concept mapping, not an
assertion that the full future model already exists or a reason to embed ASDF
objects in C kernels.

### Preserved native unit conventions

For the configuration groups that carry numbers rather than FITS mapping text,
M1 retains the existing recipe interpretation: chip/frame and rejected-sample
counts are counts; scan/trim/reference-pixel/kernel sizes are pixel quantities;
bias/flat input thresholds and saturation level are raw ADU; kappa/pixel-sigma
multipliers, saturation fraction and relative BPM-response thresholds are
dimensionless. The configured gain/RON enter the retained noise expression as
electrons per ADU and electrons respectively. Detector CRVAL quantities retain
the legacy WCS degree convention and CRPIX quantities retain pixel units,
including the old conversions.

These describe existing native use, not a calibration/header-unit audit or new
parameter values. Detector scan/trim bounds retain their one-based FITS
convention; other region bounds retain their source-specific conventions
(for example the median-region comparisons use native array indices).
No blanket coordinate or unit normalization occurs. Header key/comment/value
strings remain original text. M2 must make the relevant domain units and
conversion/source rules concrete without changing effective values; M7 later
serializes the applicable WAD records. No runtime unit objects are present now.

## Accepted implementation chain and evidence reuse

| PR | Accepted increment | Merge commit |
|---|---|---|
| #136 | C90 template, service names and qc phase | `7341c895e9e1eb7008915e1e2cf961532b7eb8a6` |
| #137 | Owned config snapshot | `1d991a22a39d6133ab19721b7bb3a6dd11394264` |
| #138 | Request/context/result/error lifecycles | `a58291a1f980fa1563ef89b49e01de4e4d47796c` |
| #140 | Actual legacy CLI capture and diagnostic bounds correction | `6a4d4d8ec078a3360a5a743845dcbe752cbc84bd` |
| #141 | Optional input BPM / required variance policy | `30ebe2a148021b2719bb8c5972b678150e86489c` |
| #142 | Resolved calibration/BPM bindings | `12f555ce4e14df0e292b629d54a3e496b94d8269` |
| #143 | Explicit file/list request adapter | `98454283341a5bbce641119bed686fa56ff9c44b` |
| #145 | First real bias service/shared kernel and paired verification | `bacfa24fce45c0e7957bbc55f9cb6abfc7027219` |

Reuse the paired receipts for [configuration](m1-config-paired-results-2026-10-29.md),
[runtime](m1-runtime-paired-results-2026-10-29.md),
[CLI](m1-cli-paired-results-2026-10-29.md),
[bindings](m1-bindings-paired-results-2026-10-29.md),
[inputs](m1-inputs-paired-results-2026-10-29.md) and
[bias](m1-bias-paired-results-2026-10-29.md). They retain exact tested revisions,
paths, assertions and limits. Earlier increments are not relabeled as tested at
the latest source. The final target run at f5858310 re-exercised the five focused
contracts together: Mac 5/5 in 13.88 s; representative Chapman4 5/5 in 11.88 s.
Agent C90/C17 and applicable ASan/UBSan evidence is separately recorded.

Per-object injection counts in individual contracts describe different objects
and paths; do not sum them into a whole-engine allocation coverage claim.
Target C17/sanitizers and LeakSanitizer are not newly claimed. No historical
matrix replay or duplicate copycat Chapman qualification is needed for closure.

## Open limits and subsequent owners

| Remaining capability/limitation | Existing owner/milestone | Effect on this disposition |
|---|---|---|
| Retained Eclipse unchecked allocation failures | Open [#144](https://github.com/fselman/wenu-imaging/issues/144), wider #75 | Remains open; blocks blanket dependency OOM/Python-host crash-safety claims. Does not block M2 settings work or erase accepted new-owner controls |
| Known --ksize handler defect; other deferred legacy defects | Existing tickets, including #133 | Not corrected or closed through this review; no implicit CLI policy change |
| Fully replacing mef_bb, general path resolution and actual grouped command dispatch | M2–M6 as specified in the plan | New boundaries coexist with the preserved compatibility engine; M1 does not activate a replacement CLI |
| General primary/single-image/MEF loading and selector consistency against files | M4, with paths in M3 | Metadata descriptors and the bounded CCD/MEF bias service are not full layout support |
| Remaining existing calibration operations and science preprocessing | M5/M6 | No further subroutine extraction is moved ahead of M2–M4 |
| New QC estimators, required variance, linearity, darks and fringes | M5a/M6a–M6d | Existing QC/explicit unavailable values preserved; no scientific audit or numerical expansion |
| Runtime WAD/ASDF schemas, project records, exact-version resolution and publication | M2 semantic contracts, M7 persistence and later clients | Crosswalk is documented; no schema runtime, project migration, graph cascade or publication capability claimed |
| mefppy, general reentrancy and parallel execution | M10 decision/binding and later parallel milestones | Internal uninstalled types are not a permanent public ABI; no deployment or thread-safety claim |

These are retained scope boundaries, not newly waived M1 requirements. Closing
this foundation milestone does not close #75/#144, supersede Stage 2/2.1
limitations, retire PAF/legacy clients or certify an ESO Phase 3 product.

## M2 handoff after owner acceptance

1. Reuse the vendored pinned tomlc17 and accepted Mac/Chapman qualification.
   Build it in the documented scoped C99 dependency lane with a strict-C90
   caller/core; do not upgrade the whole project language mode or install tools.
2. Establish the minimal versioned TOML domains/subsets and concrete typed
   configuration/unit/source mapping using the retained migration ledger.
   Preserve reduction profile, recipe and product profile as separate concepts.
3. Define containing-file path bases, composition, allowed overrides, conflicts,
   unknown keys and reproducible immutable effective settings. Subset file count
   follows actual responsibility rather than requiring one file per domain.
4. Convert OCAM/WFI examples and prove their effective stored values equal PAF,
   preserving actual legacy conversions, original strings and identical
   duplicate-key evidence. Five PAF double fields historically narrow through
   float temporaries; CLI overrides retain their actual different stored
   conversion path. Do not silently improve precision or apply PAF narrowing
   indiscriminately to overrides.
5. Test only the new TOML/configuration boundary and relevant regressions on Mac
   and representative Chapman with the [selected tools](selected-tools.md).
   No ASDF activation, notebook rewrite, new calibration math, install or
   observational reduction is part of merely entering M2.

## Owner disposition

Proposed: accept bounded M1 foundation closure with the open limits above and
continue the original roadmap at M2 after authorized integration of this review.
Until the owner accepts, record **closure recommended; owner decision pending**.
This document changes no native/Python code, tests, packages, installed selection
or scientific parameters and launches no new execution.
