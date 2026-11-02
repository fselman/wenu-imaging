# M5 first bias operation template — 2 November 2026

Status: source candidate, actual Mac C17 verification pending. Refs #203.
Base: `47123eedaaa31b4464238ffaaf1b690f7d2cde40`.
No native compilation, functional test, installation, observation processing,
merge or cleanup has been performed while preparing this candidate.

## Owner clarification

Use C17 only for current testing. Do not duplicate tests in C90/C17 or on both
Mac and Chapman. Mac is the current execution host. Assess individual tests
whose memory requirements exceed the Mac's capacity and consider Chapman for
those workloads; do not automatically schedule another platform matrix.
Preserve C90-compatible core source. The previous handoff's prohibition on
preparing native source in the cloud was an assistant-authored overinterpretation,
not an owner restriction. Source preparation and GitHub delivery may continue.

Fernando additionally requires a template subroutine for bias to be reused for
the other operations. This increment implements that shared orchestration,
rather than leaving it as a documentation convention.

## Reusable subroutine and concrete bias adapter

`mef_operation_run` is the shared serial template. Each operation supplies a
typed state object and validation, loading, calculation, optional publication
and cleanup callbacks. The template stops at the first failure, never retries,
always cleans partial temporary state after an attempted operation, and returns
the actual status. The typed adapter transfers an owned result only on success.
An in-memory request omits publication; it uses the same calculation.

Bias is the first concrete implementation. `mef_bias_from_files` supplies an
owned in-memory result; `mef_bias_files_execute` adds publication through the
same template. Both call the existing `mef_cal_bias` calculation. Its scan
correction, trimming, rejection and median stack are unchanged. New BPM, flat
and science services must reuse the template and keep their own explicit inputs,
dependencies, scientific calculations, result types and uncertainty contracts.
This template is not a second scientific dispatcher or a new workflow engine.

The loader reuses M4 catalogues, independent detector maps and Eclipse pixel
loading. Source path, logical detector, physical HDU, configuration detector,
readout, binning, ADU units and geometry are checked. It does not infer detector
identity from the HDU number. Maps may choose the detector independently per file
through the C API. The first command exposes one explicit HDU mapping shared by
its input list; per-file mapping serialization and mosaic aggregation are later
increments, not implicitly implemented by that command.

The header bridge copies the selected configuration detector into one private
legacy header/statistics slot. The source HDU remains a separate argument.
Legacy entry points keep their original behavior. A borrowed original frame
list supplies provenance without writing an intermediate list. Input frames,
result pixels, scan measurements and acceptance flags remain associated with
their original indices, including rejected frames.

Publication reuses the existing header builders and checked qfits pixel writer.
One creation identity is generated per attempt. A temporary output is assembled
in the destination directory; an exclusive hard link publishes it only after
successful FITS writes and close. An existing destination is never replaced.
The temporary assembly is an output, not a raw/calibration staging copy.
Failure removes only that attempt's temporary output, retaining inputs, logs,
records and any previously complete products. The CLI writes a separate QC
record; a later record-write failure produces a nonzero exit and retains a
complete FITS already committed. This is not a multi-file transaction.

Raw primary-image inputs produce a one-extension MEF with an empty primary.
MEF inputs retain their selected detector's original extension metadata and the
existing calibration-header policy. Existing header/clock findings #23/#24/
#125/#128/#207 are not corrected here. The adapter rejects missing EXPTIME,
MJD-OBS or ORIGFILE before entering legacy helpers that require them, and bounds
the existing creation-name and appended keyword formatters. Such rejection is
an explicit limitation, not fabricated replacement metadata. No ESO compliance
claim follows from legacy PHASE3 cards.

## Opt-in command

`MEFPP_BUILD_BIAS_ADAPTER=ON` builds `mefpp_m5` and enables existing configuration
probe dependencies. The target is not installed. Normal `mefpp`, its option-based
recipe, configured engine selection and installed payload remain unchanged.
The command uses explicit flags as a bounded development interface; it does not
implement the proposed request-file schema from architecture review section 15.

```bash
mefpp_m5 cal bias \
  --pafname /config/omegacam.paf \
  --bias /data/lists/bias.list \
  --detector-id detector-B --hdu 2 --config-detector 1 \
  --readout-id configured-readout --bin-x 1 --bin-y 1 \
  --input-bpm omitted \
  --output /reduction/bias-001/bias.fits \
  --work-dir /reduction/bias-001 \
  --log-path /reduction/bias-001/native.log \
  --config-record /reduction/bias-001/config.json \
  --qc-record /reduction/bias-001/qc.json
```

The zero-based configuration index is explicit and independent of HDU 2 and
the logical ID. The example does not assert that this mapping describes an
actual instrument. `--expected-extname` can add an independent assertion.
Input members must be full paths in the supplied legacy list; no raw files are
discovered or copied. Existing list-tokenization limitations remain. Paths,
output parent and work directory are explicit; logs/records must be new.
The output path is an explicit compatibility destination. Future configurable
CMDP/SMDP filename grammar and mosaic publication are not introduced here.

Complete the PAF attempt first. Replace `--pafname` with `--config` and a complete
equivalent native TOML, choose new attempt paths and rerun. The existing M2
reader/document owner is used directly; no PAF is generated or loaded behind
TOML. Source records remain owned by its document while it lives. The numerical
template and writer are identical in both cases. The test uses the accepted
version-1 compatibility-envelope emitter from actual native snapshot bits;
versions 2/3 remain the existing reader's responsibility. Recipe-specific partial
TOML files are still unsupported.

The QC JSON preserves original indices, acceptance, scan median/stdev, explicitly
omitted BPM and legacy variance-unavailable state. Required variances remain M6a.
This record is an execution/QC development artifact, not the future complete
project or ingestion-QC model. Actual output path and ORIGFILE are printed only
after FITS commit. No RON estimator, scientific cuts or new uncertainty option
is added.

## Planned Mac C17 verification

Use `mefpp2/tests/qualify_bias_files_mac.py` from an exact private export with
the already selected tools. Keep the actual checkout on clean main at the base;
fetching the candidate does not require switching the checkout. The runner
builds one optimized C17 lane, two build jobs, one numerical thread, niceness
at least 10. It protects checkout, exported source, installed Pycavi module,
selected native engine and configuration. It stops on a failure and retains
all logs/evidence. It neither installs nor activates a candidate.

| Contract | Actual methods/tools and pass criterion |
|---|---|
| `native_operation_template` | C callbacks verify ordered stages, stop at each injected stage failure, exactly one cleanup and optional in-memory completion |
| `native_bias_files` | Synthetic OCAM/WFI inputs through old `mefpp`, then `mefpp_m5` PAF, then TOML; exact selected-detector pixels, native configuration bits, raw headers except generated ORIGFILE, scan QC and rejected middle-frame indices; primary input, no-clobber output and missing-HDU controls |
| `native_bias_service` | Existing exact frozen-legacy numerical/ownership controls for the unchanged bias calculation |
| `native_layout` | Existing primary/extension mapping, scaling, selectors and compatible loading controls for M4 plus bias |
| `native_explicit_paths` | Existing synthetic full-recipe numerical/header and explicit-path controls to detect regression in the shared legacy header wrappers |

The new end-to-end numerical planes are only 18x9 or 9x9; their arrays occupy
far below 1 MiB. This is not an estimate of the whole process: unchanged qfits/
Eclipse global tables and interpreter overhead remain. No large-memory
observations or >4-GiB fixtures are selected. There is no reason to duplicate
these tiny checks on Chapman. A later full-size stack needs its own memory
estimate, including loaded raw planes, working copies, trimmed stack and output.

Preparing source/tests does not mean that these checks pass. Native execution
and actual-target acceptance are pending; scientific, performance, complete
dependency allocation-failure, thread-safety and ESO Phase 3 gates remain open.
The current loader holds raw planes alongside private calculation copies; it
does not claim low-memory streaming or solve the legacy allocator's spill policy
for large workloads. Review memory before choosing real data. Only after this
boundary is qualified should multi-detector assembly and the remaining operation
adapters build on the template. Keep #203 open.
