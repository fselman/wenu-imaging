# Approved engineering sampling and corrected-pixel extraction — 4 November 2026

Owner accepted the linked 160-site proposal with “Yes, proceed.” The proposal
file remains immutable review history; approved coordinates and its digest are in
config/characterization/omegacam-linearity-pilot-sites.json. This adopts sampling
only, not a noise model, fit interval, fitted coefficients or calibration validity.

## Implementation

`tools/prepare-linearity-sites.py` checks the approval, profile hashes, independent
detector/amplifier/native-slot identities, original ROI memberships, readout-side
midpoint tie and raw crop offsets. It writes 32 five-singleton ROI TOMLs and a
hashed manifest in a fresh empty directory. Existing processing profiles and
full ROI boxes remain unchanged. No FITS is opened during this preparation.

`mefpp_sample_extract` reuses `mef_linearity_from_files`, which binds explicit
FITS/HDU references, validates exact exposure times and nonconsecutive pairs,
loads selected planes, then calls the existing scan-correction/master-subtraction
sample service. The scientific kernels are unchanged. Only singleton regions
with distinct coordinates are accepted; no neighbouring replacement pixels,
ROI means, pair averaging, lamp factor or coefficient fitting is introduced.

The command arguments are:

```
mefpp_sample_extract NATIVE.paf SINGLETONS.toml RAW-SELECTION.tsv MASTER.fits MASTER-HDU MASTER-ASSET MAX-SITES MAX-OBSERVATIONS EMPTY-OUTPUT
```

The existing raw-pair plan is reused as a **selection transport**. Its parser and
binding helpers moved without semantic changes into the private
mef_measure_plan_internal.h shared by both commands. It still contains the two
raw-bias references and old pair-only row/MAD choices; the extraction command
neither opens those raw biases nor evaluates pair diagnostics. The active master
is a separate explicit ADU calibration reference, validated against the selected
identity/slot/readout/binning/geometry. For the approved pilot, the per-detector
limits are 5 sites and 100 observations. The loaded-pixel ceiling remains explicit
and includes flat planes plus active master and optional BPM. This is not a
whole-process memory ceiling: existing services load a detector's selected planes,
scan scratch and active site map, even though the output population is small.

The sample API requires numerical identity bounds. Extraction supplies the full
finite double transport domain [-DBL_MAX, DBL_MAX], **not** an admitted fit or
inversion interval. This is not exported as a calibration interval. Noise is
unavailable; the exported samples cannot be sent straight to the fitter. The
later recipe must supply a scientifically chosen interval and justified covariance.

Native outputs are `samples.tsv`, `population.tsv`, `configuration.json` and
`command.complete`. Each original-frame/site combination is retained in frame
order then source ROI order, with physical active/raw coordinates, original asset,
HDU/index/pair, exact seconds, admission state and full-precision corrected ADU.
Rejected/unavailable samples have an empty signal cell; never zero. Every approved
site remains represented, including entirely masked sites. `not_admitted` makes
no per-pixel cause claim: frame population counts separately retain aggregate
BPM/nonfinite/saturation exclusions under the existing exclusive precedence.
Noise stays explicitly unavailable. The kernel's strict finite-scan and
finite-master validation still fails the operation if those prerequisites fail.

The native completion marker is not source-preservation proof. A future actual
all32 extraction controller must verify the complete bias batch/pilot/catalog,
master memberships and ASDF lineage, freeze all selected source files and metadata,
verify products and sources after the serial extraction interval, and retain an
overall receipt. No actual extraction controller or real-data receipt is claimed
in this increment. TSVs are native transports, not final shared ASDF QC products;
ASDF publication follows the guarded recipe stage. Plotting/HTML remain separate.

## Verification and next handoff

Agent C17 command build and normal mefpp build pass. Initial focused integration
checks passed 2/2 in 1.03s (new sample command plus affected raw-pair command).
After adding explicit extension-master admission/wrong-HDU refusal, the changed
sample check passed in 0.63s; the unchanged raw-pair check was not replayed.
The tests reuse generated FITS fixtures, four mask encodings, known corrected
signals, nonsequential original indices/pairs/HDU order, null samples, raw
saturation equality, all-masked empty success, input/output preservation and
seven refused requests. They do not rerun the old noise/joint/optimizer matrix
or claim a dependency allocation/OOM qualification.

Metadata-only all32 preparation passed at sample-sites-0vzm7op7 in the agent
workspace. Changed pixel, slot, profile digest and unapproved status were refused.
The existing raw-pair parser body was moved verbatim. No observation was opened.

`Pycavi2/tests/qualify_sample_command_mac.py` prepares the singleton transports,
compares the unchanged extraction/layout/scan kernels with the retained passed
aa5427c composition gate, builds uninstalled C17 commands/normal mefpp in a fresh
retained directory, and runs exactly native_sample_command and
native_pair_command. Checkout/install/exported-source protection is required;
source snapshots now include JSON/TOML/PAF metadata as well as code. Actual Intel
Mac qualification is pending. No installation, real extraction, fit, correction,
merge or cleanup is authorized by the synthetic qualification block. Existing
approval remains sufficient for subsequent preparation/extraction after this
actual-target result is inspected. #236 and draft PR227 remain open.
