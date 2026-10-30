# M1 first concrete operation: master bias

Owner authorized continuation after acceptance/merge of PR #143 and clean Mac
and shared Chapman main `98454283341a5bbce641119bed686fa56ff9c44b`.
The owner also selected [grouped native commands](../command-line-services.md).
This increment implements the first numerical service with the accepted C90
validation/calculation/postcondition/qc/ownership pattern. It does not complete
M1 or implement the grouped CLI.

## Processing and ownership

`mef_cal_bias.h/.c` takes an immutable common context and an operation-specific
payload of borrowed raw ADU image planes in the exact resolved request order.
The caller explicitly supplies the configuration-detector index, independent of
physical HDU and detector identity. No pixel or configuration mutation reaches
the caller: working image planes and scan geometry are copies. The supplied
planes must remain stable during the call; their identity/content matching is
the loader's responsibility, not inferred from filenames here.

The service validates the operation/version, resolved bindings, one-detector
coverage, counts, finite pixels, common dimensions, valid legacy scan/trim
geometry, rejection parameters and configuration index before processing.
Initial scope is a selected CCD/MEF detector, at least three required frames,
explicit BPM omission and no applied calibration. Selected BPMs or other
calibrations fail as unsupported rather than being silently ignored; primary
image layouts and multiple detectors remain M4/generalization work. Negative or
nonfinite kappa and unsafe geometry fail as configuration errors. This is input
domain validation, not new scientific QC/rejection policy.

`mef_config_bias_settings` copies the needed typed settings from the accepted
snapshot. A small local legacy bridge calls the unchanged
`mef_overscan_correction` separately on each copied plane; it retains scan QC
for every original frame, including subsequently rejected ones. No PAF reader,
CLI parser, file discovery, process cwd change or output writer runs inside the
service. The common context's allocator is available as a borrowed internal
view; callback/user lifetime rules remain unchanged.

`mef_bias_kernel.h/.c` extracts frame-mean rejection and median stacking from
`mef_build_cal`. Both the existing recipe function's bias branch and the new
service call that same kernel; there is no second maintained bias algorithm.
The kernel consumes its private cube on success or failure. Arithmetic order,
double intermediate values, strict rejection endpoints, sample sigma, existing
float QC conversions and Eclipse's median implementation remain unchanged.
Flat-specific processing remains in `mef_build_cal`. Legacy verbose bias
rejection messages are no longer all emitted at their former positions; the
structured service QC carries the explicit per-frame decisions. Headers and
FITS writing remain the existing writer's responsibility.

`mef_bias_result` is an operation-specific owner, rather than pretending that a
metadata-only `mef_result` owns numerical pixels. It owns the signal, an
independent copied resolved request, QC arrays and allocator. It survives
context/input destruction. Every result/error output starts NULL; occupied
outputs stay intact. Partial construction is destructible, one cleanup path
releases still-local resources, and only complete success transfers the result.
Primary status remains authoritative if diagnostic allocation also fails.

The metadata-only `mef_execute` remains explicitly unsupported because it has no
image payload. The first numerical caller uses `mef_cal_bias` directly. These
internal uninstalled types/signatures are not a frozen ABI or the permanent
mefppy exposure of Eclipse objects.

## QC and uncertainty

The explicit final qc phase collects the measurements already used/written by
the old calculation: average and sample sigma of frame means, rejection limits,
retained count, product median/stdev, each original frame's scan median/stdev,
and its rejection decision. Existing pre-trim scan information remains available.
Signal and scan levels are ADU; counts are frames; the method is the retained
legacy algorithm, not a newly qualified estimator.

The result explicitly says BPM omitted/not applied, RON estimate unavailable,
and `MEF_BIAS_VARIANCE_UNAVAILABLE_LEGACY`. There is no invented RON estimate,
new quality threshold, automatic gain/RON/header replacement or scientific
acceptance decision. Variance creation/propagation remains required at M6a;
this is the explicitly marked pre-M6a compatibility lane, not a variance-off
mode for the future chain.

## Verification and limits

`bias_legacy_reference.c` freezes the complete `mef_build_cal` body from the
accepted baseline above, byte-for-byte except test-only macro name/loader
substitution outside the body. It provides an independent arithmetic oracle;
it is not linked into the production engine. The reference loader supplies
copies of the synthetic raw planes. The actual changed `mef_build_cal` also
reads matching tiny synthetic MEF FITS through the unmodified file/list/qfits
loaders, so the shared-kernel wiring is tested rather than merely inspected.

Eight profiles for each OCAM/WFI constructor configuration cover odd/even frame
counts, rejection of an outlier, zero-scatter rejection, zero kappa, prescan-only,
overscan-only and rejected scan samples. Geometry overrides are confined to
tiny synthetic fixtures. Exact signal bytes, stored QC bytes, original-frame
scan arrays and counts match the frozen reference. Independent analytic pixel
checks retain the old lower median for even counts. Input buffers, synthetic
FITS/list files, source/configuration files and parent cwd remain unchanged.
The explicit configuration index deliberately differs from physical HDU 2.

Controls include a NULL context and occupied outputs, selected BPM, multiple detectors,
unsupported primary layout, wrong operation, count/dimension/configuration-index
errors, nonfinite pixels, invalid trim, independent result lifetime, twenty
success cycles and all 24 new-owner success-path allocation positions in both
transient and persistent failure modes per instrument profile. New owner counts
return to baseline/zero; no partial result escapes.

Agent Ubuntu GCC 13.3 C90/C17 and C90 ASan/UBSan pass. Changed numerical/service
sources and the new probe pass strict `-pedantic-errors -Wall -Wextra -Werror`.
Retained legacy warnings are not repaired incidentally. ASAN_OPTIONS is
`detect_leaks=0`; no LeakSanitizer pass or whole-engine memory acceptance is
claimed. Existing configuration/runtime/CLI/file-list focused regressions are
run separately and recorded with this increment's agent evidence.

[#144](https://github.com/fselman/wenu-imaging/issues/144) records source-confirmed
unchecked allocations in retained Eclipse image/median/cube-rejection helpers.
The new allocator injection covers new owners/request/diagnostic allocations,
not those dependencies; no dependency OOM/crash-safety, reentrancy or thread
safety is claimed. The legacy wrapper's broader failure behavior remains its
existing scope under #75. No full historical matrix is repeated.

Actual Intel Mac and representative shared Chapman C90 CMake builds and all five
focused CTests now pass 5/5 at f5858310e505bfc1b137491dc35676b9245ce674,
including the normal engine link and opt-in probes. See the
[paired receipt](../../../developer/m1-bias-paired-results-2026-10-29.md) for exact
paths, times and limits. Target C17/sanitizer results are not claimed. This is
ready for bounded owner review; no repeated test/build is needed for the receipt. No install, observational
reduction, native recipe launch, automatic repair/retry, tool requalification,
merge or branch cleanup is performed by this delivery. The historical Makefile
also includes the shared kernel; it has not been newly qualified as a separate
build lane.

## Remaining work

Keep normal installed engine/package selection unchanged. General loader/path
integration, grouped command adapters and M1 closure remain separate subsequent
work; TOML/ASDF/WAD persistence, new calibration mathematics, masks and required
variances retain their milestones. Do not treat a numerical in-memory result
as a published FITS product or an accepted full reduction.
