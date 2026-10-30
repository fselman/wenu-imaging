# M2 subset composition — agent results — 30 October 2026

After accepted/merged PR #147 and owner-confirmed clean Mac/shared Chapman main
`0550fb90215c636cc6b881eb67e221c24b5ed876`, owner instructed “Proceed” with
reusable subsets and explicit override rules. The
[composition contract](../architecture/proposed/m2/native-subset-composition.md)
defines the prepared increment, version/precedence/allowlist/ownership limits and
remaining M2 work. It stays opt-in; no normal engine/installed selection changes.

Agent Linux x86_64 / GCC 13.3 / Python 3.12.14 / CMake 3.29.6 results:

| Lane | Actual execution | Result |
|---|---|---|
| C90 composition/core, C99 parser/shim | Normal engine and three text probes linked; original compatibility and new subset CTests | 2/2 passed; 1.42 s + 19.71 s, total 21.13 s |
| C17 composition/core, C99 parser/shim | Same targets and two CTests | 2/2 passed; 2.03 s + 15.15 s, total 17.19 s |
| Strict C90/C99 ASan+UBSan | New composition/reader/snapshot/probe and unmodified parser; new subset contract against uninstrumented actual PAF/CLI references | Passed; detect_leaks=0, halt_on_error=1 |

The original regression still matches 585 OCAM, 249 WFI and 249 signed-zero/text
edge stored settings and passes its 41 rejection/recovery cases. Its unsupported
version fixture now uses version 3 since version 2 is intentionally supported.

The new contract checks 16 composition/equivalence profiles, each from two
unrelated caller directories, with all composition/snapshot allocation positions
injected and clone/source-destruction/occupied-output controls. The WFI split
profile exercises 123 composition/snapshot allocation positions per caller
context. Exact effective values are compared with the real PAF constructor;
selected numeric overrides match the actual legacy CLI loader mef_bb_load via
cli_capture_probe, not a second conversion model. Normal mefpp was linked but
not executed; no FITS or Pycavi reduction routine ran.

Thirty-two additional rejection/same-process-recovery cases cover conflicts,
local/forbidden/unused/scoped overrides, hidden invalid child values, unknown
keys, wrong list/version/type/NUL values, missing files, cycles/symlink aliases
and path/depth/file/list resource bounds. Successful controls cover nested
replacements, parent resolution of sibling conflicts in either order, shared
DAGs and identical no-ops. The canonical-path cache is not content identity,
atomic filesystem capture or durable source-provenance serialization.

[Retained reports, commands, modes and hashes](fixtures/agent-m2-toml-subsets-2026-10-30/README.md)
identify the actual runs. The initial new-test failure was a fixture mistake:
2.0 equalled the real WFI reference and was correctly accepted. A distinct 3.0
fixture plus an explicit inequality assertion corrected that case; no native
code change was needed for the failure. The original failed logs remain retained.
Final runs include the fixed 27-key explicit override allowlist and nested/scope
controls. Later numeric catalog additions will not silently expand that policy.

Compile commands confirm C90/C17 composition/mapping and C99 only in the private
parser/shim. The pinned parser source/header/license remain unchanged. Existing
legacy compiler warnings remain; no warning-free or warning-baseline audit claim.
Callback coverage includes C90 composition/snapshot owners, not parser or original
temporary detector-map allocations. No LSan, dependency-wide OOM, thread-safety,
Python-host, astronomical or complete-M2 acceptance follows from these results.

Actual selected Python 3.11.14 / Intel Mac and one representative shared Chapman
C90 build plus the two focused tests are pending. Use the already selected tools
and fresh private exports; no repeat dependency/tool qualification or historical
matrix. Owner review precedes separately instructed merge/cleanup. Full domain,
unit/source/WAD and complete migration work remains M2; other numerical extraction
stays M5/M6 and #133/#144/#75 remain open.
