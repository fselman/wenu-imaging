# IO-0 frozen implementation plan — approved roadmap v1.0

Owner approved roadmap v1.0 in this conversation after fetching 6f5026583edf3ee7e82a13aa896b2fb4bceda99c.
Client date: 31 October 2026 (America/Santiago); roadmap filename/date uses
the original UTC document date. Approval is for ordered IO-0 through IO-6,
not merge/installation. #195 remains open. M5 is paused for this increment.

## Interfaces fixed before C edits

- Add int qfits_get_hdrinfo_wide(char *, int, off_t *, off_t *) and
  int qfits_get_datinfo_wide(char *, int, off_t *, off_t *).
- Shared private query: int qfits_query_wide(char *, int, off_t *).
- Old int APIs retain signatures, validate all requested outputs before assigning,
  fail on unrepresentable requested results, and leave outputs unchanged on failure.
- qfits_query_n_ext and ordinal/count parameters stay int.
- Only qfitsloader.seg_start and seg_size become off_t in both header copies.
  All private clients rebuild together; no claim of binary ABI compatibility.
- File positions/spans use off_t; transfers/mapping lengths use checked size_t.
  Current supported LP64 targets permit long for diagnostics/parser; build checks
  must explicitly verify signed off_t and sufficiently wide long/size_t before
  using that relationship. No int64_t/C99 source feature introduced.
- Per-plane pixels must fit int, raw/decoded plane byte products must fit the
  retained supported/addressable limits. Segment/cube aggregate sizes may be wide.
- Legacy HDU limits remain 128 total unless explicitly bounded priming is used.
  Fixtures use 66 total HDUs, within the existing ordinary limit.

## Exact synthetic fixtures and operation

Large MEF: one 2880-byte empty primary header and 65 IMAGE extensions. Each
extension has a 2880-byte header, BITPIX=-32, axes 4096x4096, BSCALE=1, BZERO=0,
stable EXTNAME/EXTVER and a deterministic detector ID. Pixel payload is
67,108,864 bytes, padded to 67,109,760. Total input and matching output size:
4,362,324,480 bytes (4.062731266 GiB). Inputs are sparse zero-valued float32
planes with independently written, nonzero sentinel pixels.

Large cube: a valid primary 4096x4096x65 float32 cube, total 4,362,079,680 bytes,
with last-plane sentinel pixels. Used for selected plane reads, not whole-cube
loading or output. The 65-plane dimension fits existing int count limits.
Ordinary controls use the same patterns with small dimensions/counts and existing
primary/extension/mosaic and unsigned endpoint/scaling controls.

Processing harness calls existing image_loadext for each CCD, image_sub_local
with a matching uniform bias image of 16 ADU, and mef_hdrpix_dump with source
headers for primary/extension output. image_sub_local is already used for bias
subtraction in mefp_lib.c; its implementation is not changed. This is a bounded
existing numerical operation, not a full recipe/scientific validation. Output
pixels are independently expected input minus 16, verified in bounded chunks.
Process one CCD at a time, retaining detector/HDU order and existing float32
storage policy. Use the existing decoder/converter and normal library linkage.

No observational inputs. Input files are chmod read-only after generation.
Source fingerprints use size/mode/mtime and known-written regions, not full-hole
hashing. One output validation pass verifies every pixel and relevant header,
storage/scaling/order, file length and padding through Astropy/NumPy plus
independent analytic layout/pixel expectations.

## Resource bounds and execution order

Initial agent filesystem reports 53 GiB available. Run generation must check again
and stop if insufficient. First check sparse support with a temporary private
file; remove only that disposable probe. Require at least 12 GiB free before
large execution. Individual large files are about 4.063 GiB, below 8 GiB ceiling.
Sparse inputs write only headers/sentinels. Single fully materialized output is
about 4.063 GiB. Initial planned physical retained data is <8 GiB, below 32 GiB
ceiling; do not assume output sparsity. Log actual allocated blocks.

Live pixel arrays: about 64 MiB science +64 MiB uniform bias +64 MiB writer
conversion, plus legacy mapping metadata/runtime and bounded validation buffers.
Plan conservatively below 1 GiB native working set, within approved 4 GiB ceiling.
A large virtual mapping is not a 4-GiB RAM allocation. Record actual peak RSS;
unexpected excess stops dependent execution for review.

Stages: IO-1 scanner/query controls, then IO-2 read controls/M4 integration, then
IO-3 writer arithmetic and status, then IO-4 focused C90/C17 ordinary and boundary
checks, scoped sanitizers and one C90 multi-GiB processed output. Finally the same
private runner/fixtures on Mac then representative Chapman (IO-5), one large
C90 output per host; C17 large-offset reads/ordinary processing only. No
implementation is called target-qualified until those returned receipts pass.

Read controls cover late headers/pixels beyond 2/4 GiB, map/copy/window reads and
last cube plane. Writer controls cover wide padding, error return on a private
unwritable/full sink where supported, and exact large output. Malformed/truncated/
overflow controls fail before invalid access. Old narrow queries test atomic
outputs on failure and representable requested values on otherwise-large files.

No general benchmark, dependency/tool requalification, production installation,
original-data write or repeated unrelated suites. All source/check changes stay
within the approved inventory; any additional production file/interface requires
an amendment first. Small focused test artifacts retain their logs; the actual
large run retains its single output and bounded validation receipt.
