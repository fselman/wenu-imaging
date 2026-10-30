# Agent M2 subset checks — 30 October 2026

Actual agent Linux x86_64 / GCC 13.3 / Python 3.12.14 / CMake 3.29.6 results.
C90 and C17 CMake builds linked normal mefpp and all three text probes. Both
focused CTests passed in each mode: original 41-case compatibility regression,
and 16 composition/equivalence profiles from two directories with 32 additional
rejection/recovery cases. Strict C90/C99 ASan/UBSan compilation and the new
subset contract passed against uninstrumented PAF and CLI reference probes.
ASAN_OPTIONS=detect_leaks=0; UBSAN_OPTIONS=halt_on_error=1. No LSan, all-process
allocator, concurrency or actual Mac/Chapman claim. Existing legacy warnings
remain; no new warning-baseline audit.

Reports retain original private attempt paths, exact commands and source/probe
hashes. Compile excerpts confirm C90/C17 composition/mapping and C99 only in the
parser/private shim. The parser source/header/license are unchanged from the
accepted pinned upstream. Callback allocation tests now include C90 composition
owners and the returned snapshot; parser/temp detector allocations are excluded.
Per-case target artifacts remain in the original private attempts and are not
all copied here. This fixture does not contain astronomical inputs or products.

The first subset attempt stopped at an invalid rejection fixture: its proposed
conflicting value 2.0 equalled the actual WFI reference 2.0. Native code correctly
accepted an identical definition. The fixture was changed to 3.0 and asserts that
it differs from the reference. The corrected attempt passed; no native fix was
needed for that failure. Later final attempts include the explicit fixed
allowlist and nested-override/scope controls. Original failure logs are retained.
