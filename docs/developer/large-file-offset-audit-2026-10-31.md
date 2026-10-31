# File-offset migration audit — 31 October 2026

Audit baseline: merged main `38b27f8da943acfdd83b9f1cc9a243405e346a96`.
Owner requested an audit before implementation, ahead of M5. Related issue: #195.
This document changes no C source, API, build, installation or observation.
Findings are source observations, not newly reproduced runtime failures.

## Assessment and proposed scope

Recommend proceeding before M5, as a coherent cross-layer I/O migration. Merely
changing cache arrays or removing the INT_MAX refusal would be unsafe: consumers
still narrow offsets, pixel-byte arithmetic can overflow, and output padding
narrows stat sizes. A MEF can exceed 2 GiB while every CCD plane is small.

Use signed `off_t` for on-disk positions/spans and checked `size_t` for addressable
buffers and transfer lengths. Current CMake already requires at least 64-bit
off_t. Retain C90 source compatibility through the existing POSIX environment;
do not adopt long long, C99 int64_t or a new dependency merely to name the type.
Use fseeko/ftello consistently, check their availability in the existing build,
and check all arithmetic/conversions before calling mmap, allocation or I/O.
Off_t alone does not prove addressability: size_t and pointer-range bounds matter.

First target: large aggregate FITS/MEF files, later headers/data and later cube
planes, with individually supported image dimensions/pixel counts. Preserve
existing numerical types, HDU numbering, detector identity/order, scaling and
processing. Explicitly retain/reject unsupported huge individual planes and
table dimensions. Widening file positions is not an all-image-index migration.

Prefer new status-plus-wide-output segment queries, backed by one wide scanner.
Keep old int APIs as checked compatibility wrappers that return failure when a
requested result cannot be represented. Do not silently change an int return
into a wide value under an old prototype. Migrate every bundled byte-offset
consumer to the wide queries. qfits_query_n_ext remains int-valued, a count.
Public qfitsloader segment fields and qfits_col.off_beg also need widening;
these change structure layout, so all linked clients need a coherent rebuild.
Compatibility wrappers do not preserve binary compatibility of changed structs.

## Complete proposed core edit inventory

Paths below are relative to the repository. These are 20 existing source/header/
build files for the recommended coherent scope, including two dormant Eclipse
file-size helpers for interface consistency. New helper/test files are additional.
Line references refer to the baseline and will move during implementation.

| File | Required change and source evidence |
|---|---|
| mefpp2/qfits5/src/cache.c | Lines 77–90: filesize, block count, offset/size arrays are int. Lines 309–367: int answer and block-to-byte multiplication. Lines 425–818: scanner locals, growth allocations/sizeof(int), BITPIX/axis products, padding, seeks, stat assignments and debug formats. Keep count/budget controls; replace the whole-file refusal only after the full chain is wide. |
| mefpp2/qfits5/src/cache.h | Declare wide query path, preserve checked legacy entry, update int-offset documentation/examples. Count/flag selector remains int. |
| mefpp2/qfits5/src/simple.c | Lines 122–193: segment locals and mapping boundary. Lines 482–543: get_hdrinfo/get_datinfo output APIs and failure handling. Lines 563–707: hs, hs+1, mmap lengths and two explicit pointer-difference-to-int casts. Check query status before using output. |
| mefpp2/qfits5/src/simple.h | Wide segment declarations and compatibility contract, including required type includes. |
| mefpp2/qfits5/src/pixio.c | Lines 81–159: loader segments and seg_start+seg_size. Lines 357–506: datastart, image/window/line bytes, plane offset, seek strides, fread return and conversions. Lines 868–1263: int dump byte count and allocation/copy products. Retain representable pixel-count limits and check before multiplication. Fix diagnostic formats too. |
| mefpp2/qfits5/src/pixio.h | qfitsloader.seg_start/seg_size and example formats, with type visibility. Pixel values, dimensions and HDU/plane ordinals are separate. |
| mefpp2/qfits5/src/fits_rw.c | Lines 268–330: header segments, mapping bounds, (int)(where-start) and seg_size+80. Lines 345–365: zeropad casts st_size to int before modulus; compute from wide size, keep bounded pad count. |
| mefpp2/qfits5/src/tfits.c | Lines 409–615: absolute offset_beg, data_size, running column position, table byte product. Lines 671–844: offset plus row stride, selection allocations and mapped bounds. Retain explicit row/field count limits; checked refusal for unsupported table shapes. |
| mefpp2/qfits5/src/tfits.h | qfits_col.off_beg and qfits_col_fill offset argument are int. Although field comment says relative, loading initializes it from the absolute data start. Widen and correct documentation. |
| mefpp2/qfits5/include/qfits.h | Installed umbrella duplicates loader/table structs, column-fill prototype and segment query declarations. Must match private headers, examples and wide type visibility. |
| mefpp2/qfits5/src/xmemory.c | Lines 789–1006: mapping API already uses size_t, not int. Add explicit nonnegative/representable stat-to-size_t and pointer-span checks before whole-file mappings and offs arithmetic. Preserve actual mapping base/length for unmap. First-map and cached-map returned-size conventions differ; reconcile with audited callers, not an unrelated allocator rewrite. |
| mefpp2/src/iproc/cube_load.c | Lines 322–443: cube_getinfo header byte length and wide-query call. Other cube loaders inherit widened qfitsloader without offset-local changes. |
| mefpp2/src/include/local_types.h | cube_info.headersize is int; widen byte-length field to match its producer. |
| mefpp2/src/unix/file_handling.c | Lines 73–84: filesize returns (int)stat.st_size. Provide wide size/checked compatibility behavior. No in-tree call sites found; still a public Eclipse helper. |
| mefpp2/src/include/file_handling.h | Match filesize contract/prototype and update int-size documentation. |
| mefpp2/src/iproc/cube_save.c | Line 496: appended->lx * appended->ly is evaluated in int before assigning qd.npix. Validate retained pixel-count limit before multiplication at writer boundary; inherit wide byte transfers in qfits. |
| mefpp2/ins/mef/common/mefp_lib.c | Lines 1603–1686: split data_beg, mapped-buffer conversion/bounds, long/ftell output position. Lines 4678–4716: checked writer byte totals, qd.npix dimension product before its later off_t cast, addition/padding overflow. |
| mefpp2/ins/mef/common/mef_layout.c | Lines 229–266: segment locals, explicit INT_MAX whole-file rejection, wide-to-size_t payload comparisons. Keep per-plane/count limits at 339–340; these are not file-offset limits. |
| mefpp2/ins/mef/common/mef_layout.h | Replace current explicit 2-GiB whole-file contract with implemented wide range and retained shape/addressability limits. No public offset fields currently need widening here. |
| mefpp2/CMakeLists.txt | Existing off_t-size check is useful and should remain. Check fseeko/ftello under selected feature definitions; ensure declarations/types are coherent for all relevant targets. No tool upgrade or build-system migration. |

No new type header is mandatory if public/private headers use off_t with
sys/types.h. If implementation selects a shared named type/helper header, it
must be an explicit additional file with matching installation rules. Likewise
platform_config.h.in needs modification only if new configure results are emitted
there; it does not currently impose the int offset restriction.

## Bundled utilities: six additional files

These are outside the current CMake QFITS_SOURCES library/normal mefpp executable.
They must be changed (or explicitly excluded from large-file support) before
claiming that the entire bundled qfits tool suite supports large files. Recommend
including their I/O corrections in the scope rather than leaving silent traps.
Their historical modifying operations are not permission to touch raw data.

| File | Required change |
|---|---|
| mefpp2/qfits5/main/dfits.c | Independent scanner: int data_bytes/skip_blocks, atoi multiplication and fseek at 178–308. Widen/check its traversal too; changing library cache does not fix it. |
| mefpp2/qfits5/main/flipx.c | int dstart at 59 and get_hdrinfo call at 108; widen byte positions, validate mapping/row-byte bounds and convert at pointer boundary. Existing call requests header start, not data start: semantic correctness is tracked in #198, not solved by a type change. |
| mefpp2/qfits5/saft/stripfits.c | int file/header/output sizes and pixel counts at 102–108; local filesize explicitly casts stat size at 259. Widen/check copy and output sizing. |
| mefpp2/qfits5/saft/iofits.c | int file sizes, padding, remaining/copy bytes at 174–185, size-changing pixel conversions, lseek offset at 312, local stat cast at 384. |
| mefpp2/qfits5/saft/hierarch28.c | fs=(int)fileinfo.st_size at 276; search_and_replace_kw takes int buffer size at 379. Widen mapping/search span and bounds. |
| mefpp2/qfits5/saft/fitsmd5.c | int cumulative cur_off/off_md5 at 491–492; whole-file MD5Update at 684 implicitly converts st_size to unsigned int len (declared at 149). Chunk the feed, not the MD5 algorithm/state word types. At 4 GiB and above this call can truncate its input length (#199). |

## Coercions and arithmetic that must not be missed

| Pattern | Why a wider destination alone fails |
|---|---|
| wide = int_a * int_b | Multiplication overflows before assignment. Widen a validated operand first, then check product range. |
| (off_t)qd.npix after qd.npix=lx*ly | The later cast cannot repair earlier int overflow. Validate dimensions before computing the count. |
| data_start = seg_start + pnum*imagesize | All terms and intermediate plane-byte product must be checked, including later cube planes beyond 2 GiB. |
| stat.st_size -> int; wide query -> int local/output pointer | Narrowing occurs at storage/API boundaries, not just explicit casts. Never cast int* to off_t*: it permits overwriting caller memory. |
| int* arrays changed but sizeof(int) retained | Allocations/copies become too small; stack and growth buffers, final arrays and debug code must change together. |
| (int)(where-start), (int)(where-buf2) | Pointer difference is narrowed; use validated pointer/size ranges without int truncation. |
| seg_start + seg_size; padding round-up | Addition can overflow even in 64 bits. Check against file/end limits before addition; derive padding without overflowing round-up. |
| signed off_t <-> unsigned size_t | Negative values and oversized lengths can wrap. Check sign and representability before converting or pointer arithmetic. |
| fread -> int dataread | Return is size_t; retain size_t for transfer length/result. |
| MD5Update(..., sta.st_size) | An implicit parameter conversion to unsigned int truncates a whole-file length; feed bounded chunks. |
| printf %d for widened offset | Variadic argument type mismatch, not merely cosmetic. Audit examples and debug-only branches as well. |
| fseek/ftell via long | Long is wide on current LP64 targets, but the intended file-position contract should use off_t/fseeko/ftello. Check function return conventions correctly. |

## Inspected paths not requiring offset edits

- mefpp2/src/iproc/image_io.c, mefpp2/ins/mef/common/mef_paths.c and
  mefpp2/ins/mef/recipes/mefpp.c: image wrapper, extension counts and orchestration
  do not store file byte positions. Rebuild and exercise representative paths.
- mefpp2/qfits5/src/qfits_wrap.c: old Python wrapper requests headers/counts,
  not byte offsets. It is outside the current CMake build; no wrapper redesign.
- mefpp2/qfits5/src/fits_md5.c and src/md5.c: library FITS hashing feeds bounded
  blocks. Do not widen MD5's intentional 32-bit algorithm words or pixel ints.
- mefpp2/qfits5/include/xmemory.h: falloc/fdealloc already use size_t offsets/
  lengths. Preserve that memory-facing interface; change checked conversions in
  xmemory.c, not every caller to off_t indiscriminately.
- mefpp2/qfits5/src/fits_h.c: integer header accessor remains appropriate for
  retained int-sized dimensions/counts; wide storage arithmetic/parser belongs
  to scanner. A future individual-axis expansion would change that assessment.
- mefpp2/ins/mef/common/mef_toml_bridge.c: fseek/ftell is for a capped 4-MiB
  configuration input, not FITS data; no large-image migration needed there.
- Spatial-registration offsets in shift/xcorrelation code are image shifts,
  unrelated to file positions. No mass replacement of the word offset or int.

## Verification changes to prepare only after audit review

Existing mefpp2/tests/qfits_discovery_probe.c must use wide locals/output formats;
qfits_discovery_contract.py must distinguish valid large sparse FITS success from
malformed/overflow failure instead of requiring every 2**31-byte file to fail.
Add a dedicated large-file I/O probe/contract (new files) wired in CMake, rather
than expanding unrelated BPM/configuration suites. Preserve original evidence.

Use valid synthetic sparse MEFs with actual later HDUs/pixels beyond 2 GiB and
4 GiB, read a small recognizable last detector through mapped and copied/window
paths, test later cube-plane positioning, split and output padding, table column
offset if table API is included, and controlled arithmetic-overflow refusals.
A huge sparse file alone or a metadata-only read cannot establish pixel support.
Keep sentinel values and exact ordinary-file pixels/headers independent of the
new reader. Never scan/hash all sparse payload merely to prove preservation.
Check sparse support/logical and physical disk use before creating fixtures.

Compile C90 and C17 with selected tools, check conversion diagnostics within
the changed boundary, run focused agent sanitizer controls and Mac/representative
Chapman verification. Do not repeat unrelated historical test matrices. Utility
checks need their own bounded harness because current CMake does not build them.
There is no new run or passing test claim in this audit.

## Critical opinion and remaining limits

This is a medium cross-layer compatibility change, not a difficult new FITS
algorithm and not a one-line fix. It is well placed before decomposition: future
services should share one correct I/O contract rather than inherit a 2-GiB ceiling.
No new header reader, format backend, numerical method or library replacement is
needed. Existing bounds checks should be generalized, not removed.

Costs are API/struct consistency, careful overflow handling and focused boundary
tests. Wide cached entries roughly double the bytes of the four int offset/size
arrays; a 128-entry pair of temporary 64-bit arrays uses about 2 KiB rather than
1 KiB. This is small relative to images but should be stated, not called free.
Keep ordinary stack storage and actual-count growth; avoid the allocation
regression just corrected in #197. Wide offsets should not introduce per-pixel
checks or extra full-plane copies.

Whole-file mmap remains a virtual-address-space strategy, not a requirement that
the entire file reside in RAM. Widening positions does not make huge single-plane
algorithms, memory exhaustion, arbitrary FITS heaps/tables or very high detector
counts supported. Existing legacy HDU count limits are independent of byte width.
The implementation should report exact supported ranges, preserve safe refusal
for the rest and retain full-size performance obligations. Audit review precedes
implementation; M5 is paused for this requested priority change.
