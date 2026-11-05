# Bias receipt compatibility correction

5 November 2026. Refs #241/#235/#236; draft PR #227.

Actual Mac preparation_dependencies failed on qualified d25b106 before any
admission, FITS access or native processing. Retain
/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-linearity-preparation-plan-vrhso3qw.
The wrapper's METADATA PRESERVED:False was an unchecked default after an exception,
not evidence of source mutation. The saved qualification confirms exact source
d25b10650bcb5a0a3132cdee3f32e2867ee9f3ff; its native acceptance remains valid.

## Cause and correction

The original locator assumed overall-execution.json with source_preservation=true.
CCD65's real pilot writer instead produces outer-execution.json, with five
preservation guards including inputs and no source_preservation field. The batch
uses overall-execution.json, eight guards including shared_inputs, and identical
inputs/after_inputs. Owner returned both actual receipt summaries: status
complete_for_owner_inspection, all guards true, inputs20/11, batch31 results;
first bias digest matches between receipts.

bias_receipt_fingerprints now treats the local pilot receipt as authoritative
when present, validates detector/master/QC identity and all five pilot guards.
Without a pilot it requires exactly one local/parent batch receipt naming the
selected detector/master result, with all eight guards, source_preservation=true
and inputs==after_inputs. Both formats require complete valid historical bias
hashes. No fallback can bypass a failed pilot. Receipt bytes/hashes remain frozen
in the existing preparation dependency graph. No new image baseline is invented.

Eight standard-library JSON controls passed in0.007s: real pilot and batch
schemas, failed-pilot refusal despite a good batch, incomplete/nonboolean guards,
wrong detector/master, changed batch inputs, missing/invalid hashes and ambiguous
or missing receipts. One changed-boundary synthetic recipe case passed in7.770s
using the existing agent binary. Existing fixture now represents the actual
pilot schema. No broad qualification replay or numerical kernel change.

## Mac recovery

Pycavi2/tools/retry_linearity_admission.py exports exact fetched metadata source
into a fresh Pictures/OCAM/wenu-imaging plan directory. It checks retained source
against the actual qualification fingerprint map and requires all numerical,
configuration and common-QC files to match that qualified source. It uses the
same retained ASDF6 runtime and native executable (fingerprinted, not executed).
It runs only the eight new JSON controls, then validates all32 real master/sample
dependencies and saves plan.json. Progress reports each admitted detector.

Preservation checks cover captured metadata, user checkout, old qualified source,
new metadata source, retained binary and private QC runtime. Unchecked state is
null; an admission failure remains status failed and retains partial evidence.
No FITS images, raw-image hashing, bias construction, independent singleton
extraction, corrected-ROI processing, physical model, installation, merge or
cleanup. Actual all32 recovery remains pending until owner returns the receipt.

After admission, use the qualified native preparation and corrected metadata
recipe to publish a new real corrected-ROI ASDF archive; diagnostics and plots
remain separate, and owner inspection precedes physical modelling. Scientific
algorithms/equations and their existing LaTeX/PDF guide are unchanged.
