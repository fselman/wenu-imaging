# Format probe declaration correction — 30 October 2026

Actual selected-tool Intel Mac verification of PR #173 at
b4fe1c6a0cbea8728562e60400999da32a1b4547 stopped in the private build, before test
inventory or any functional test. Apple clang rejected implicit declarations of
qfits_warning and qfits_error in the newly introduced format_safety_probe.c.
The normal engine and Eclipse allocation probe built before this stop.
Terminal preservation assertions passed for the installed reduction module,
configured engine/configuration and clean review checkout. Evidence remains at
`/Users/fselman/Software/build/wenu-imaging/mac-native-safety-batch-0q_fourp`.
The uploaded terminal transcript is committed; the full private run has not been
transferred or independently inspected. No Mac functional pass is claimed.

## Cause, origin and correction

[#177](https://github.com/fselman/wenu-imaging/issues/177) is a new test-only
portability defect. qfits.h declares callback controls but not the variadic
warning/error functions used directly by the probe. The exact declarations already
exist in qfits5/src/qerror.h. The probe now includes that existing private header;
no declarations are duplicated and no production API/header/behavior changes.
The format probe target additionally uses -Werror=implicit-function-declaration
with the existing GCC/clang toolchain flags. This strengthens the agent build
rather than weakening Apple clang. Earlier GCC logs did warn about both calls;
those warnings were missed during review and their runs are retained unchanged.

The private header source was inspected before editing. Only CMake's probe options
and one test include changed. Scientific code, expected outputs, fixed clock,
other probes, qfits allocator policy and installed files remain unchanged.
Keep #177 open until corrected actual Mac/representative Chapman checks.

## Corrected agent checks

Using the existing private selected GCC 13.3.0/CMake 3.29.6/Python 3.12.14:

| Lane | Result |
|---|---|
| Optimized/fortified C90 | Strict probe build and native_format_safety 1/1, 0.10 s |
| Optimized/fortified C17 | Same 1/1, 0.10 s |
| Existing optimized C17 ASan/UBSan | Strict probe build and same 1/1, 0.18 s, no findings |

The stricter flags are retained in each compile receipt. Tests keep all exact
short/percent/long diagnostic, ownership, timestamp, overflow and offline RTD
assertions. Leak detection remains explicitly disabled under the known container
limitation; this is not broad memory/leak or real exhaustion qualification.
Only the affected format contract was rerun: the earlier combined C90/C17 4/4
and scoped diagnostic 3/3 evidence remains the original qualification of unchanged
production code, rather than being presented as newly executed full batches.
No Apple clang installation or target-tool requalification occurred in the agent.

See [retained failed/corrected evidence](fixtures/agent-format-prototypes-2026-10-30/README.md).
The new combined source manifest retains all earlier production/test identities,
updates the two corrected test-build files, and adds the private header dependency.
Earlier evidence and manifests are preserved byte-for-byte.

## Next target step

Fast-forward the clean Mac review branch from b4fe1c6 to the exact published
correction. Then use a fresh private export/build with the same four contracts;
protect installed module/configured engine/config and checkout even on failure.
Use the new manifest under agent-format-prototypes-2026-10-30, not the earlier
snapshot's manifest. Preserve the failed Mac directory and archive. Corrected
actual Mac verification precedes Chapman; no tests on Chapman are claimed yet.
PR #173 stays draft; applicable findings stay open. No installation, observation,
numerical change, configured-engine activation, automatic merge or cleanup.
