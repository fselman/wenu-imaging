# Template for the next native operation recipes

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

The QC and representation rows are deliberately unresolved for final bias design.
The present bias JSON is a provisional debugging record. Software qualification
does not adopt it for subsequent recipes. A native engine independent of ASDF
does not decide which representation a project layer will save.

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
