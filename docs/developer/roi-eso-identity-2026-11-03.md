# Exact ESO identities in named ROI configuration — 3 November 2026

Resuming the real OCAM preparation exposed #230: mef_roi_config's ID validator
rejected the # character in the actual ESO_CCD_#65 ... ESO_CCD_#96 identities.
The native raw/layout and pair services retain these strings, so this was a
configuration admission gap. The new quoted PAF/TOML regression fails before the
correction; no real observation or numerical measurement was launched.

The correction adds # to the bounded 1..63-character identifier grammar, preserving
strings exactly in the existing reader/binder. Values remain quoted in PAF/TOML;
a hash inside the string is not normalized away. Whitespace/path separators,
empty/long IDs, duplicate/unknown keys, schema errors and bad bounds remain refused.
No fitter, statistics, scan geometry, mask semantics or scientific threshold changes.

Agent GCC C17 native_roi_config passes 1/1 in 0.08 s. The test covers both formats,
exact ESO_CCD_#65 and ESO_CCD_#96 values, explicit L/R amplifier identity, reordered
bindings and the existing strict/atomic/ownership controls. The fixture uses small
synthetic dimensions; it is an identity contract, not real-detector geometry proof.
[Before failure](evidence/roi-eso-identity-2026-11-03/agent-before-tests.log),
[corrected build](evidence/roi-eso-identity-2026-11-03/agent-after-build.log),
[corrected checks](evidence/roi-eso-identity-2026-11-03/agent-after-tests.log).

Actual Intel Mac gate passed at f02eb695aa91c34a30dc1651fa8bc78b5ca597c4:
native_roi_config 1/1 in 1.26 s, 1.27 s total; retained
/Users/fselman/Software/build/wenu-imaging/mac-roi-identity-8xg2xMCO.
Checkout, installed_files and exported_source preservation all passed; main remains
clean. This is the owner's returned terminal receipt; full logs remain on the Mac. Pycavi2/tests/qualify_roi_identity_mac.py exports
the exact commit, builds roi_config_probe and runs only native_roi_config after
checking its inventory. It protects the clean main checkout, installed files and
exported source. No unrelated numerical matrix replay, actual pixels or install.
Issue #230 is closed after this scoped actual Mac acceptance. PR #227 remains draft;
no merge, install or actual-data numerical acceptance is implied.

## Current real OCAM preparation evidence

Owner-returned selection-review.json output confirms raw normal read mode/speed,
mosaic read (ordered), 1x1 binning, 32 outputs, and for the first two detectors
manufacturer output ID L with OUT1 NX=2048, NY=4100 and 48 prescan/overscan columns.
These manufacturer labels are recorded evidence, distinct from the OUT1 keyword
slot. Complete bindings must verify every selected detector's evidence rather than
extrapolate those two printed amplifier labels to the entire mosaic.

All 32 candidate BPM planes are BITPIX 8 with active dimensions 2044 x 4091,
values only 0 and 1, no nonfinite values and no MASKENC/MASKREG. This supports the
legacy binary path, not reason8. The existing Eclipse convention is 1=good; the
binding must declare it explicitly and preserve the original mask. A dense value
of 1 alone is not independent proof of the producer's convention.

Native PAF crop groups are X=51..2094, Y=5..4095 for CHIP1..8/17..24 and
Y=105..4195 for CHIP9..16/25..32. Overscan is X=2100..2142 for the first group and
X=5..48 for the second. Both produce 2044 x 4091 active planes. These are source
configuration declarations, not newly measured crop choices. Resolve logical
identity to the historical native PAF slot using reviewed reference evidence;
Python .cfg entry order is not that slot, and later reordered HDUs must not
silently change the detector's geometry.

Explicit ROI rectangles, physical raw saturation boundary, bias pair selection
and full per-detector amplifier/readout validation remain pending for the actual
measurement launch. No values are silently chosen by this compatibility fix.
Future retained comparison/measurement data belongs under the instrument's
Pictures/.../wenu-imaging directory with its purpose/deletion README, not a build
folder. This qualification creates only reproducible synthetic build/test work;
its directory retention will be reviewed at branch closeout with Fernando.
