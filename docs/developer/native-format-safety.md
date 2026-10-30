# Reachable native format and buffer safety — #74 batch

Owner authorized adding related fixes to the existing #144 draft PR #173 before
one combined Mac/Chapman verification. This is a separate commit based on
2699aa97228baa22956be30d7e8a68e826ea7c93, not a separate target campaign.
See [agent evidence](native-format-safety-agent-results-2026-10-30.md).
Actual selected-tool Mac/representative Chapman checks remain pending.

## Complete finding inventory for this increment

| Area | As-is classification | Correction and boundary |
|---|---|---|
| Eclipse warning/error/comment log buffers | Active inherited `vsprintf` into 1024 bytes, even when logging is disabled | Bounded formatting; short log bytes unchanged; oversized diagnostic logs explicitly end `...[truncated]`; full terminal text remains streamed |
| Progress log and log filename | Inherited fixed-size copies | Mark oversized progress logs; reject overlong log filename with an error and disable logging rather than truncate a path |
| Newline-only message format, #174 | Original import has the same empty-buffer under-read | Check empty string on every stripping iteration; preserve ordinary stripping behavior |
| Message format allocation | Existing unchecked `strdup` in diagnostic routines | Return with a fixed stderr diagnostic when the format copy fails; no whole-allocator recovery claim |
| qfits warning/error callbacks | Active inherited unchecked variable formatting plus prefix concatenation | One bounded prefixed message; exact short prefixes/bytes and explicit truncation/error marker |
| Recipe versions in science/Phase3 metadata | Inherited nonliteral calls with fixed, short compiled version arrays | Supply the version directly as header data, retaining both existing distinct version values |
| BPM generated keyword/copy | Inherited prefix-plus-index formatting and treating that generated text as a format | Checked keyword construction rejects overlong result; exact data copy preserves literal percent characters |
| FITS header merge failure, #176 | Same original function: missing diagnostic integer argument and leaked copied header | Supply item index and destroy only owned copy; caller input headers retained |
| Split output/temp names | Earlier path correction already reserves 40 suffix bytes, sufficient for accepted inputs | Explicit bounded formatting/results checks replace reliance on the precondition alone; names and publication policy unchanged |
| qfits swap filename | Original formatting retained; accepted tmpdir setter already reserves 64 suffix bytes | Defensive checked formatting; existing fatal allocation policy on impossible filename failure retained; never open a truncated name |
| Eclipse timestamp buffers | Active engine date and generated-product-name functions; original fixed buffers | 96 bytes cover all signed-int field widths; bounded output; normal bytes, local-time policy and existing centisecond arithmetic unchanged |
| RTD exchange name/command | Conditional generic image-load/display facility, not selected by ordinary FITS checks | Check both buffers and reject overflow before file save/send; offline boundary tests only, no RTD connection or display acceptance |
| qfits textual header dump | Public library diagnostic API; no direct current recipe call found | Output each prepared line as data with `fputs`; no FITS card/CONTINUE redesign or new I/O error-result contract |
| New probe progress input, #175 | Introduced here, not production | Correct 0-based progress input; preserve four truncation-marker assertions and original failed attempts |

Imported Eclipse/mefpp functions in this table compare identical at
c69c314a24e56311dfd0efeb5721c3549aa5cbd0 and this increment's parent, except
for separately described recent integration sites (split/BPM adapters).
Original qfits functions compare identical at
9470098a68ebaf8e2ba67f2bde1f5b1090a2524b. Source-origin function hashes,
original failing probes and corrected evidence are retained. No newly introduced
production cause is attributed to the original code; #175 is explicitly new test code.

## Original #74 diagnostic disposition

The original compiler-assisted audit recorded 19 format diagnostics, not nineteen
observed runtime failures. Its call-graph distinctions remain applicable: object
link demand is not an executed function, and conditional reachability is not an
operational requirement. The first review incorrectly called RTD unused; the
historical graph includes its conditional branch, so both diagnosed RTD buffer
sites are now bounded without claiming RTD operation qualification.

| Original audit unit | Count | Disposition |
|---|---:|---|
| mefpp recipe | 1 | Fixed version used as data |
| mefp_lib | 3 | Two remaining nonliteral calls corrected here; old BPM filename call already removed by accepted path work |
| image_rtd | 1 | Exchange filename fixed; additional optimized command-buffer warning also corrected |
| Eclipse t_iso8601 | 2 | Bounded timestamp buffers corrected |
| fits_h | 1 | Literal diagnostic output corrected |
| qerror | 2 | Bounded diagnostic formatting corrected |
| xmemory | 1 | Defensive filename formatting corrected; accepted setter was already bounded |
| gnuplot_i | 4 | Outside current recipe's potential-call set in the retained audit; unqualified legacy facility |
| qfits t_iso8601 | 1 | Reached by legacy FITS table-writing APIs, not the current image recipe; unqualified |
| tfits | 3 | Legacy FITS table-writing formats, outside current image recipe; unqualified |

Keep #74 open for its remaining facilities and target gates. This is not a claim
that the whole native source tree is buffer-safe. FITS long strings/CONTINUE
#125 and write/flush/close contracts #128 remain separate batches. Other existing
compiler warnings are retained, not silently relabeled as resolved. RTD command
quoting/protocol redesign and display behavior are outside this correction.

## Interface and tests

No installed API or Python production code changes. Existing POSIX snprintf/
vsnprintf support on selected tools is used from C90/C17, as elsewhere in this
project; no claim of a new strictly ISO-C90-only runtime. No algorithms, accepted
expected arrays, FITS short-card serialization, time policy or allocator settings
are changed.

`format_safety_probe` compiles copies of actual message/time/RTD/MEF functions,
using a fixed test-only clock, a local format-copy failure seam, and a local
header-item failure seam. Successful qfits allocation/accounting is real mode 2.
The normal libraries have no test seam. The driver checks exact short diagnostics,
percent-containing data, four marked long logs, empty newline-only formats,
copy failure, exact-fit/overlong keywords, literal header text, owned-copy failure
cleanup, ordinary/five-digit-year timestamps, accepted/rejected swap-name bounds,
and offline RTD command/cwd bounds. A separately corrupted internal tmpdir must
fail with explicit allocator status 47/message; a signal or sanitizer error is
never accepted as correct failure handling. No disk filling, memory exhaustion,
network display or observation is used.

For the combined target batch, build `mefpp`, `eclipse_allocation_probe`,
`format_safety_probe`, and `qfits_swap_probe` with config probes enabled and
resources disabled. Run exactly `native_eclipse_allocation`,
`native_format_safety`, `native_qfits_swap`, and `native_explicit_paths`.
These retain #144's 592 injected requests and all accepted numerical/ownership
regressions, plus the directly affected swap checks. Actual Mac first, then shared
Chapman with selected tools/private exports and protected installation/checkout
identities verified on success and failure. Preserve all failed/corrected evidence.
No historical matrix replay, installation, automatic merge or cleanup.
