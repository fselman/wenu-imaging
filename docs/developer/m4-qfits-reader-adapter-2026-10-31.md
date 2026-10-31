# M4 qfits reader adapter — 31 October 2026

Current [bounded closure review](m4-bounded-closure-review-2026-10-31.md):
revised paired functional gates and the corrected Chapman performance follow-up
are complete at native source 5b251831. Recommend owner acceptance with explicit
limits; do not repeat this test cycle. Earlier pending statements below retain
their historical scope. No automatic merge, installed activation or milestone advance.

Current follow-up: [offset storage correction](qfits-offset-storage-correction-2026-10-31.md)
restores the ordinary stack-buffer path after inspecting the first performance
series. New agent gates pass; revised target qualification is pending. Prior
performance results remain under review and are not replaced by test durations.

Subsequent [paired actual-target qualification](m4-qfits-paired-results-2026-10-31.md)
passes at 5e6bd83 and is owner accepted. Current next step is the
[performance plan review/preparation](m4-performance-comparison-plan-2026-10-31.md),
not a repeat of the functional gates. Earlier pending-target text below is historical.

The owner accepted the [reuse recommendation](m4-header-reader-reuse-review-2026-10-31.md).
M4 now consumes qfits-owned headers and offsets. Its independent maps, strict
selected metadata validation, selector/reference checks and existing Eclipse
plane loader remain. It no longer reads FITS blocks, locates END cards or seeks
over payloads. No second file-framing parser is retained in M4.

## Existing reader and narrowly changed dependency boundary

- qfits_cache_prime_bounded is an additive entry point over the **existing cache
  walker**. It enforces HDU count and header-byte budgets before publication,
  sizes temporary offset storage from the caller limit, checks structural integer
  conversion/multiplication and seek calculations, and refuses unsupported offsets.
  Failed discovery frees pending state without publishing a partial cache entry.
- Existing qfits_query_n_ext/get_hdrinfo/get_datinfo/header_readext are reused.
  Normal signatures remain; ordinary cache-hit lookup stays unchanged. Legacy
  discovery retains its 128-total-HDU limit and now rejects excess before writing
  outside storage. The bounded caller can admit more, including the 140-extension
  control, without changing that legacy limit.
- qfits_header_visit traverses existing stored cards once, in original order,
  with borrowed const views including duplicates. M4 selects and validates fields
  without repeatedly scanning a linked list or copying a working image.
- mef_layout_read obtains each existing qfits header, validates required metadata
  and storage span, destroys the header, and retains its owned compact catalogue.
  Required duplicate-card conflicts still fail. Optional cards stay absent; no
  physical identity, EXTVER, units or calibration choices are invented.

The changed qfits functions retain the bundled dependency's allocator/cache/global
policy. This does not establish fully recoverable dependency OOM, concurrency,
snapshot locking, general table/heap support or a large-file redesign. Normal
pixel loading/scaling and numerical algorithms are unchanged. All opens are for
reading; no repair, serialization, in-place update or installation is performed.

## Explicit byte-offset limit

The legacy public offset APIs return **signed 32-bit int** on selected targets.
The new guard rejects a whole file larger than INT_MAX bytes (2,147,483,647,
just under 2 GiB) before discovery arithmetic. This concerns the complete FITS/MEF,
not each detector or available RAM. It is an explicit refusal of unsupported
representation, not new large-file support. A 64-bit caller variable alone
cannot fix int multiplication/return values inside qfits. Larger-file support
needs a separately designed wider offset path through affected callers/loaders.

Bounded mode requires complete 2880-byte framing and the current raw-image
profile: no random groups, nonzero PCOUNT/heaps or GCOUNT other than one. M4 still
discovers NAXIS<=3 and binds only the already reviewed 2-D planes. Narrowed limits
are stated here rather than silently advertised as a general FITS implementation.
The ordinary legacy query path is checked for arithmetic/range safety; it is not
claimed to acquire every strict raw-profile validator.

## Agent evidence

[Logs, exact sources and receipt](fixtures/agent-m4-qfits-reuse-2026-10-31/receipt.json)
retain optimized C90/C17 builds and focused tests with existing private tools,
without resource installation or observational inputs.

| Check | Result |
|---|---|
| C90 discovery/layout/bias/native paths | 4/4, 23.91 s |
| C17 same four contracts | 4/4, 25.59 s |
| Scoped ASan/UBSan discovery | Passed, 5.37 s |
| Scoped ASan/UBSan layout/bias | 2/2, 5.39 s |

Discovery controls compare ordinary legacy and checked APIs against independently
known offsets for 0/1/8/32 extensions; bounded mode also handles 140. Exact/short
HDU and header budgets, duplicate-card retention, overflowing dimensions and a
2-GiB sparse file have controlled rejection checks. Sparse payload is not read or
hashed; other tiny fixture bytes are preserved. Existing layout/bias controls
retain primary/one-extension/mosaic scaling and known pixels, permutations,
selectors, allocation-owner failures, FIFO rejection and source-change handling.
Native-path regression exercises the actual engine's legacy and explicit paths
with existing tiny OCAM/WFI fixtures and unchanged expected arrays/metadata.

The prior private instrumented qfits library reproduces #194 (index128 beyond a
128-entry array) and #195 (2*2147483647 signed overflow), each stopping with the
expected diagnostic exit86. Before-fix logs/library hash are retained. These are
synthetic agent demonstrations, not observed production failures.

One initial C90 build request occurred before regenerating the newly added target;
its no-rule log is retained. The first sanitizer test launch overlapped the build:
discovery passed, while layout/bias could not start because executables were absent.
After successful build completion, only those two tests were run. The failed log
and corrective evidence are retained under setup issue #196 (closed). No sanitizer
finding is hidden by that setup correction. Leak detection remains disabled for
the existing legacy-cache limitation; this is not leak or performance acceptance.
Final comment-only clarification did not change executed behavior.

## Target handoff and remaining gates

The pinned private qualifier now inventories/runs exactly **four** contracts per
C90/C17 lane: native_qfits_discovery, native_layout, native_bias_service and
native_explicit_paths. It uses the recorded absolute tools, private exports and
builds, no installation or original observations, and checks installed files,
checkout and exported source. Its syntax and agent contracts pass; corrected
Mac then representative Chapman runs are pending. Previous two-contract target
receipts remain valid for the earlier implementation, not this changed boundary.

#194/#195 stay open pending applicable actual-target qualification. M4/PR #186
remain open for remaining actual mapping, shared-context equivalence and matched
optimized performance review. Test durations are not benchmarks. No full reduction
or additional general FITS feature is introduced as a decomposition prerequisite.
