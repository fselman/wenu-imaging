# Remaining OCAM bias dependencies — 4 November 2026

The real CCD65 pilot c93dcd9 succeeded at
Pictures/OCAM/wenu-imaging/linearity-bias-CCD65-epw82wy3. Ten of ten biases were
accepted; the native FITS master and commonASDF QC exist. Overall status is
complete_for_owner_inspection with checkout/install/export/private-runtime/input
preservation all true. Raw mean274.055872..278.064218ADU becomes corrected mean
0.031444..0.084165ADU. This shows removal of most frame-level offset variation,
not a quantified scan-estimator error or known median-master variance. Nonfatal
legacy xmem free-NULL messages did not prevent native/ASDF completion.

A second attachment155309 contains output pasted into Bash, producing command-
not-found and syntax errors. It is not evidence of a second bias processing run.
The next controller independently checks clean main and the successful pilot's
retained recipe/provenance before any new observation processing.

`run_ocam_linearity_bias_batch.py` reuses the completedCCD65 pilot and executes
31 remaining native/ASDF bias recipes serially. It copies the exact pilot recipe
choices; only detector/output identity, independent reviewed raw/BPM HDUs, native
slot and new output paths change. No new scan/stack/rejection/RON/polarity setting
is introduced. All ten raw bias files must use a common explicitly reviewed HDU
for the selected detector because that is the existing adapter contract; a mixed
mapping fails instead of guessing. Slots are from maintained geometry, not HDUs.

The original pilot's binary, mapper, configuration/list, master/QC and receipts
are preserved. Eleven shared images (ten raw biases plus structuralBPM) must match
pilot whole-file hashes. They are fully fingerprinted once before the whole batch
and once after, with hashes and stat identities compared. No31 repetitions of
whole-file input hashing. Per-detector native/ASDF completion is provisional until
the guarded batch status passes: this deliberately reuses the same complete bias
recipe/publication controller as the accepted single pilot. Unlike the earlier
raw-pair orchestration, biasASDF publication is part of that existing complete
recipe and is not split or rewritten. A failed source/preservation check makes
the whole batch failed; its per-detector completions cannot establish admission.

The existing bias serializer leaves image-file SHA fields unavailable; shared
whole-file identity evidence resides in overall-execution.json, not invented ASDF
hash fields. ASDF records retain common logical frozen links and measured values.
Future input admission must require the successful outer batch receipt as well
as each completed recipe. All produced FITS/native evidence/ASDF files are also
fingerprinted and verified before overall completion. Keep the master catalogue,
outer receipt and per-detector directories together.

Five focused metadata/orchestration controls pass on the agent: independent and
shuffled mappings, unchanged recipe choices, unsupported mixed-HDU refusal,
serial staging, stop on failure/wrong detector and exactly two shared hash passes
with changed-source refusal. An initial test-only exception assertion expected
ValueError while the helper correctly raises RuntimeError; the assertion was
corrected without changing production behavior. No native estimator test was
failed or changed. The same five small checks run on the Mac before image hashing
or native processing, from byte-verified exported test/controller files. No old
numerical/ASDF test matrix, C build or dependency installation. Actual31-detector
bias batch remains pending; this is the next bounded operational integration.

Final guards cover clean main, installed tools, qualified source, private runtime,
original pilot, native adapter, shared images and all generated products. Failure
retains all partial products/logs and never silently resumes or overwrites. With
all31 complete and guards passed, masters.json indexes32 candidate signal products,
including unchangedCCD65. It points to the required outer batch receipt. No MEF
assembly, plotting, HTML, correction application or accepted calibration occurs.
Master variance remains unavailable; do not insertRON²/N for the median or treat
row-profile stdev as scan-error uncertainty. Real noise/fit choices and correction
coefficients remain pending. Keep#236 open. No install/merge/cleanup.
