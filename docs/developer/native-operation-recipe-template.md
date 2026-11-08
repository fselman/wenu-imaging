# Template for the next native operation recipes

## Current structural amendment — 8 November 2026

The owner conditionally approved the [coordinator design](design/common-recipe-coordinator-v1.md).
Bias now implements the common outer structure in a 60-line command. Final owner
source acceptance and selected-Mac qualification remain pending. The existing
`mef_operation_run` remains the inner validate/load/calculate/optional-publish/
cleanup lifecycle; its callbacks and scientific behavior are unchanged.

Every outer coordinator follows this visible order:

1. Initialize safely destructible owners and sample the start time once.
2. Prepare configuration and admit every explicit input/detector binding.
3. Open run resources after admission.
4. Execute the declared scientific processing, preserving collective steps.
5. Verify stored results and QC; publish through existing product services.
6. Complete reporting or retain failed work, then release owners once.

`mef_recipe_run.h/.c` supplies common paths, exclusive logging, private workspace,
completion and failure reporting. Its small state borrows operation/progress/
workspace names and source revision; it contains no detector state or scientific
policy. Its functions return true on success. `mef_bias_recipe.h` contains the
separate bias owners and typed phase functions. The command explicitly orders
them; there is no new callback dispatcher. Existing product path resolution and
inner operation services remain in use.

High-level files should normally fit two readable pages, at most three. Put blank
lines before and after standalone explanatory comments. Do not pack statements or
hide the whole recipe behind one opaque call. Future recipes reuse this structure
while retaining their own typed scientific services, collective calculations and
publication contracts. Implementing those recipes is outside the present scope.

The older dated notes below are historical. Consolidating them and other
superseded documentation is queued after the bias readability refactor.


Current bias completion path: [bias-recipe-completion-2026-11-02.md](bias-recipe-completion-2026-11-02.md).
Bias is the only new recipe implemented; BPM is the next recipe to create, not
an existing caller. Numerical/QC definitions and the native-ASDF handoff below
are now implemented and target-qualified at eeacca3; earlier definition-pending
statements are historical. The final one-command completion entry is prepared
for its targeted Mac gate. No new BPM or other recipe is implemented here.


2 November QC decision: ASDF is adopted for the common saved QC records. The
[shared QC schema and creation path](shared-qc-asdf-2026-11-02.md) now supplies
`QcRecipe`/`BiasQcRecipe`, one validator/ASDF writer and local reference traversal.
Use that shared assembly path at the project integration boundary; do not add
recipe-specific serializers. Bias quantities stay ADU/counts. Estimator/region,
hot-pixel and frame-pair definitions, numerical extraction and standalone CLI
handoff remain open. Earlier persistence-pending language below records the
pre-decision scope; it does not undo this now-adopted representation.

This is the companion to `mef_operation_run` in
`mefpp2/ins/mef/common/mef_operation_template.h/.c`. It incorporates the first
bias recipe's actual Mac C17 lessons, including #210, #211 and unresolved #212.
Apply it to subsequent BPM, flat and science adapters. It does not authorize
their numerical implementation, new QC estimators or persistence choices.

The execution sequence is unchanged: validate, load, calculate, optionally
publish, then always clean temporary owners. Bias proved that this lifecycle
alone does not establish correct metadata, a valid header or a valid comparison.
Those contracts must be explicit in each concrete recipe.

## Fill in the recipe contract before implementation

| Contract field | Required decision or evidence |
|---|---|
| Operation identity | Operation name/version and native producer/version/source identity; no success inferred from a filename |
| Scientific boundary | Existing kernel and exact units/precision/order/rejection to preserve; separately identify any proposed numerical change |
| Inputs | Explicit ordered raw lists and selected calibrations, optional-input choices, applicability and immutable-file policy |
| Detector mapping | Logical ID, original HDU, configuration index and output ordinal as separate concepts; bind each file independently |
| Output coverage | Selected detector set, layout, required reference detector/statistics, and the meaning of any mosaic-level metadata |
| Result ownership | Borrowed inputs, private working arrays, pending owned result, failure cleanup and successful transfer |
| Processing diagnostics | Existing quantities actually available from the kernel, their definitions, units, regions, correction stage and original frame indices |
| Scientific QC | Questions to answer and owner-reviewed estimators/interpretation; pending decisions must remain visibly pending |
| Decisions | Algorithm rejection, detector health, eligibility and human/policy exclusion kept separate, with reasons and traceability |
| Headers/provenance | Keyword authority, configured versus measured values, input identities, actual correction state, completeness and unknowns |
| Saved representation | Explicitly reviewed contract/schema and responsible layer; do not choose JSON/ASDF from coding convenience |
| Resources | Peak loaded/working/result/header/queue memory, execution host and selected tools; no claim based on one-plane memory alone |
| Acceptance | Exact comparable references, independent known answers, expected identity/layout differences, failure controls and retained evidence |

For bias, these rows now use the reviewed numerical definitions and common
ASDF creation path. The versioned native JSON is internal transport, not saved
QC. A future BPM recipe must fill its own scientific quantities/definitions and
reuse the common ASDF builder/writer rather than copying transport as QC.

## Concrete adapter scaffold

Use an operation-specific typed state and result. The code below is a layout
guide, not another dispatcher or a compilable implementation with fake success.
Each callback must do its real work or return an explicit error/unsupported
status. Existing native routines remain the calculation authority.

```c
/* Typed state: borrowed config/request/maps; temporary inputs/workspace;
 * pending owned result; reviewed output/publication policy. */

recipe_state state;
mef_operation_steps steps;
mef_status status;

/* Initialize all owners before anything can fail. Reject occupied out/error. */

recipe_state_initialize(&state, config, request, maps, output_policy);
steps.validate = recipe_validate;
steps.load = recipe_load;
steps.calculate = recipe_calculate;
steps.publish = publish_requested ? recipe_publish : NULL;
steps.cleanup = recipe_cleanup_temporaries;

status = mef_operation_run(&steps, &state, error);
if (status == MEF_OK) {
    *out = state.pending;
    state.pending = NULL; /* Transfer exactly once, after required completion. */
} else {
    recipe_result_destroy(state.pending);
}
return status;
```

`recipe_validate` checks metadata/applicability before loading arrays. Loading
uses existing qfits/Eclipse services through explicit mappings; it must not
introduce another FITS parser. Calculation does not publish files. Publication
prepares headers from the typed result and reviewed coverage before writing,
and reports completion only after its declared commit boundary succeeds.
Cleanup releases only temporary owners, including partially loaded arrays.
Results that outlive the call must own their required metadata and arrays.
Keep independent-command and full-recipe callers on this same operation path.

## Lessons that must carry forward

### Compare the same detector coverage (#210)

The first bias test compared detector-B output with a two-detector mosaic's
primary RDNOISE. The mosaic primary described detector A: 4.1; detector B was
configured as 4.0. Exact selected pixels and extension headers already matched.
Changing the adapter to emit 4.1 would have made its metadata wrong.

Define what the reference primary describes before comparing it. For the
current bias test, project only the configured RON/gain cards from the independent
legacy selected-detector extension and independently check their values against
native configuration bits. All other primary cards remain exact, apart from
separately generated ORIGFILE. Record that projection in evidence. It is not a
generic ignore list, nor a rule for choosing mosaic-wide RON/gain in future.
Each new recipe needs its own explicit header/coverage correspondence.

Use nonidentical detector parameters and nonconstant detector pixels in fixtures;
identical values can conceal a wrong mapping. Keep source HDU, configuration
detector and output position independent even when a fixture happens to align
them. Test reordered per-file detector maps when that adapter supports them.

### Reuse safe header construction (#211/#212)

The new primary-image publisher deleted structural cards, then merged a header
using indexed traversal. Bundled `qfits_header_del` did not decrement `hdr->n`;
the merge traversed beyond the surviving cards and crashed. A passing MEF case
had not exercised this primary-image conversion.

Do not index or merge a header as an update after deletions using this qfits
API. `qfits_header_copy` traverses forward links and reconstructs its count by
append; use a fresh copy before indexed enumeration. Build a changed structural
prefix with append and copy only the allowed nonstructural metadata. Do not
delete required cards and assume the remaining object's counters are sound.

The qualified bias example is `primary_image_header` in `mef_bias_files.c`.
Reuse the existing qualified publication path where applicable. When another
recipe needs the same conversion, extract that helper into a shared header
module with its existing controls rather than duplicating it. This is an explicit
reuse point, not permission to write a second serializer or broadly fix qfits.
Issue #212 remains open; the caller mitigation is not general qfits safety or
complete allocation-failure qualification. Long-string limitations remain #125.

Validate FITS structural cards, order, scaling and metadata with an independent
reader. Processed physical pixels must not inherit the raw unsigned-integer
storage offset. Cover both primary-image and extension input; float and scaled
unsigned-16 cases must reach the actual publisher, not only the numerical service.

### Preserve measurements without inventing QC policy

Keep configured gain/RON separate from any measured estimator. Keep scan
statistics and algorithm acceptance flags in original input order, including
rejected frames. A stacking rejection flag does not itself define scientific
QC exclusion. Separate detector health, output selection, eligibility and
processing outcome. Preserve unavailable/unknown states explicitly.

Carry existing diagnostics through extraction without silently redefining them.
Agree any new estimator, region, units, correction stage, interpretation and
decision rule with Fernando before implementation. Preserve the raw observations
and decision history. A small debugging record is not a final QC schema and its
extension is not sufficient producer provenance. Do not copy the bias command's
provisional JSON choice into the next recipe as a default.

### Keep publication and validation bounded

Inputs stay read-only; never use the input directory as an implicit catalogue.
Temporary product assembly is an output, not a staged copy of an input. Existing
destinations must not be overwritten. Define whether the FITS and a result record
commit independently: a complete FITS may remain after a later record-write
failure, but the command must report that failure truthfully and not rerun itself.

For every adapter, exercise partial failure/cleanup, missing selected dependencies,
and an existing output, alongside exact successful products. Log actual producer,
operation/configuration/input identity and effective processing state according
to the reviewed provenance contract; never advertise completion merely because a
pending descriptor or filename exists.

## Start the next recipe's acceptance plan from this matrix

| Dimension | Minimum applicable case |
|---|---|
| Numerical reference | Independent known answer plus exact legacy/component comparison at the changed boundary |
| Configuration route | Equivalent PAF/TOML settings through the same service where both routes are supported; compare stored bits |
| Mapping | Different detector parameters, independent source/config/output indices and supported shuffled maps |
| Input layout/storage | Primary, one-extension and selected mosaic input as supported; float and unsigned-16 scaling through publication |
| Metadata | Raw-card comparison under explicit matching coverage, generated-identity treatment and recorded projections only |
| Original membership | At least one rejected middle frame where rejection applies; retain its index and diagnostics |
| Publication/failure | Controlled missing/incompatible input and protected existing output; no false completion or input mutation |
| Ownership/resources | Partial cleanup and immutable inputs/results; estimate all coexisting arrays before full-size execution |

Select controls relevant to the actual change; do not blindly rerun this entire
matrix or the bias campaign for every edit. Current execution is C17 on the Mac;
consider Chapman only for individual tests exceeding Mac memory. Preserve
C90-compatible core source, selected absolute tools, low batch priority and
bounded CPU/thread use. Explain each test before execution. Keep failed evidence,
diagnose the actual mismatch/stack, and rerun only affected controls. Software
verification, scientific QC acceptance, installation and merge remain distinct.


## Finish the whole command, not only the native calculation

Bias completion uses the same native operation template, then the common ASDF
writer and frozen-reference verification. Native FITS success alone is not full
recipe success. The completion entry records preflight/native/qc/verify stages
and returns success only after all required outputs validate. Keep its native
producer separate from the outer completion-module identity.

For the next BPM recipe, retain this boundary: one callable C calculation path,
one shared QC creation path, and truthful overall completion. Preserve existing
files and completed earlier products on later failure; do not auto-retry or
pretend there is a multi-file transaction. Explicitly test failure before native
execution, native rejection, later QC conflict, and protected previous receipts,
including exact inputs/no false success. Reuse qualified native binaries and
source evidence when an increment changes only outer orchestration. Do not
create or modify a new recipe merely because reusable library helpers exist.

## Use the qfits keyword spelling, not a stripped Astropy key

Use full `HIERARCH ESO ...` names when passing hierarchical keywords to qfits.
Astropy may expose `ESO ...` names, but those do not acquire HIERARCH automatically
in this library and can be truncated silently on output. Correct dotted shortFITS
omits ESO; prefix searches require the full name. Verify disk round-trip, not
only a lookup in the object just populated. See the
[HIERARCH review](hierarch-keyword-review-2026-11-02.md) and #223. This does not
repair or relax the separate long-value/CONTINUE restrictions in #125.
