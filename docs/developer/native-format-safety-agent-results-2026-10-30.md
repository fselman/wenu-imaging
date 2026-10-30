# Native format safety — agent results, 30 October 2026

Target update: [actual Mac probe declaration failure and correction](native-format-prototypes-2026-10-30.md). Earlier agent qualification below is retained; no Mac functional test ran at the first target attempt.

Owner requested batching further related fixes before target synchronization.
PR #173 retains #144 as its first commit; this second increment addresses the
reachable #74 slice and connected inherited #174/#176 findings. See the
[complete scope/origin/remaining-facility table](native-format-safety.md) and
[raw evidence](fixtures/agent-native-format-safety-2026-10-30/README.md).
Actual selected-tool Intel Mac/representative Chapman checks remain pending.
Keep applicable tickets open. #74 retains unqualified legacy facilities.

## Actual checks

Private selected GCC 13.3.0, CMake/CTest 3.29.6 and Python 3.12.14; C90/C17
`-O1 -D_FORTIFY_SOURCE=2`, scoped C17 ASan/UBSan `-O1 -g` with
`detect_leaks=0`, halt-on-error, non-PIE container executable. No install/tool
upgrade, observations, production Pycavi invocation or configured-engine change.
Builds ran at nice 10 with two jobs; existing native-path regression uses the
private already qualified NumPy 1.26.4/Astropy 6.1.7 environment.

| Action | Actual outcome |
|---|---|
| Original comm long message | ASan stack-buffer overflow, expected child failure |
| Original newline-only message | ASan heap under-read, expected child failure |
| Original qfits long message | ASan stack-buffer overflow, expected child failure |
| Original five-digit-year date | ASan global-buffer overflow, expected child failure |
| Original textual FITS dump with `100%%` | Loses literal percent; deliberate verification exit 23 |
| Final combined C90 | Format, allocation, swap, native path: 4/4, 24.36 s |
| Final combined C17 | Same 4/4, 24.26 s |
| Final scoped address/UB checks | Format, allocation, swap: 3/3, 10.53 s; no findings |
| Final provenance-aware format driver | 1/1 each C90/C17/ASan, no product/probe changes |
| Actual Mac/representative Chapman | Pending one combined four-test private C90 run per host |

Original reproductions compile unchanged units from parent
2699aa97228baa22956be30d7e8a68e826ea7c93 into isolated instrumented children with
current private libraries. They are original-function reproductions, not an
entire historical executable. Core dumps are disabled for these children.
The textual dump reproduction uses a double percent to demonstrate corruption
without an unsafe percent-n conversion. All signals/failures remain evidence;
corrected failure controls require explicit status, never a crash substitute.

Each corrected format run has eight ordinary PASS sections plus explicit swap
formatter failure and offline RTD cwd rejection. Its test-only clock preserves
historical local-time/centisecond behavior, including the existing .012 result;
no time-model correction is hidden in buffer work. The failed header-merge
control verifies unchanged qfits byte/cell counts and retains both input headers.
Diagnostic truncation is visibly marked; metadata/filename overflow is rejected.
RTD tests never connect, save an image, or send a command.

The other three contracts preserve the original eight bias equivalence profiles
per PAF, 592 one-shot/persistent injected dependency requests, twenty swap cases,
and sixteen positive/fourteen rejected actual native path profiles. No accepted
numerical oracle or source observation was changed. Broad leak freedom, real
system exhaustion, concurrency, RTD operation and remaining legacy format
facilities are not qualified. The known container LeakSanitizer limitation is
retained rather than replayed or claimed waived.

## Failed preparation and corrected attempts

The first C90 build did not register the newly edited CMake target; explicit
regeneration resolved this without source/tool changes. The first C90/C17 format
runs failed the new probe's four-marker assertion (#175): it passed done=1,total=1
into the historical pre-increment progress routine, which therefore displayed
2 out of 1 and did not log completion. Only the probe input changed to zero; all
four marker assertions remain. The three unrelated contracts passed, and only
the failed format test was retried. Subsequent conditional RTD source corrections
justified the final combined runs listed above.

The first original-header compile lacked the actual private fits_p.h include
directory and did not run. Its failed compile/initial receipt remain; correcting
the include path yielded the expected explicit original corruption result.
The new nested-directory driver was made independent of temporary-path length;
its final provenance-only additions were then verified against all three existing
probes, without another build or broad regression replay. All attempts are retained.

## Exact identity and handoff

Source was dirty on the parent commit during tests; configure-time build-info
honestly records unknown source revision. The combined source hash manifest
identifies final #144 and format production/test bytes. Previous #144 evidence
continues to identify its original separately tested snapshot and is not rewritten.
Current logs/flags and exact original-source origin/diagnostic inventory are retained.

Next is a single guarded Mac review-branch synchronization, then one private
C90 four-test run; then the same on representative shared Chapman. Record paired
results and update the existing draft only after returned evidence. Preserve
selected tools, installed reduction module/configured engine/config, clean
checkout, all original/corrected runs and prior qualification. No automatic
installation, merge, branch deletion, numerical tuning or full-M3 closure.
