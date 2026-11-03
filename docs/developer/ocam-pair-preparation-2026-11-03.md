# OCAM real-sequence preparation — 3 November 2026

After the Mac raw-pair qualification passed, the owner instructed proceeding and
confirmed the input directory ~/Pictures/OCAM/bpm. The returned dfits/fitsort table
confirms 30 files from 13 March 2017, all with OBS.ID 574184: ten zero-second r_SDSS
biases and twenty v_STRM FLAT,DOME,DETGAIN frames. This is owner-supplied primary
header evidence, not yet independently inspected extension layouts or pixels.

The selected flat sequence preserves acquisition order:
2,70,40,5,10,30,20,50,60,7 | 7,60,50,20,30,10,5,40,70,2 seconds.
Each pair has two explicit file identities. The 7 s pair is consecutive; the
other equal-time pairs are not. No time sorting, rounding or lamp scaling occurs.
The sequence helper records every declared filename and verifies the exact
primary exposure/type/filter/instrument/OBS.ID against the shared FITS reader.

## Saved preparation outputs

Pycavi2/tools/prepare_ocam_pair_measurements.py reuses the existing bounded
inspect_fits_headers implementation. It reads headers only, never image arrays.
The output directory must be new and outside the raw directory. It saves:

- inventory.json: selected metadata/cards/diagnostics, header-time evidence,
  configured detector claims, observed independent HDUs, exact configuration
  hashes, scan/trim declarations, unresolved measurement selections and source
  stat preservation. FITS warnings remain visible; no input repair occurs.
- sequence.tsv: original order, role/pair, declared/header time, path and metadata
  error count. Tab delimiters are emitted through the standard CSV writer.
- pairs.json: explicit zero-based sequence indices for each named flat pair.

Up to 128 other .fits files directly in the same directory are inspected as
unselected candidates. Names do not choose a calibration or assert its role.
No recursive search or calibration activation occurs. The .cfg supplies logical
detector names and Python configuration entry order; each file's HDUs are matched by
EXTNAME independently. This does not validate a native binding merely because
its ordinal matches. The Python entry index is not the native PAF slot;
configuration_detector is now null until explicitly resolved. Hardware/amp/readout/geometry evidence remains for review.
CCD_69 and CCD_77 are tagged for the already-recorded instrument-history review,
without declaring the selected frames affected by that historical event.

## Remaining measurement selections

The saved report explicitly leaves unresolved the BPM and its encoding/polarity,
per-amplifier ROI rectangles, raw saturation boundary, the raw bias pair, and
resolved amplifier/readout bindings. Existing headers and candidate products
will inform these choices. No fabricated master, all-good substitute mask,
arbitrary saturation limit or default ROI is inserted. ready_for_measurement is
false; successful preparation means prepared_for_selection_review.

This increment gathers the missing real header evidence needed to bind the
Mac-qualified numerical service. The later retained native run will use the
reviewed bindings and selections and expose raw-pair tables before gain-range
or uncertainty-model choices. No new fit, Monte Carlo, correction, product/QC
publication, installation or merge is included.

## Verification and actual Mac command

Three preparation-policy tests pass in 0.048 s on the agent: explicit filenames
and pair membership; saved records with reversed HDU order and unchanged source
hashes; exposure/type/OBS.ID/coverage conflicts, including duplicate header keys.
The tests inject header records and do not claim to test FITS parsing; the shared
reader's actual Mac qualifications remain earlier evidence.
[Preparation test output](evidence/ocam-pair-preparation-2026-11-03/agent-policy-tests.log).

Pycavi2/tests/qualify_ocam_pair_preflight_mac.py is the retained exact-source
actual Mac runner. It verifies host/Python/niceness and clean main c73d9a9e,
exports the fetched commit, runs those three small policy checks, then inspects
the actual source directory and prints detector coverage/layouts and candidate
names. It protects the checkout, installed module/configured engine and exported
Python/C/config sources. Raw protection is stat identity only; no pixel checksum
or payload validation is claimed by a header inventory. Full diagnostics remain
in the saved JSON if metadata blocks preparation. Existing native gates need no
replay for this Python header-preparation increment.


## Actual Mac receipt and label correction

Owner returned successful header preparation at a9bdb160, retained
/Users/fselman/Software/build/wenu-imaging/mac-ocam-pair-preparation-XqbLTbCy.
Thirty selected assets, ten biases, twenty flats, ten pairs and one unselected
candidate were read. All configured identities occur in all 30 files with stable
2144 x 4200 image layouts. #96 is HDU32; #65 through #95 follow the reported
independent mapping. Candidate OCAM_BPM_1x1.fits has 33 HDUs, absent primary type/
product category. Raw stat and checkout/installed/export preservation all pass.
Complete logs/JSON remain on the owner Mac; only terminal output was supplied.

Source review caught an overly strong field name in the preparation report:
configuration_detector was filled from ext_N_name order in the Python .cfg.
Native mef_bb_new sets ccd[i].extnum=i+1 and reads PAF CHIP(i+1), while scan/crop
uses bb->ccd[bb->xtnum-1]. Thus these indices must not be conflated. The helper
now records python_config_entry instead and leaves configuration_detector null.
No native pixels were processed, and binding-validation flags were always false.
The correction passes three small policy tests in 0.037 s, including an explicit
null-native-slot assertion. The prior inventory stays retained without a header
replay. Future binding must use reviewed detector-to-PAF geometry, independent
of the current file's HDU ordinal. Raw/BPM geometry and mask encoding/polarity
still need review before numerical measurement.
