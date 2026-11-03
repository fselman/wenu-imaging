# Raw-only file admission for pair measurements

The real OCAM runner must not require a master bias merely to measure raw
bias-pair RON and flat-pair variance versus signal. The existing general linearity
file adapter also constructs corrected per-pixel observations for the later fit;
that is unnecessary for this first diagnostic pass and would consume much more
memory. A new explicit raw-only boundary addresses that gap before the command
runner and real observations are launched.

`mef_linearity_raw_from_files` takes a typed `mef_linearity_raw_files_input`:
configuration slot and detector/amplifier identity, ordered explicit flat
path/HDU/asset/index/pair references, two selected raw bias references, optional
BPM encoding/registry or declared binary polarity, active ROIs, raw saturation,
exact pair-time tolerance, exposure keyword/HDU, row ceiling and loaded-pixel
budget. There are no automatic scientific selections.

It validates each file's existing M4 map independently against the configuration,
active origin/dimensions, raw dimensions, identity, unit, amplifier evidence and
explicit readout/binning context. It refuses duplicate/aliased references or input
indices, out-of-range ROIs, over-budget input sets, ambiguous exposure cards,
incorrect pair multiplicity or incompatible exact pair times before loading pixels.
The caller still freezes paths, verifies the primary readout/clock/classification
cards and chooses the two raw biases. The supplied readout ID is a caller claim,
not an independent hardware-mode verification by this service.

After admission it reuses the existing M4 plane and mask loaders and the qualified
`mef_linearity_measure_pairs` service. No overscan correction, trimming of arrays,
master subtraction, dense fit-observation construction, lamp scaling or zeroing
of the flat difference is performed. ROI bounds are translated to raw coordinates
by the existing pair service. Both explicit binary polarities and REASON8 retain
their existing meanings; omitted BPM is recorded as omitted.

The returned existing `mef_linearity_files_result` contains pairs, resolved flat/
raw-bias/BPM paths and detached binding snapshots; samples and master-bias path
are NULL. The existing destructor handles partial failure and completed ownership.
The ordinary pair and bias TSV writers consume its pair result directly. Inputs
remain immutable and the result outlives source maps, configuration and caller
metadata. One detector is admitted per call. The explicit pixel budget counts
all selected flat/bias/BPM planes, including scans; it is not a byte limit for
all numerical scratch or total process memory. The surrounding runner must call
serially and release each detector result before loading the next detector.

## Validation and target-host gate

Agent C17 preparation passed native_linearity_raw_files 1/1 in 4.76 s. Twenty tiny
FITS cases cover omitted/reason8/both binary encodings, independently reordered
HDUs, nonconsecutive pair order and exact retained times, missing/duplicate exposure,
amplifier/readout mismatch, pair mismatch, bad registry/encoding, pixel/row limits,
aliases, invalid ROI and forbidden preloaded pointers. The generated master-bias
file is deleted before every call: success demonstrates no master dependency.
Known raw-pair RON, pixel counts and exported raw signal establish the intended
path. Every input FITS file is hashed before/after. One successful reason8 case
also exercises all 130 persistent custom file/service owner allocation failures;
results detach from destroyed input owners before table export. No new dependency
OOM or reentrancy guarantee is claimed.

`Pycavi2/tests/qualify_linearity_raw_files_mac.py` builds only raw-file and table
export probes, inventories exactly native_linearity_raw_files and
native_linearity_pairs_export, and preserves clean accepted main, installed files
and exported source. Actual Mac qualification is pending. Existing general
linearity-file and BPM numerical code are unchanged; no full historical test
matrix, installation or real dataset execution is requested.

After that gate, add the command/plan orchestration and exact source/provenance
receipts around this raw-only boundary. Bind the reviewed detector/processing
TOMLs to the current native configuration/ROIs and complete the remaining full
output/header checks. Explicit raw saturation, binary BPM polarity and distinct
raw-bias pair precede actual measurements. Future observational products go to a
purpose-named ~/Pictures/OCAM/wenu-imaging directory with a README stating why
needed and when erasable. Build directories remain temporary compilation/test
locations and need an owner disposition review at branch merge/cleanup.
