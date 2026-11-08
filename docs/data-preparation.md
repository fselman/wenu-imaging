# Preparing inputs

Raw observations are immutable. Read-only preflight reports missing or conflicting
metadata; any approved repair creates separate prepared copies. Keep raw,
orchestration and product directories distinct. Preparation does not select
calibrations or establish detector/scientific suitability.

Require reviewed observation category, exposure type and observing technique before
reduction. Metadata meaning and provenance belong to the
[WAD contract](architecture/proposed/wad-processing-project.md#data-preflight-under-wad).
Check source headers and instrument/readout/binning/detector identity explicitly;
unknown values must remain unknown rather than being invented from filenames.

The [ZWO preparation helper](../Pycavi2/tools/prepare_zwo_asi.py) supports explicit
TOML settings and reviewed plan/apply operations. The
[Bath ASI1600 example](../Pycavi2/config/preparation/zwo_asi1600mm_bath.toml) is
dataset-specific; it is not a universal camera calibration. Use the helper's
`--help` for its supported interface. Check applicability before using an example.

Before applying a plan, review proposed metadata, source identities and destination.
Original headers and pixel payloads remain untouched. Copies preserve payload
bytes; stale CHECKSUM/DATASUM cards are omitted rather than asserted valid.
Only a completed prepared tree with `PREPARATION_COMPLETE` and its preparation
manifest is eligible for later admission; retain incomplete output for diagnosis.
Successful preparation does not launch a reduction or imply Phase 3 compliance.
