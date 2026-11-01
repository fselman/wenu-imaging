# Large image I/O: agent IO-0–IO-4 receipt and IO-5 handoff

Owner approved [roadmap v1.0](large-file-image-io-roadmap-v1.md) after reviewing
6f502658. Approval and frozen IO-0 plan were recorded at 158ec8d8 before C edits.
Implementation follows the fourteen production/header/build files and three new
test/runner files. No scope amendment, numerical rewrite or additional FITS reader.

## Implemented boundary

The existing shared qfits scanner/cache now stores off_t disk positions/spans.
Additive status-returning wide segment queries feed header/keyword readers,
pixel loading and M4. Old int queries check only requested outputs, fail rather
than narrow and leave outputs intact on failure. Only two loader span fields
change type; both header copies agree and clients must rebuild.

Checked loader plane/window/seek/mapping arithmetic retains ordinary per-plane
limits. Whole-file size can exceed 2/4 GiB without widening detector ordinals,
dimensions or numerical arrays. The copied-window converter used a full-plane
count for its smaller buffer; #201 corrects that in the approved read boundary.

Writer byte counts, source pixel-count products and cumulative file/padding
arithmetic are checked. Changed write/flush/close boundaries report failure.
Existing image_sub_local and mathematical/scaling code remain unchanged.
mef_split, table structs/data APIs and standalone utilities stay outside scope.

## Agent checks actually performed

| Check | Result |
|---|---|
| C90 discovery and ordinary contracts | Four focused contracts passed in 24.52 s |
| C17 same contracts | Four passed in 24.06 s |
| Final invalid-plane/64-bit overflow/known-region controls | Affected focused suite rerun and passed C90/C17 |
| Scoped C90 ASan/UBSan | Large-file focused and discovery contracts passed 2/2, 8.25 s |
| Large C90 existing-operation case | Passed: 65 CCDs, 4,362,324,480-byte input and processed output |

Four contracts are native_large_file_io, native_qfits_discovery, native_layout
and native_explicit_paths. The last preserves existing tiny OmegaCAM/WFI exact
product comparisons. No prior BPM/configuration/full matrix was replayed. Changed C translation units
also parsed with -Wconversion/-Wsign-conversion/-Wformat=2. The retained log
includes reviewed nonnegative disk-to-memory conversions and bounded padding
remainders; legacy numerical packing warnings remain. This is not a warning-free
or broad numerical-cleanup claim.

Sanitizers cover changed discovery/read/window/write controls, not a second
multi-GiB processing run. Leak detection was disabled for the documented legacy
cache limitation; no leak-free claim is made. After the four-contract suites,
the negative/mutated plane guard was added and its affected focused controls
rerun in both modes. Later production edits were comments only; the test free-space
reserve was aligned to 12 GiB before large execution and 512 MiB for focused sparse
controls. Target runner has syntax/source checks, not actual target execution.

An initial private probe build stopped because the existing opt-in CMake probe
flag had not been enabled. Its log is retained; reconfiguration enabled the
existing flag, without a source correction. A report-writing helper initially
used a Python without Astropy and failed before creating evidence; it was rerun
with the existing private qualification interpreter. Neither was a native failure.

## Large-case evidence

Retained agent run:
`/workspace/scratch/104db3d59fe9/io-evidence-c90/large-file-io-pxzh3wyc`.

Private sparse input: 65 float32 4096x4096 image extensions, known sentinel values,
zero-valued unwritten regions and stable extension identity/order. A separate
65-plane cube checks a late plane. Both files are >4 GiB and made read-only.

Processing uses production image_loadext, unchanged image_sub_local with uniform
16-ADU bias, then mef_hdrpix_dump, one detector at a time. The processed output
is fully materialized: logical 4,362,324,480 bytes; allocated 4,362,330,112 bytes.
It is not a metadata-only or sparse-output shortcut. No original observations.

Independent Astropy framing and analytic chunked NumPy comparisons checked
**all 1,090,519,040 large-output pixels**, all relevant headers/scaling/order/HDU
positions and zero padding; 48 tiny-output pixels were also checked. Output was
validated once rather than redundantly hashed. Input size/mode/mtime and known
written headers/sentinel regions are preserved without hashing sparse holes.

Native large-processing call: 32.3333 s. Maximum peak RSS across native child calls:
136,294,400 bytes (about 130 MiB). This is qualification context, not a matched
performance comparison or general speed/memory claim. Planned resource ceilings
were respected. Full output, original attempts and evidence remain retained.

Source identities, exact logs, failed setup log and full large receipt:
[agent fixture receipt](fixtures/agent-large-image-io-2026-10-31/receipt.json).

## IO-5 next, IO-6 still pending

Use qualify_large_file_io.py on the actual Intel Mac, then representative Chapman4.
It preserves clean main 38b27f8, installed module/engine/configuration and the
exported source. It pins itself to the exact fetched candidate, uses selected
tool invocation paths, isolated builds, nice >=10, two build jobs and one
numerical thread. It does not install or open observational data.

C90/C17 each build and run the four focused contracts. C90 additionally creates
and independently validates one >4-GiB processed MEF. C17 does not repeat that
multi-GiB output. Need at least 12 GiB free before the large case; actual retained
output is about 4.063 GiB and sparse inputs consume little physical space.

Actual target results are pending. #195/#201 stay open. No target sanitizer,
scientific/full-recipe, exabyte, giant-plane, table, standalone-tool or general
no-performance-penalty acceptance follows from these agent checks. No merge,
installation or M5 advance is authorized until the approved gates and owner
integration decision are satisfied.
