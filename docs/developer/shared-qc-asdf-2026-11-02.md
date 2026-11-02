# Shared QC records and recipe creation path — 2 November 2026

Status: Mac shared QC metadata contracts passed 10/10 in 1.607 s at 0840f031.
Native libasdf provisioning/interchange and Chapman remain pending. #213/#214/#215.
The native bias calculation/publication qualified at 2803786 is unchanged.
No new numerical estimator, normal activation, native bias test replay, merge
or cleanup accompanies this candidate. The owner-authorized private libasdf
trial is separate from production installation; see the qualification note.

## Owner decisions

QC structure and the recipe creation path are shared as far as possible across
bias, BPM, flats and science. ASDF is the common saved representation, with
one record per input and a separate product record referencing the inputs.
The characterized file identity/full filename and characterization lead the
logical record. `.fits` becomes `.asdf`; do not append `.fits.asdf`. Compression
naming/identity is future work; reject unsupported suffixes and name conflicts.
Store records in explicit QC destinations, not by modifying raw directories.

Keep file/assessment identities and measurement origin independent of physical
location. Raw records contain their measurements; participation/rejection is
specific to the parent recipe/product, not a mutation of the raw record. A
project monitor can display a tree while sharing the same leaf records among
several products. Its index is derived, not a competing measurement authority.

Bias QC is in ADU (counts for pixels), with no gain conversion or downstream
detector characterization. Requested quantities are overscan level/RMS, bias
level/RMS, hot-pixel count, RON from a pair difference, and detector ensemble
mean/median. Also retain row/column profiles, the per-frame values in acquisition
order for stability inspection, invalid/clipped counts, sample/region context,
input membership and exclusions. No automatic scientific cuts are adopted.

## Common implementation

`Pycavi2/pycavi/pycavi/pycavi_qc.py` contains the shared creation path:

1. `QcRecipe` creates the same versioned record for an input or product from
   explicit metadata. It does not discover files, infer IDs/HDU mappings or
   read image pixels. It owns copies of supplied metadata.
2. `add_measurement` uses one descriptor for scalars, profiles and explicit
   unavailable/invalid values. `add_input` adds ordered frozen QC references and
   parent-specific participation. Duplicate input occurrences retain indices.
3. `summarize_detectors` produces only the requested scalar mean and median,
   retaining contributor and unavailable-detector IDs. Units and stage/method
   must agree. Profiles have no implicit cross-detector average.
4. `seal` transfers an immutable record; callers receive copies for inspection.
5. One `write_record` validates and writes ASDF for every recipe, exclusively
   publishes a new sidecar and never opens/copies/modifies the image asset.
   Linked input records must already exist and match identity/content/selectors.
6. One `read_record` and `traverse_records` support offline monitor traversal,
   verifying the referenced assessment/content, shared leaves, local root bounds
   and record-count limits. Missing/changed references fail explicitly.

`BiasQcRecipe` is the first recipe-specific adapter. It supplies the agreed
quantity catalogue and ADU/count restrictions, and requires two distinct file
origins for measured pair-difference RON. Other recipes use the same parent
builder/schema/writer; they add their own numerical quantities and definitions.
The second-recipe contract fixture demonstrates that reuse without implementing
a new flat calculation.

The shared schema is `Pycavi2/pycavi/config/qc-schema-1.0.0.json`, a local custom
schema used with Python ASDF 6.0.0 and target ASDF standard 1.6.0. The retained
`asdf-standard` package 1.5.0 supplies the 1.6.0 core schemas; package and file
versions are different. Mac standard 1.6.0 shared QC target checks passed. Common
descriptors use primitive values/lists and explicit units, without new ASDF
extensions, asdf-astropy or another JSON Schema dependency. The optional `qc`
dependency group and schema package resources are declared; no package is
installed or upgraded in production. Installed wheel/resource qualification remains later.

## Shared logical structure

```yaml
qc:
  file:
    id: stable asset identity
    filename: complete original filename.fits
    location: explicitly supplied location
    kind: raw or product
    sha256: supplied verified digest, or null
    observed_at: observation time, or null
    selectors: explicit detector/HDU/configuration selectors
    context: supplied instrument/readout/binning context
  characterization:
    detectors: per-detector common measurement descriptors
    summaries: scalar detector mean/median and contributor identities
  record:
    schema_version: 1.0.0
    assessment_id: identity of this particular assessment
    created_at: timezone-qualified assessment time
  provenance:
    producer: software name, version and source revision
    operation: explicit operation
    configuration_id: explicit effective-configuration identity
  inputs: ordered frozen QC references and participation
  extensions: reviewed recipe-specific additions
```

This shows the logical layout, not a hand-written substitute for the ASDF
serializer. Both raw and product records use these common fields. ASDF's own
library metadata remains separate from the native measurement producer.

A measurement records name, value or numeric profile, unit, availability,
reason, method, processing stage, region, sample count and origin list. Each
origin identifies file, logical detector and HDU. Own-file HDUs are checked
against its selectors; input-derived/pair measurements are checked against
the referenced input records. A trimmed master does not acquire a fictitious
overscan: any input-derived measurement must identify the actual raw sources
and stage. Pair-difference RON describes those input measurements; it is not
silently converted to electrons or scaled into a master-noise estimate.

A frozen input reference includes a relative QC path, file identity, assessment
identity and semantic content digest. Participation keeps original membership
index, used/rejected/not-used/pending state and reason. Raw QC does not inherit
these product-specific decisions. Rejection remains recipe membership evidence,
not an automatic scientific QC exclusion policy.

References are explicit application descriptors stored in ASDF, rather than
automatic `$ref` dereferencing. This lets the common resolver check identity,
content, selectors and project-root limits before following links, without
network access or FITS array loading. A shared leaf is visited once; ordered
membership remains in each parent. This is a monitor foundation, not a monitor UI
or a general project/WAD processing engine.

Image-file digests are supplied from existing identity evidence, not recomputed
by each recipe/writer. QC content digests freeze the much smaller assessment
records. Moving the complete QC tree preserves relative links. Renaming image
files requires updating location/catalogue knowledge, not inventing a new asset
identity. Reassessment does not overwrite a previous sidecar: choose an explicit
new assessment destination and retain the old frozen parent links. The library
does not create a directory/versioning policy automatically.

## Creation template (library API)

```python
builder = BiasQcRecipe(
    file=explicit_file_descriptor,
    assessment_id=explicit_assessment_id,
    created_at=explicit_timezone_timestamp,
    producer=explicit_native_producer,
    operation="cal.bias",
    configuration_id=effective_configuration_id,
)
builder.add_measurement(
    detector_id,
    name="bias.level", value=native_value, unit="ADU",
    definition=reviewed_method_stage_region_and_sample_count,
    sources=explicit_file_detector_hdu_origins,
)
# For product records, first seal/publish the individual input QC records.
builder.add_input(input_record, qc_path="input001.asdf", participation="used")
builder.summarize_detectors("bias.level")
record = builder.seal()
path = write_record(record, explicit_qc_directory)
```

For an input record, omit the `add_input` step. All recipes follow this same
assembly/seal/validate/write path; do not create another recipe-specific ASDF
serializer. Use `add_unavailable` with a truthful stage/reason when an agreed
quantity cannot yet be supplied. Unavailable is not zero. A computed value must
have its real region/method/count and origins; the writer supplies no estimator.

## Explicit remaining boundaries

The agreed quantity names/ADU policy do not yet specify mean versus median
for level, the precise RMS estimator, regions and correction stage, hot-pixel
threshold/persistence, or how to select the RON pair. Those definitions remain
for owner discussion. This candidate implements the common creation/persistence
path, not those unreviewed calculations. Test values are explicitly supplied
metadata fixtures, not new scientific estimators or measurements of real frames.

The existing native CLI JSON remains a provisional debugging artifact until
the standalone/native-to-project handoff is reviewed and wired. It is not the
canonical saved QC and is not relabelled as ASDF. The new common writer creates
genuine ASDF records from the shared typed record contract. No automatic ingest
or processing activation, native Python binding, pipeline association or full
end-to-end numerical QC coverage is claimed by this first library increment.

## Planned verification

Run only `test_shared_qc.py` through `qualify_shared_qc_mac.py`, in the retained
qualified private ASDF environment under the actual Intel Mac. Ten focused
metadata-only controls cover naming/conflicts, immutable records, separate raw
and product membership, ASDF round-trip and schema rejection, unavailable values,
ADU/pair origins, summaries/profiles, shared inputs/relocation, broken references,
source-HDU/root checks and reuse by another recipe fixture. Network attempts
are denied and recorded. Image identity fixtures are tiny artificial byte files;
no FITS processing or numerical correctness is being tested. Source checkout,
installed engine/Pycavi/config and exported source are protected and evidence
retained. No native bias C17/C90 tests or completed dependency trials are repeated.
The owner subsequently authorized `--with-libasdf` for one additional isolated
libasdf 0.3.0 C17/Python interchange gate at file standard 1.6.0:
`docs/developer/libasdf16-private-qualification-2026-11-02.md`.
