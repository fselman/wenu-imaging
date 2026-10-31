# M4 FITS reader reuse review — 31 October 2026

**Recommendation: reuse the existing qfits/Eclipse FITS I/O. M4 should validate
metadata and construct independent detector maps, without a second file-framing
parser.** This is a source/design review for owner decision, not an implemented
replacement, authorization for dependency changes, or acceptance of PR #186.

The owner approved M4 detector/layout work, then challenged the additional
header reader. The candidate chose its own bounded framing implementation without
first making that choice reviewable. The owner instructed this reuse review.
The twelve-observation native audit is paused; the unpublished client and its
small agent fixtures are retained privately, outside the proposed delivery.
No native library, installed program or original observation changes in this review.

## Existing facilities already cover the basic layout need

These findings are from the bundled source at paired-qualified candidate
`2d662b148db56b0292ca6ec3ee9bceb1bc463595`; the relevant existing qfits/Eclipse
implementation is also in accepted main. No external documentation or assumed
behavior is substituted for that source.

| M4 need | Existing code and implication |
|---|---|
| Primary HDU and arbitrary numbered extension headers | [qfits_header_read/readext](../../mefpp2/qfits5/src/fits_rw.c) forwards primary reads to readext(...,0); extension reads accept nonnegative indices. Primary support does not require a new parser or fictitious mosaic. |
| HDU discovery and header/data offsets | [qfits_query_n_ext/get_hdrinfo](../../mefpp2/qfits5/src/simple.c) use the existing [qfits cache](../../mefpp2/qfits5/src/cache.c). Discovery already skips image payloads using structural cards. |
| Ordered cards and duplicate detection | readext appends cards, including original lines, with [qfits_header_append](../../mefpp2/qfits5/src/fits_h.c). It preserves duplicates; getstr returns the first match, so M4 must enumerate cards when detecting conflicts rather than relying only on getstr. The candidate comment about possible coalescing does not describe this existing append path. |
| Required strings, numeric values and optional presence | qfits header accessors provide values; M4 can distinguish absent cards and validate required values strictly. Its identity, selector, units and geometry rules belong above FITS I/O. Do not rely on permissive atoi-based conversions for those rules. |
| Pixel loading and scaling | [image_loadext](../../mefpp2/src/iproc/image_io.c) is already used by the candidate mef_layout_load; primary/extension/mosaic scaling and bias controls passed. There is no reason to replace pixel decoding. |
| Existing pipeline integration | [mefp_lib.c](../../mefpp2/ins/mef/common/mefp_lib.c) already uses qfits_header_read/readext and extension queries; [mef_paths.c](../../mefpp2/ins/mef/common/mef_paths.c) uses them for calibration geometry. Reuse keeps one FITS dependency boundary. |

qfits uses read-only file opens/private mappings for these reads; a whole-file
virtual mapping is not the same as reading or converting every pixel. This
source inspection does not measure I/O or certify all malformed-input behavior.
Raw files must remain immutable; no repair/update/serialization call is proposed.

## What the candidate added

[mef_layout.c](../../mefpp2/ins/mef/common/mef_layout.c) currently contains its own
read_hdu and file traversal. It recognizes 2880-byte blocks, END and structural
cards; calculates payload sizes/padding; seeks between HDUs; validates selected
values; and enforces header/HDU/allocation limits. It reuses qfits_getkey/getvalue
for card parsing and Eclipse for pixels, but this still duplicates substantial
FITS framing/discovery logic. Calling it only a layout layer understated that
choice. Its owned maps, selector checks and compatibility logic are distinct and
remain useful independently of the scanner.

The original goals of bounds, duplicate/conflict detection, unknown-value
preservation, source identity and deterministic failure are legitimate. They do
not establish that a second parser is necessary. In particular, duplicate cards
are available from the existing qfits header object.

## Gaps that cannot be hidden by a thin wrapper

| Existing dependency gap | Consequence for a reuse adapter |
|---|---|
| cache.c has fixed 128-entry offset arrays; extension discovery writes using an incrementing index without a count guard | A post-query count check is too late to protect the scan. Source finding [#194](https://github.com/fselman/wenu-imaging/issues/194); no high-count execution or target failure claimed. |
| Payload sizes, block counters and returned byte offsets use unchecked int arithmetic | Merely storing the result in off_t does not provide checked large-file support. Source finding [#195](https://github.com/fselman/wenu-imaging/issues/195); no large-file experiment claimed. |
| Current discovery/header APIs accept no caller-supplied header-byte/HDU budget | M4 cannot truthfully retain its current pre-read budget guarantee by checking only after a complete legacy read. Review a narrow checked qfits entry point if that guarantee is retained. |
| Dependency allocations/caches and error policy differ from M4's explicit allocator/status objects | A wrapper cannot promise recoverable failure for every underlying dependency allocation. Preserve the already stated limits and qualify any changed ownership boundary. |

Long strings/CONTINUE (#125) and write-status handling (#128) remain separately
deferred. This review neither implements them nor turns a full qfits rewrite
into a prerequisite for decomposition. The ordinary 1/8/32-detector fixtures do
not exercise all the legacy limits above. Existing source defects are not new
observed failures of the qualified production reduction.

## Proposed ownership and implementation boundary

1. **qfits:** own FITS framing, HDU discovery and card storage. Reuse the current
   implementations. If needed for M4's stated contract, propose only checked
   counts, arithmetic/offset handling and bounded discovery through an internal
   or additive entry point sharing the existing machinery. Do not silently alter
   legacy public semantics or introduce another parser in the caller.
2. **M4:** consume owned header metadata, validate the required selected fields,
   retain missing/unknown states, construct per-file identity/selector/geometry
   maps, preserve source order, and check selected/reference compatibility.
   Keep header lookup and validation out of pixel loops.
3. **Eclipse/qfits image loader:** retain existing plane loading and scaling.
   Numerical services continue to consume the same validated planes.

Before code changes, settle whether a narrow checked qfits extension is in scope,
or whether an explicitly narrower existing-reader support contract is acceptable.
The latter must state limits and cannot claim the current general bounded-input
guarantees. This is a real design decision; neither alternative is silently
selected by this review. The recommended direction is reuse with the minimum
reviewed dependency work needed for the accepted contract.

## Evidence retained and next acceptance

The [paired result](m4-native-layout-paired-results-2026-10-31.md) remains valid
for the exact current candidate. Mac and representative Chapman4 each passed
layout+bias in C90 and C17, with installations, clean main and exports preserved.
#185/#193 were closed with correction/evidence comments. Those passes establish
behavior of that implementation; they do not approve its reader architecture.
PR #186 remains draft/on hold for this design decision. No merge, actual-header
audit, normalization/performance campaign or further functional replay follows
from this review.

After the direction is accepted, implement only that change and qualify affected
boundaries: valid primary/one-extension/shuffled MEF metadata, duplicate/missing
cards, actual required bounds, unchanged decoding/plane results, ownership and
same-workload optimized performance. Reuse unaffected evidence; do not restart
the broad historical matrix. M5/M6 calibration/science decomposition remains the
goal; full new reductions and unrelated FITS features are not added here.
