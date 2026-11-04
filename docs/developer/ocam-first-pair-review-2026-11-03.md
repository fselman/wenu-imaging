# First real OCAM selection proposal

The one-detector command/runner passed its actual Mac C17 gate at 6e75a7b:
2/2 in 3.04 s, run mac-pair-command-mv3iAx5L, with checkout/install/export preserved.
The next action reviews existing header evidence and prepares a concrete selection
proposal, without running the measurement command or rereading image arrays.

`tools/prepare-ocam-pair-review.py` consumes the original saved inventory and prior
selection-review JSON under mac-ocam-pair-preparation-XqbLTbCy/inventory. The latter
is preserved as previously obtained pixel-review evidence, not reinterpreted as a
polarity certificate. No unchanged 31-file header scan or BPM pixel scan is repeated.

It checks the exact 30-file sequence and acquisition order, OBS.ID 574184, declared
roles/filters/exact exposures, one template per role, primary normal read mode/speed,
ordered clock, 1x1 binning and 32 outputs. Each of all 32 outputs in every selected
file must have one exact EXTNAME/physical-chip ID, manufacturer output L, expected
raw dimensions, valid 2048x4100 window and 48-column prescan/overscan declarations.
HDU association is resolved independently per file; Python .cfg order is ignored.
The candidate BPM requires all 32 exact identities, 2044x4091 footprints and BITPIX8.
Raw BITPIX/BSCALE/BZERO/BUNIT evidence is retained for review, not assumed from RON
cards or nominal gain values. Missing/duplicate/conflicting required cards fail.

Every selected source and BPM must retain the inventory's original stat identity,
checked again after review. Metadata/configuration SHA256 is checked before/after.
This is saved-header plus stat admission, not a fresh cryptographic verification
of the observation payload or a native FITS/BPM compatibility test. The qualified
runner later fingerprints payloads and the native command reads current headers.
No full-well/nonlinearity conclusion or native measurement is claimed here.

## Proposed choices for owner review

| Item | Proposal | Basis and limit |
|---|---|---|
| First detector | ESO_CCD_#65 / output L | Native CHIP1, independently associated HDU per file |
| Regions | Five existing 512x512 ROIs | Reviewed layout; active bounds remain unchanged |
| Bias pair | 09:50:05.624 and 09:50:48.373 | First two chronological biases in the admitted sequence; suitability still unmeasured |
| Raw saturation exclusion | At or above 65534 ADU | Existing PAF MEF.SATLEVEL; a digital exclusion boundary, not the nonlinearity onset or analog full well |
| Legacy BPM | Explicit binary, 1=good | Existing Eclipse convention; dense ones/binary counts alone do not prove polarity |
| Flat pairs | All ten original nonconsecutive pairs | Preserve 20-file acquisition order and original indices |
| Time tolerance | Exactly zero | This OCAM sequence declares exactly equal pair EXPTIME values |
| MAD diagnostic | Enabled | Alongside ordinary variance; no new clipping or lamp normalization |
| Resource ceilings | 206467604 loaded pixels, 50 rows | Exactly 22 raw planes plus one active BPM, five ROIs × ten pairs; not a total-process byte guarantee |

These are proposals, not implicitly adopted scientific settings. The output is
selection-proposed.toml plus review.json, saved header evidence copies and README.
The tool has no execution mode and does not invoke the qualified runner. The
header review should be returned and the three bias/saturation/BPM choices agreed
before creating/executing the first-detector numerical run. CCD69/77 history notes
are retained; no affected-detector exclusion is inferred from those events.

Create a fresh review directory under ~/Pictures/OCAM/wenu-imaging, not build.
Its README explains purpose and deletion conditions. Original metadata and raw
files remain unchanged; needed evidence is copied into the instrument directory.
Compilation/export directories are reviewed for disposition with the owner at
branch merge/cleanup, according to the existing retention instructions.

Three stdlib policy checks pass with injected saved-header records. They cover
complete/reordered 32-detector admission, exact proposal/table counts, and refusal
of amplifier/clock/duplicate-card/coverage, sequence/time and BPM-shape conflicts.
No synthetic FITS parser substitute or numerical estimator is introduced. Actual
Mac review against the retained real inventory is pending; no native rebuild or
replay of already passed command/numerical tests is needed for this helper.
