# Large FITS/MEF image I/O roadmap — version 1.0

Date: 1 November 2026. Status: **APPROVED by owner after review of commit 6f5026583edf3ee7e82a13aa896b2fb4bceda99c**.
Baseline: main `38b27f8da943acfdd83b9f1cc9a243405e346a96`.
Tracking: #195; proposal PR #200. This roadmap precedes M5.

## 1. Objective and authority

Read a large FITS/MEF, process ordinary-sized CCD planes with existing numerical
routines, and write a valid large processed FITS/MEF. File position must no longer
be limited to signed-int bytes. This is an image I/O change, not a general
conversion of mefpp/Eclipse to 64-bit numerical types.

The owner's complete I/O clarification supersedes the earlier read-only scope.
The original broad audit and subsequent read-only inventory remain historical
evidence. Owner approval is recorded in the IO-0 frozen plan. Execute its stages and gates in order. Do not add
capabilities, omit gates, relax limits or expand a test campaign silently.

Every implementation commit references #195 and the approved roadmap version.
Record stage completion, actual source revision, checks, limitations and retained
evidence. Approval to implement does not authorize merge, installation or switching
the production engine. Original observations must never be modified.

## 2. Capability and type contract

| Quantity | Required treatment |
|---|---|
| File positions and on-disk byte spans | Signed off_t, verified at least 64 bits by the existing build contract |
| Allocation, mapped/addressable spans and transfer counts | size_t, with explicit sign/range conversions from off_t |
| Seek/tell operations | fseeko/ftello where a file position is needed; check status before use |
| HDU/detector/plane ordinals and bounded counts | Existing int interfaces and established limits |
| Dimensions and per-plane numerical indices | Existing types; validate supported range before products |
| Pixel values, precision, BSCALE/BZERO and mathematical algorithms | Unchanged |

Do not assume that a cast after a calculation fixes overflow. Check multiply,
addition, block rounding and signed/unsigned conversions before evaluation or use.
Never cast int* to off_t*. Audit allocation/copy sizeof expressions, pointer
differences and diagnostic formats when associated values change.

A signed 64-bit file position represents up to 2^63-1 bytes; this is a type
ceiling, not a qualified operational file-size claim. Initial qualification
establishes successful cases beyond both 2 and 4 GiB, under the existing supported
image shapes, HDU counts, filesystem and address-space limits. State exact tested
sizes in the acceptance report, not an invented universal maximum.

## 3. Explicit exclusions

- No widening of all image indices, pixel integers, dimensions or Eclipse types.
- No arbitrary huge single-plane, heap/random-group or table-payload support.
- No standalone qfits utility modernization; #198/#199 remain separate.
- No new FITS parser, FITS library replacement, format/backend or dependency.
- No M5 subroutine extraction, parallelism, Python binding or numerical changes.
- No new instrument/scientific policy, calibration association or full science audit.
- No new allocator policy, global cache redesign or output publication architecture.
- No change to existing HDU-count/header budgets merely to enable large bytes.
- No raw repair, installed replacement, tool upgrade or duplicate Chapman environments.

Headers may need traversing across a file containing other HDUs, but the increment
does not promise reading unsupported table data. Preserve current supported-format
boundaries; reject cases that cannot be safely traversed rather than guess lengths.

## 4. Bounded file inventory

Fourteen existing production/header/build files are in scope. Only relevant I/O
portions of mixed read/write files may change.

| File, relative to repository | Responsibility |
|---|---|
| mefpp2/qfits5/src/cache.c | Wide cached sizes/positions and scanner arithmetic; bounds; ordinary stack/growth behavior |
| mefpp2/qfits5/src/cache.h | Wide internal query declarations and checked legacy contract |
| mefpp2/qfits5/src/simple.c | Wide segment queries; header keyword readers; safe narrow wrappers and query-result checks |
| mefpp2/qfits5/src/simple.h | Matching wide public read declarations |
| mefpp2/qfits5/src/pixio.c | Loader positions, plane/window arithmetic, seeks; pixel transfer/allocation byte counts and write status |
| mefpp2/qfits5/src/pixio.h | Loader file-position/span fields and documentation; preserve pixel/count interfaces |
| mefpp2/qfits5/src/fits_rw.c | Header-read spans/pointer bounds and wide whole-file padding arithmetic |
| mefpp2/qfits5/include/qfits.h | Coherent installed API/loader declarations and associated examples |
| mefpp2/qfits5/src/xmemory.c | Checked stat/offset/size conversions and mapped read/release bounds; allocator policy unchanged |
| mefpp2/src/iproc/cube_save.c | Validate retained pixel-count range before lx*ly at the writer call boundary |
| mefpp2/ins/mef/common/mefp_lib.c | Existing image/MEF writer size accounting, pixel-count checks and padding; no mef_split migration |
| mefpp2/ins/mef/common/mef_layout.c | Consume wide segments; replace whole-file INT_MAX refusal after complete read integration |
| mefpp2/ins/mef/common/mef_layout.h | Supported I/O/read range and retained plane/count constraints |
| mefpp2/CMakeLists.txt | Seek/tell declarations/build checks and focused test wiring |

Eclipse image_io/cube_load and mef_load_ext are rebuilt against the loader, without
numerical restructuring. Keep cube_info.headersize and the dormant Eclipse
filesize helper unchanged; bounded primary-header lengths can use safe narrow
queries. Keep qfits table structs/APIs and standalone utilities unchanged.

Expected verification changes: existing tests/qfits_discovery_probe.c and
tests/qfits_discovery_contract.py; add at most three focused files under
mefpp2/tests: large_file_io_probe.c, large_file_io_contract.py (including synthetic
fixture generation), and qualify_large_file_io.py (private target runner).
Existing tiny native-path comparison code may be reused without changing its
oracle. If another production file or changed public interface proves necessary,
record why and obtain a roadmap amendment before modifying it.

Documentation updates and stage receipts are allowed in AGENTS.md,
docs/developer/agent-instructions.md, docs/developer/roadmap.md, this roadmap,
the audit and linked evidence directories. They add no runtime capability.

## 5. Ordered stages and exit gates

### IO-0 — freeze interfaces, fixtures and resource plan

Deliver the concrete wide query signatures, loader-field changes and test plan
before source edits. Proposed additive names: qfits_get_hdrinfo_wide and
qfits_get_datinfo_wide, status int with off_t* outputs. Back them with one wide
existing scanner/query implementation; do not create a second reader.

Keep old int APIs with checked conversions. Only requested outputs must fit;
validate all requested values before assigning outputs. Extension counts remain
int. Changing the two loader segment fields changes struct layout: coherently
rebuild all linked clients and update both header copies. Do not claim old binary
ABI compatibility or mix old installed headers/libraries with new private objects.

Specify fixture header/layout bytes, expected positions and pixel/scaling oracle
independently of the changed implementation. Use current supported counts/shapes.
Select one existing processing path, normally bias subtraction, for the >4-GiB
end-to-end case; do not introduce a new reduction operation.

Before large execution, emit exact logical sizes, expected physical disk use,
output inventory, plane memory estimates and commands. Resource ceilings:
individual fixture/output logical size at most 8 GiB, planned peak retained
physical disk at most 32 GiB, and planned native working memory at most 4 GiB.
These are test budgets, not claimed library limits. Inputs may be sparse; do not
assume output files will be sparse. Check available space and sparse support.
If a valid existing operation/configuration cannot fit these budgets, stop and
propose the exact amendment; do not silently substitute metadata-only acceptance.

Exit: signatures, file boundaries, one processing operation, fixture oracles and
bounded resource plan are written and consistent with the approved roadmap.

### IO-1 — wide discovery and compatibility boundary

Widen cached file positions/spans, local scanner block/data-byte arithmetic and
buffer allocations/copies coherently. Retain regular-file checks, bounds, budgets,
pending-cache publication on success and actual-count storage growth. Replace
the scanner's blanket whole-file INT_MAX refusal only with checked wide traversal.

Old int queries return failure for an unrepresentable requested result, without
truncation or partially published results. A small requested primary header length
can still succeed for a large file. Keep int status/count meaning separate from
byte-position results.

Exit: exact ordinary offsets unchanged; independently known positions beyond 2
and 4 GiB succeed through wide APIs; narrow compatibility and malformed/overflow
controls succeed. This alone does not establish pixel or processing support.

### IO-2 — header and pixel reads

Migrate header/key readers and loader init/read/window paths to wide positions.
Check plane multiplication, start+length and window strides before use. Convert
to memory sizes only after checking representability and file bounds. Keep
existing per-plane pixel/count/byte limits explicit. Use the existing decoder;
do not add full-plane copies or per-pixel position checks.

Integrate the M4 layout consumer and update its capability statement. Retain
source-identity checks, detector identity/order, selected maps and count budgets.

Exit: known late-header values and exact recognizable pixels load through mapped,
copied and supported window paths; a late cube plane is positioned correctly;
ordinary scaling/unsigned endpoints agree; invalid spans fail before access.

### IO-3 — processed output I/O

Keep numerical computation unchanged. Correct byte-count arithmetic before
conversion allocations and fwrite, retain representable pixel-count bounds, use
size_t transfer counts and check write/flush/close results at changed boundaries.
Do not widen qfitsdumper.npix merely to support aggregate MEF size.

Compute total output size and FITS padding from wide quantities. Preserve existing
header order, HDU order, storage precision and scaling policy. Validate expected
size with overflow-safe arithmetic. Existing void padding APIs need not become
a new publication framework; callers must not report a verified complete output
when required bytes/padding were not written. Preserve existing partial-output
handling; no new atomic publication design is implied.

Exit: output crosses 2 and 4 GiB correctly, each HDU is readable with correct
position/length/padding, and changed I/O boundaries do not report truncated writes
as success. Write controls use only private scratch outputs.

### IO-4 — focused agent integration qualification

| Control | Required evidence |
|---|---|
| Ordinary primary, one-extension and mosaic inputs | Unchanged exact decoded pixels, scaling, headers/order using existing independent tiny reference comparisons |
| Valid sparse late HDUs beyond 2 and 4 GiB | Correct known header/data offsets and exact late-detector pixel reads |
| Late cube plane | Correct plane start with ordinary plane size |
| Mapped/copied/window reads | Correct bytes and selected region; existing supported mode restrictions retained |
| Narrow API boundaries | Success for representable requested values and deterministic refusal otherwise |
| Invalid/overflow/truncated spans | Controlled failure before invalid allocation, seek or pointer access |
| Output position/padding and short-write control | Correct wide totals and no false completion at changed boundaries |
| Existing-operation large MEF case | Process ordinary CCD planes and produce one processed MEF >4 GiB; independently verify every plane's expected pixels and relevant headers/scaling/order |

The final case must exercise production I/O and an existing numerical path.
A dedicated harness can call existing services/helpers without modifying the
monolithic recipe or creating a new workflow. Record actual routines called.
A new writer probe alone or header-only success is not a substitute.

Use an existing independent FITS reader and analytic expected results. Compare
large output pixels in bounded chunks in a single validation pass; do not allocate
the entire MEF or redundantly hash it. Preserve sparse-input size/mode/timestamp
and deliberately written regions without hashing gigabytes of holes.

Compile optimized C90 and C17 with selected tools. Run focused sanitizer controls
on changed arithmetic/mapping/I/O paths; large end-to-end execution need not be
duplicated under sanitizers. Inspect casts, implicit narrowing, sizeof expressions,
format strings and diagnostic-only branches. Keep all failed and corrected logs.
Reuse unaffected evidence; do not replay BPM/configuration/old full matrices.

Exit: focused C90/C17 and scoped sanitizer evidence, exact ordinary results and
the real >4-GiB processed-output comparison all pass within declared budgets.

### IO-5 — actual Mac, then representative Chapman

Use the same qualified source, runner/fixtures/oracles and the canonical
selected-tools.md paths. Fresh private source exports/builds/output directories;
nice >=10, two build jobs, one numerical thread. Verify actual checkout/environment
guards without rediscovering already selected tools or duplicating Chapman3/4.

On each target, compile C90/C17, run the focused I/O controls, and execute the large
end-to-end processing case once with the C90 executable. C17 uses focused controls
and the ordinary exact-processing comparison; do not repeat the multi-GiB output
merely for language mode. No original observations or installed programs used
as writable targets; keep user main clean.

Exit: returned Mac/Chapman receipts identify source/tools, exact tested sizes,
mode-specific checks, output comparison and preserved checkout/installation/input
state. Source changes after qualification require affected checks, not automatic
replay of every unaffected lane.

### IO-6 — acceptance, integration and M5 resumption

Prepare one implementation PR/closure report mapping each stage to actual evidence.
No stage closes on a written/unexecuted test. Record supported file positions,
remaining per-plane/count/addressability limits, ABI rebuild requirement and any
unresolved findings. Do not claim exabyte qualification from the type ceiling.

After owner acceptance and explicit merge/cleanup instruction, integrate and give
guarded Mac then Chapman synchronization/cleanup. Installation/engine activation
requires its applicable authorization and is not part of source synchronization.
Close #195 only when agreed implementation/target acceptance criteria are met.
Then resume M5 calibration subroutine decomposition.

## 6. Performance and change control

No numerical algorithm, compiler-optimization change, new pass over image data,
new full-plane copy or unconditional heap-offset allocation is authorized.
Retain the corrected ordinary-file stack fast path. Wide cached entries consume
more metadata bytes; this is an explicit small structural cost, not a claim of
identical memory use.

No reproducible processing slowdown is permitted and no automatic percentage
allowance is introduced. Capture duration, peak RSS and I/O-volume evidence for
the bounded large run; this is qualification context, not a statistical speed
claim. Reuse prior unaffected performance evidence. If changed-path inspection
or results indicate extra copying/scanning or a reproducible slowdown, stop,
report it and agree a focused measurement/correction plan before further runs.
Do not start another general benchmark campaign by default.

Scope amendments require an explicit owner decision before dependent work.
An amendment identifies requested version change, reason, additional files,
capabilities, resources/tests and impact on existing evidence. Unexpected failures
stop the affected stage; record them and propose correction within the approved
boundary. No silent gate waiver, capability substitution or opportunistic cleanup.

The final success criterion is usable large image I/O with unchanged numerical
behavior, qualified beyond 4 GiB on both target environments. It is not a general
64-bit rewrite of Eclipse/mefpp.
