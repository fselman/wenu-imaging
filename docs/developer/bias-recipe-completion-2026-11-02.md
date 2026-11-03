# Bias recipe completion — 2 November 2026

Owner direction: finish the new bias recipe first; afterward create the new BPM
recipe following the template. Bias is the only new recipe implemented. The
legacy BPM builder exists, but the new BPM recipe and two-pass bias/BPM workflow
have not been created. Do not describe other new recipes as existing callers.

## What completion covers

The bounded M5 bias recipe selects one explicit detector, reads an ordered bias
list, uses equivalent PAF or TOML settings, optionally uses an existing BPM on
active pixels, and produces a median-stacked FITS bias plus common ASDF QC for
its inputs/product. Read noise uses an explicitly supplied raw pair before any
overscan correction. Detector BPM is not applicable to electronic scan reads.
The existing C operation template remains the calculation/publication path.

The C17 calculation, file loading/publication, BPM binding and ASDF handoff were
qualified on the actual Intel Mac at eeacca38346a2d09d88e262513abda189d6b01e3:
six contracts passed, zero failures, 22.31s. Retained evidence is
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-asdf-TGJPe5t1`.
Installed files, checkout, exported source and retained QC controls all passed
preservation. This receipt supersedes the pending status in older source notes.

The remaining practical gap was separate native and ASDF commands. The new
`run_bias_recipe` completion entry in `pycavi_bias_qc.py` runs those same existing
steps and verifies the saved product QC and every frozen input/BPM link before
reporting complete. It adds no numerical routine, native code or serializer.
The same script retains writer-only invocation for an existing complete handoff.

## Complete command contract

Use the qualified ASDF Python to execute `Pycavi2/pycavi/pycavi/pycavi_bias_qc.py`.
Supply `--native-adapter ABS_EXECUTABLE`, `--receipt NEW_ABS_JSON`,
`--qc-directory EXISTING_DIR`, `--assessment-id ID`, `--created-at TIMESTAMP`,
then `--` followed by the complete native `cal bias` argument list described in
[the BPM/ASDF handoff](bias-bpm-asdf-handoff-2026-11-02.md). Batch invocations use
niceness at least10. No installation or engine selection is implicit.

The native arguments must explicitly include `--measurements yes --mad yes|no`,
all existing input/configuration/detector/output paths, and either BPM omission
or its selected file/HDU/polarity/geometry. RON remains an optional explicit
pair; an unrequested quantity is saved as unavailable. No estimator, input pair,
scientific threshold or data association is chosen by the outer command.

The new entry point:

1. Validates explicit arguments, writer availability, schema and no-overwrite
   output/receipt/product-QC paths before native processing where possible.
2. Runs the selected native executable through its existing C operation template.
   All images stay in the established qfits/Eclipse/bias path.
3. Accepts only a complete handoff matching this invocation; uses the existing
   shared assembly/schema/ASDF writer, then verifies local frozen references.
4. Reports `BIAS_RECIPE complete` and exit0 only after both FITS and ASDF steps
   and read-back succeed. It records native binary/source producer and the
   completion-module hash for reproducibility.

The execution receipt is JSON attempt evidence, not a second QC format. Its
stages are preflight/native/qc/verify/complete. On an attempted phase failure it
records failed status, phase, native exit code when known, and the error. Invalid
arguments may fail before any attempt/receipt is reserved. An earlier receipt,
including a symlink, is never overwritten. Interrupted work is not called complete.

No automatic retries, deletion, input staging or multi-file transaction is added.
A complete FITS may remain after a later QC failure; completed input ASDF files
may remain after a later publication/verification failure. Retain those files
and the receipt/logs, correct the cause and choose a new explicit attempt.

## Final focused checks

Agent preparation: all six completion cases pass with the existing C17 binary:
PAF with omitted BPM, TOML with an existing BPM, protected output, native missing
HDU, conflicting input QC after FITS success, and protected previous receipt.
The test checks exact zero-valued known-answer FITS pixels for this fixture,
verified record counts, binary/module identities, truthful stages/exit codes,
no false full-recipe success and unchanged source inputs. The prior six native/
ASDF contracts are not repeated. Seven independent synthetic reuse guards pass:
valid lane, changed/additional C source, changed binary, failed prior run,
changed selected tools, and altered prior test evidence.

Actual Mac qualification of the new completion entry remains pending. The
protected runner's `--complete-bias --reuse-native-run ... --qc-python ...`
verifies the passed eeacca3 receipt, C17 configuration, tool identities, prior
CTest log, original Git archive and all native source/build bytes. It matches the
adapter hash against its passed file-bias contract, runs only the seven reuse
guards and six completion cases with new source/outputs, and preserves selected
old native evidence/binary controls. There is no rebuild or old-test replay.
Native producer revision remains eeacca3; the completion-module hash records the
new orchestration separately. Selected installed Python makes fixtures; retained
qualified ASDF Python runs the complete command. No environment provisioning.

## Template and next recipe

The companion [operation template](native-operation-recipe-template.md) now
includes completion/publication lessons: native success is distinct from full
recipe success; preserve failed phase and completed earlier outputs; use one
common QC writer and checked references; test normal and late-failure paths.
The current scope is one detector per invocation, not mosaic aggregation,
recipe-specific partial TOML, installation, production activation, scientific/
observational acceptance, variance propagation or general allocation safety.
Those remain their separately reviewed stages, not hidden requirements for
finishing this bounded bias adapter.

After this completion gate, continue with the **new BPM recipe**: inspect the
existing Eclipse/legacy BPM resources, fill the same operation contract, announce
any genuine missing functionality, and implement through the existing native
operation template and common QC path. Do not invent a two-pass workflow or new
BPM thresholds as part of bias closure. M5 #203 remains open for the later recipes.
