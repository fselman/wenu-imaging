# Native ASDF readback correction — 6 November 2026

## Confirmed target evidence

At `bde45688ba604e0098a230edf582e478ca5e8b14`, the actual Mac rebuild
cleared all 63 reported compiler warnings and both native probes passed. Seven
integration groups passed, with two independent ASDF readbacks. The TOML case
with BPM/MAD/RON omitted exceeded 120 seconds (#267). Both detector operations
and final MEF assembly had already completed; the remaining staging ASDF was
255287 bytes. The original result/console/product logs and failed files remain
under `mac-standalone-bias-SP3Cgdhb/checks-warning-fix`.

Independent Python ASDF6 opened, validated and closed that staging file,
reporting two detectors, four embedded input records and zero calibrations.
The retained libasdf0.3 file-backed interface opened it, then exceeded ten
seconds at the first `asdf_get_string0` metadata lookup. No close was reached.
The memory-backed interface read the identical bytes, returned schema version
`2.0.0` with success code zero, and closed normally. The file digest was
preserved in both diagnostics. Its only candidate document-end marker was at
offset255282 and was the valid byte sequence `\n...\n`.

This demonstrates a native file-backed readback failure. It does not demonstrate
invalid ASDF, faulty bias arithmetic or failed TOML ingestion. A review of pinned
upstream 0.3.0 `src/parser.c`/`src/stream.c` found non-progress risks in the fast
file tree scan; the exact internal buffer-state defect is not yet established.
Do not claim that empty calibrations or omitted MAD is the upstream cause.

## Bounded consumer correction

After emitting the staging file and checking its ASDF1.6 header, the native writer
reads its exact bytes with standard C I/O and calls `asdf_open_mem_ex` instead of
`asdf_open_file_ex`. The file must be regular, nonempty and representable by
`size_t`; allocation/read/EOF/close failures prevent publication. All existing
native metadata checks and exclusive link-based publication remain unchanged.
The buffer remains alive through reader/view destruction and is released on
success or error. No serialized fields or file bytes are transformed.

This adds one buffer of the emitted QC sidecar's byte size during readback. It
contains metadata, not raw FITS image arrays. The writer object has already been
closed. No arbitrary size cap, extra QC estimator, external-library modification
or dependency upgrade is introduced. Allocation failure remains an ordinary
publication error. This workaround is specific to the observed library path;
it does not establish that every possible ASDF tree parses without defects.

## Focused verification and next step

Strict consumer C17 syntax checks pass with `-Wall -Wextra -Werror
-pedantic-errors`, using the existing external-header/system-include boundary
and pinned API headers. Python retry-driver syntax passes. An initial direct
check used `-I` for the third-party headers and diagnosed their existing wide
enum; using the CMake target's existing `-isystem` boundary corrects that test
invocation without changing or suppressing consumer checks.

The target memory-interface diagnostic is already passed. Actual corrected
writer integration remains pending. Rebuild only the candidate recipe target
in a new source/build under the retained Mac root. Reuse the previous adapter,
tiny synthetic fixtures and exact unmasked reference products. The driver's
`--reuse-omissions` option runs only the formerly timed-out group, into
`products/toml-no-mad-memory-readback`, independently compares FITS/ASDF/QC,
checks all pre-existing synthetic fixture/output file digests, and writes
`bias-recipe-omissions-retry-results.json`. It neither regenerates fixtures nor
overwrites the original aggregate receipt, failed logs, staging ASDF or MEFs.
The seven passed groups are explicitly reused, not reported as newly executed.

Keep #267 open for the external file-reader limitation even after the consumer
workaround passes. #256 remains pending the corrected omission integration.
No real whole mosaic, installation, merge, viewer or evidence cleanup is
authorized by this correction. Next after target acceptance: obtain exact
current real inputs/configuration/BPM/RON and orchestration/products paths for
the agreed actual whole-mosaic run.
