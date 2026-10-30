# Format probe declaration evidence — 30 October 2026

See [the correction receipt](../../native-format-prototypes-2026-10-30.md).
The actual Mac terminal transcript records a build failure before any tests,
and successful installed-file/checkout preservation assertions. Full original
run remains on the Mac, not independently transferred/inspected here.
New test code #177 includes the existing private declarations and makes missing
declarations fatal on GCC as well. Corrected C90/C17/scoped ASan builds and
format-only controls pass. Earlier combined suites were not replayed because
production code did not change. The combined source manifest adds qerror.h and
updates only the two test-build files; earlier manifests/raw runs remain intact.
Actual corrected Mac and representative Chapman qualification is still pending.
