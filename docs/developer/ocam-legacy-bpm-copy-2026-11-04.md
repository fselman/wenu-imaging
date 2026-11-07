# Legacy OCAM BPM structural compatibility copy — 4 November 2026

Issue #232; draft PR #227. This is an explicit input-format derivative, not a
relaxation of native FITS admission or recalculation of the approved binary mask.

## Evidence

Actual Intel Mac #231 qualification of512092fa passed2/2 in5.56s with all three
preservation checks true; retained mac-extname-binding-it2gdv4q. The real retry
ccd65-raw-pairs-extname-w5wjs5pr passes all flat/bias bindings then fails layout
discovery on OCAM_BPM_1x1.fits before pixel loads. Outer checkout/install/export
checks pass; final source fingerprint verification is not reached on native failure.

Owner's read-only header receipt confirms33 HDUs, empty primary and32 unsigned8
2044x4091 IMAGE extensions with exact detector identities. Each summary lacks
PCOUNT/GCOUNT; the full first extension confirms this. FITS image extensions require
PCOUNT=0 and GCOUNT=1 (NASA FITS Standard section7.1, table7.1):
https://fits.gsfc.nasa.gov/standard30/htmlfiles/fits_standard3000054.html
No selected duplicate cards were reported; original stat was preserved.

## Copy contract

Use the installed Astropy FITS header/offset reader; do not implement a second
FITS parser or load image arrays. Require the reviewed32-detector OCAM1x1 geometry
and processing crops. Require empty primary, exact independent unique identities,
BITPIX8 unscaled2D images, expected active dimensions, exact stored spans and EOF.
Refuse duplicate structural/identity cards, conflicting PCOUNT/GCOUNT, CHECKSUM
that would require a separate update, and a pre-existing output path.

The CLI requires original SHA256 from the failed runner's frozen input records.
Match that fingerprint before writing. Add missing count cards in mandatory order
in a separately named OCAM_BPM_1x1_structural.fits. Stream-copy payload and padding
from library-reported offsets, without numerical decoding. Strictly verify the
copy, compare all pre-existing cards and independently reread/hash every copied
payload including padding. Check original full hash and stat again after copying.
Record original/copy hashes, per-HDU offsets/lengths/data hashes, additions and
configuration hashes in preparation.json. README specifies purpose/retention.
Failure is truthful and retains partial evidence. No scientific acceptance implied.

## Verification and next action

Seven agent synthetic tests pass in0.166s: missing counts/exact pixel+nonzero-padding
and metadata equality; byte-identical already-standard input; refusals for conflicting
counts, duplicate identity, wrong detector set, changed source hash and existing output.
Synthetic data are tiny. Agent Astropy7.1.1 is an isolated preparation dependency,
not a change to the user's environment or project dependency versions.

Actual Mac step: export helper/tests from exact delivered source, run those seven
new checks with existing installed imaging Python, then prepare copy under a fresh
Pictures/OCAM/wenu-imaging/legacy-bpm-structure-* purpose directory using retained
qualified512092fa profiles. No native rebuild/replay. Inspect its receipt before
creating a derived execution selection pointing to this byte-verified copy with
explicit original lineage. Preserve approved bias pair, raw exclusion>=65534 ADU,
binary1=good, all ten acquisition-order pairs and five ROIs. No real measurement
is launched by preparation. Keep #232 open pending actual preparation and binding.

Keep both failed measurement attempts, original BPM and retained native builds.
No installation, activation, fit, branch merge or deletion is part of this correction.
