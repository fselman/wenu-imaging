# First real-data linearity sampling proposal — 4 November 2026

Status: PROPOSAL ONLY; no sampling, noise model, interval or fit has been adopted.

All32 scan-corrected median-master bias SIGNAL candidates now exist. The remaining31
batch d84568b passed at Pictures/OCAM/wenu-imaging/linearity-bias-batch-05ijf_sx;
overall complete_for_owner_inspection,31completed, all8preservation checks true.
masters.json includes the originalCCD65 pilot. CCD69/74/77/84/85 accepted9/10;
others10/10. Preserve these actual memberships; do not silently force the rejected
frames into a master or give every master the same sample count in propagation.
The existing rejection rule, not a new classification, made these decisions.

## Population decision before extraction

Five512x512 ROIs on32detectors contain41,943,040 physical sites. The qualified
reference joint fitter allocates dense structures and one illumination-rate
parameter per site; it cannot be treated as an established whole-ROI solver at
that size. ROI means are not interchangeable with physical pixels in its model.

Propose a compact engineering pilot: ONE deterministic physical pixel near the
centre of each reviewed ROI, across all32detectors. These are160 physical sites,
at most3200 original-flat observations, and225 joint parameters (160 illumination
rates,64 amplifier response coefficients, ONE common shutter offset). Keep all20
original flats in acquisition order and original pair identities; do not average
the pairs or introduce per-frame illumination factors. Existing BPM/nonfinite/raw
saturation admission is retained. A missing/bad proposed site is recorded, not
replaced by an automatically selected nearby pixel or a hand-picked quiet one.

The concrete proposal is
config/characterization/omegacam-linearity-pilot-sites-proposal.json. It retains
source profile hashes, detector/output/slot identity, source ROI and both active
and raw FITS1-based pixel coordinates. For an even-width ROI, the central-pixel
tie is resolved toward the readout in each axis; upper-half reflection therefore
uses ceil rather than floor as needed. Arrays are not rotated. For example:

| Detector / ROI | Active pixel | Raw pixel |
|---|---|---|
| CCD65 near_readout |384,384|434,388|
| CCD96 near_readout |1661,3708|1711,3812|

All160 sites are unique and within their source ROIs; direct calculation checks
the CCD65/96 readout reflection for all five corresponding ROIs. Profile loader
validation and these arithmetic checks passed; no images were opened. These
checks do not establish that the proposed pixels are scientifically suitable.

At maximum admission, the3200x3200 double covariance factor alone is78.125MiB.
This is not a total-memory estimate: the covariance assembly/QR, model/profile,
raw-plane loading and sample-extraction owners need additional memory. This pilot
size is a bounded engineering starting point, not performance qualification or
representative whole-detector calibration. Convergence and spatial sampling
stability must be assessed; a single central pixel is not an accepted response
map or justification to correct every pixel without further validation.

The alternative is to develop and qualify a scalable full-population forward
model/solver before a real-data fit. That is a larger numerical development;
using ROI means in the existing direct-pixel fitter is not the alternative.

## Still separate scientific decisions

Sampling acceptance does not choose a noise distribution/pooling rule, covariance
model, Monte Carlo count/seed, fit interval, inversion bounds, optimizer budgets,
profile grid or calibration validity. Those must remain explicit and supported
before the real fit. Master variance remains unavailable. Do not use RON²/N for
the actual median master, row-profile scatter as scan-estimator uncertainty, or
unit/identity covariance to bypass missing inputs. Per-master accepted membership
and shared-error dependence are retained. All existing ordinary/MAD diagnostics
remain unchanged; no pixels/ROIs are newly rejected by making this proposal.

No new observations processed, fitter run, correction applied, plots/HTML,
installation, merge, cleanup or repeated numerical qualification. #236 remains
open. Request owner's sampling choice before implementing this as an extraction
population; positive feedback on the earlier mosaic does not choose fit pixels.
