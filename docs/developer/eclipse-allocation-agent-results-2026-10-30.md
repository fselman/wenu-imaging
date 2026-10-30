# Eclipse allocation correction — agent results, 30 October 2026

Batch update: owner authorized [reachable format/buffer corrections](native-format-safety.md) in the same draft PR before one combined four-test Mac/Chapman handoff. This earlier receipt retains the original #144 snapshot, checks and evidence.

Owner authorized #144 at merged main e2460fb72bdbe69f92c7da8994a81d21928569b5.
Branch: `fix/eclipse-allocation-failures`. See [scope/origins/limits](eclipse-allocation-failures.md)
and [retained evidence](fixtures/agent-eclipse-allocation-2026-10-30/README.md).
Actual selected-tool Intel Mac/representative shared Chapman qualification remains
pending; #144/#171/#172 stay open. This is a draft review increment, not full M3.

## Checks actually performed

Private selected GCC 13.3.0, CMake/CTest 3.29.6, Python 3.12.14; no installation.
Compiler `/usr/bin/gcc`, ar/ranlib/make `/usr/bin/…`; Python and CMake paths are in
the receipts. Dependency driver uses the standard library; existing native-path
regression uses private NumPy 1.26.4/Astropy 6.1.7 within project bounds. Builds ran
at nice 10 with two jobs. Builds used dirty source based on e2460fb; configure-time
build-info honestly records unknown source revision. The committed source hash
manifest identifies final tested source/test bytes, independent of build-info.

| Lane/action | Actual result |
|---|---|
| Original four production units at e2460fb with local NULL seams | Eight direct cases fail as expected: six SIGSEGV, image-pixels and overscan-owner assertion aborts |
| Corrected C90 `-O1 -D_FORTIFY_SOURCE=2` | Engine/probe build; allocation and native-path CTests 2/2, 24.41 s |
| Corrected C17, same optimization/fortify | Engine/probe build; same 2/2, 23.69 s |
| C17 `-O1 -g` ASan/UBSan | Allocation suite 1/1, 6.12 s; no address/undefined findings, leak detection disabled |
| Actual selected-tool Mac/representative Chapman | Pending private C90 engine/probe build and same two CTests |

Original reproduction compiles unchanged image_handling, cube_handling,
cube2image and mefp_lib units from e2460fb, linked to the corrected test harness
and remaining units. It demonstrates the named inherited failures, not an
entirely original executable. Each case runs in a separate process with core
dumps disabled; nonzero originals are retained evidence, never accepted as
corrected error handling. No actual OOM was induced.

Each corrected instrument run passes eight exact legacy/FITS/QC profiles, eight
direct controls, 73/75-position single/persistent dependency sweeps and repeated
same-context recovery. There are 592 injected bias attempts across both instruments.
The existing native path test adds 16 positive profiles and 14 rejections through
the actual normal C executable, preserving exact arrays/relevant FITS metadata
and caller/input/calibration state. Existing reference fixtures and numerical
oracles were not edited. No production Pycavi routine or observation was run.
The complete site list and counters are in each instrument log.

## Failed preparation retained

The first new driver used a whitespace temporary prefix incompatible with the
reused legacy list fixture. It failed before engine execution (#172). Only the
prefix was corrected; fixture and all ownership/numerical assertions remain.
The first C17 preparation mistakenly used CMAKE_C_STANDARD and
MEFPP_INSTALL_RESOURCES rather than actual MEFPP_C_STANDARD and
MEFPP_BUILD_RESOURCES. Configure stopped on missing funpack and its subsequent
build could not find a Makefile. Both logs are retained. The corrected preparation
uses actual project options; no funpack installation or dependency change occurred.

## Limits and next step

NULL-return seams exist only in test copies of actual dependency units. This
qualifies the bounded bias propagation contract, not actual global allocator
exhaustion. qfits fatal RAM/swap policy, serial mode 2 and two-million-pointer table
remain unchanged. Scoped sanitizer success is not LeakSanitizer or whole-engine
memory acceptance. Legacy format diagnostics remain visible in build logs (#74).

Proceed Mac first using its established tools and a private exported build. Protect
the actual nested installed reduction module, configured engine/config and clean
checkout on success and failure. Then run the identical checks on representative
shared Chapman. Preserve originals, corrected evidence and installations. No
historical matrix replay, observations, numerical tuning or automatic merge/cleanup.
