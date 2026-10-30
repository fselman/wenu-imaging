# Agent first-bias-service evidence — 29 October 2026

Base: 98454283341a5bbce641119bed686fa56ff9c44b (accepted PR #143).
Agent Ubuntu GCC 13.3.0, explicit /usr/bin/cc. This is agent evidence, not Mac
or Chapman execution. No CMake executable was available in this workspace;
recorded manual compile commands are preparation, not a target-tool workaround.
Use the selected CMake/CTest on the actual target computers.

C90, C17 and C90 ASan/UBSan each pass eight synthetic profiles for both OCAM/WFI,
including exact frozen legacy pixels/QC, actual changed mef_build_cal tiny-MEF
loading, independent analytic values and preservation checks. The only FITS
are tiny generated fixtures; no astronomical data or native recipe is run.
24 new-owner allocation positions x transient/persistent failures and twenty
success cycles per instrument pass; owner counts return to baseline/zero.
ASAN_OPTIONS=detect_leaks=0; UBSAN_OPTIONS=halt_on_error=1. Retained Eclipse
allocator failure paths are not covered; open #144 limits memory claims.

Focused C90 configuration/runtime/51-case CLI/17-case two-directory input
regressions also pass. Their complete reports are included; detailed logs
remain at the reported scratch paths and are reproducible with their drivers.
Exact source/probe/fixture identities and actual command statuses are recorded.
No target C17/sanitizer, LSan, full-engine memory or scientific claim.
Earlier in-memory-only runs remain in scratch; these final bias reports also
cover the legacy FITS bridge and analytic values. No functional failure or
numerical correction occurred during this increment.
