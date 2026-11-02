# BPM FITS and common ASDF publication

The bound-file increment at 328c50ef518c76a66791f0a398321848b84413aa passed
actual Mac C17 service/file contracts in 8.07 s. Evidence remains at
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-files-sEzWKwiU`, with installed
files, checkout and exported source preserved. This next increment adds product
publication; its actual Mac gate is pending.

## Native product and reusable Eclipse support

The existing Eclipse `intimage_save` has a void return and uses a floating-point
image path. The announced `intimage_write_hdu_checked` extension instead reuses
qfits integer conversion, validates header geometry/scaling and integer ranges,
and checks header, data, padding and flush errors. It supports unsigned 8-bit and
signed 16-bit planes without floating-point conversion. Existing save behavior
and numerical fitters are unchanged.

`mef_bpm_publish` creates a fresh temporary file in the destination directory,
writes and checks all HDUs, flushes/fsyncs/closes it, then publishes by an exclusive
hard link. Existing files, directories and symlinks are never overwritten. Failed
writes do not expose a partial final product. Headers are constructed fresh with
full `HIERARCH ESO ...` spellings; this is not an ESO Phase 3 compliance claim.
The caller supplies an exact revision and a validated canonical UTC timestamp.

| Plane | Storage | Meaning |
| --- | --- | --- |
| Primary | unsigned 8-bit | New or explicitly combined WENU_BPM_V1 reasons; zero means no detected reason |
| COVERAGE | unsigned 8-bit | 0 unmeasured, 1 fitted, 2 legacy least-squares fallback |
| NSAMPLE | signed 16-bit | Accepted sample count |
| NEWFLAGS | unsigned 8-bit | Reasons detected by this operation |
| SELECTION | unsigned 8-bit | 1 usable according to prior, new reasons and coverage; 0 excluded |
| PRIORFLAGS / PRIORSEL, when supplied | unsigned 8-bit | Original reason bytes or normalized binary selection |

NEW and COMBINED output modes are explicit. Combining a binary prior fails
because its reasons are unknown; NEW mode retains that prior in PRIORSEL and
uses it in SELECTION. Combining reason masks requires WENU_BPM_V1. Separate
coverage prevents an unmeasured zero-valued pixel from appearing certified good.
Primary legacy binary polarity output is not part of this increment.

The result owns a clone of the exact configuration, allowing publication after
its context and bound maps have been destroyed. Readout, binning, detector,
original input membership, selected calibration roles, thresholds, saturation
cuts, ROIs, fit states and prior encoding remain explicit provenance.

## ASDF through the existing QC boundary

Native code emits a versioned internal JSON handoff containing its results and
configuration snapshot. JSON is transport, not a second saved QC format.
`pycavi_bpm_qc` validates that handoff, hashes physical inputs and the product,
and uses the unchanged common QcRecipe, schema and ASDF writer. It performs no
FITS pixel processing or new numerical fitting.

Raw-flat assessments record admission and measurements from C, including excluded
frames. Selected bias/prior assessments describe their binding, not a claim to
have regenerated or scientifically reassessed them. The parent records reason
and coverage counts, parameters and frozen references; traversal is consumed to
verify those links. Configuration and file digests are checked for mutation.
Existing destinations are rejected. Leaf records precede the parent; an I/O
failure may retain completed diagnostic artifacts, but does not imply whole-recipe
success. Whole-command completion and its CLI remain the next increment.

## Verification and target gate

Agent preparation passed three focused C17 contracts in 7.13 s:
`native_bpm_service`, `native_bpm_files`, `native_bpm_publication`.
The publication contract covers five synthetic FITS/ASDF scenarios, both fit
modes, binary/reason/no priors, missing coverage, excluded frames, exact integer
serialization, complete HIERARCH names, independent Astropy readback, configuration
ownership and allocation cleanup, exclusive publication and input preservation.
ASDF checks use the existing schema/core 1.6 writer, frozen-link mutation rejection,
malformed-handoff/configuration rejection, no overwrite and blocked networking.
This is agent preparation, not Mac or observational acceptance.

The Mac `--bpm-publish` gate builds and runs only these three affected contracts,
using the retained qualified ASDF interpreter. It checks that interpreter's
controls before and after the run and preserves checkout, installed files and
exported source. The unchanged shared QC and earlier bias contracts are retained,
not replayed. No installation, checkout switch or merge is performed.

After actual Mac success, continue the recipe command and whole-operation
completion. Gain, RON, full linearity and the shared signed shutter model remain
pending; the formula design PDF/LaTeX is unchanged. Validate changed code on
Chapman before full actual WFI/OmegaCAM tests there.
