# M1 file/list inputs into resolved operation requests

Owner instruction: proceed after accepted/merged PR #142 and confirmed clean
Mac/shared Chapman main 12f555ce4e14df0e292b629d54a3e496b94d8269.

## Implementation

The internal C90 mef_input_request.h/.c adapter adds mef_request_from_input.
It accepts an explicitly declared single-file or legacy-list input, an absolute
input path, an explicit absolute list-member base and a caller-supplied selected
image catalogue. It fills an owned resolved request through the accepted
mef_request_create_resolved builder. The caller supplies the operation,
calibration roles, per-detector BPM choices and output/work/log locations.
Its initial input array must be NULL/count zero, avoiding competing membership
definitions. No role or operation is inferred from names or list labels.

For lists it reuses Eclipse charmatrix_read, the parser inside framelist_load;
it does not implement another list tokenizer or modify the original reader.
The old framelist_load/is_ascii_list validate relative filenames against cwd.
The new adapter instead joins relative first-column entries to the supplied
original execution base. That base is not inferred from the list's directory
or the current process directory. Direct files are never retried as lists and
lists are never retried as FITS files after an error.

Rows and duplicate members retain their order. Each member expands in the
catalogue's explicit within-file detector order. The catalogue supplies real
asset IDs, detector IDs and HDU index/name/version selectors; the adapter does
not fabricate them. Duplicate detector or HDU mappings within one file are
rejected as ambiguous. Unknown listed paths fail. Primary HDU 0 remains an
explicit reference, not a translation of legacy xtnum=0. The caller/inventory
must select the intended detectors before this adapter is called; generic
FITS layout discovery remains M4 work.

Paths match the catalogue lexically after joining. No realpath, symlink
canonicalization, dot-component normalization, recursive search or new identity
policy is introduced. Relative '..' is not silently collapsed across symlinks.
Aliases require an explicit catalogue location. General path/alias handling
remains M3; this bounded explicit-base boundary does not replace that milestone.

Legacy syntax remains whitespace-delimited first-column filenames; additional
columns are not interpreted as association policy. Comments at column zero and
blank rows use the unchanged parser behavior. Quoted filenames containing
spaces are not newly supported in legacy lists. Spaces in containing paths and
direct single filenames are supported. The bounded adapter rejects NUL bytes
and rows with 1023 or more non-newline bytes before calling the legacy
ASCIILINESZ=1024 parser; no historical parser behavior is changed outside it.

## File access and BPM behavior

The adapter checks that the supplied file/list, each selected member and every
selected calibration is a readable regular file. It follows filesystem links
for that access check; missing/broken/nonregular selections fail. It opens and
closes data/calibration files without reading their headers or pixel arrays.
List text is read by the parser. A readable non-FITS file is not thereby
validated as an image: format, dimensions, detector/HDU applicability, units
and mask conventions remain the later FITS/service boundary's responsibility.

Explicit BPM omission produces no BPM lookup, guessed default, link or map.
A selected BPM needs the accepted consistent descriptor and a readable file;
a missing selected BPM fails without a partial request or fallback. The same
access rule applies to other selected calibrations. Selected is not applied,
and readable is not scientifically valid. Generated validity/rejection flags
and required M6a variance processing are unchanged and not implemented here.

Only the new opt-in probe library uses this adapter. The production recipe,
old loader, PAF defaults, automatic engine BPM discovery, notebook wrappers and
installed selection are unchanged. The raw CLI capture is not yet automatically
split/routed into these requests. No new CLI flags, TOML/ASDF schema, calibration
association, variance algorithm or QC estimator is introduced.

## Ownership, errors and concurrency limits

The input specification/catalogue is borrowed for the call. Expansion arrays
are temporary; returned requests deep-copy descriptors, strings, roles and BPM
choices. A pending request transfers only after all access checks succeed.
One cleanup section releases partial request and adapter/parser owners.
Occupied output/error pointers remain unchanged; status is authoritative if an
optional diagnostic cannot allocate. Errors identify the failed path when
reporting memory is available.

The per-object allocator covers new adapter/request/diagnostic memory. Existing
Eclipse parser allocations still use its established allocator and are not
included in injected-failure owner counts. No dependency allocator policy or
global hooks are changed. Eclipse tokenizer/allocator globals are unchanged;
this does not establish thread safety or safely concurrent calls in one process.
No chdir, environment mutation, shell, output file or project publication occurs.

Inputs and caller catalogue must remain stable for the duration of the call.
Access checking and the existing two-pass parser are not a filesystem snapshot
or a lock against concurrent replacement. Project-level input locking and
identity validation remain the planner/I/O contracts; this adapter does not
claim atomic inventory or verify byte identity from an asset ID string.

## Tests actually run

Agent Ubuntu/GCC 13.3 strict syntax checks pass for the new C90/C17 adapter and
probe with -pedantic-errors -Wall -Wextra -Werror. Existing dependency compile
warnings are retained; no warning-free whole-native claim is made.

The new native_input_request test creates tiny synthetic FITS files and text
lists, then runs seventeen cases from each of two unrelated working directories.
It calls actual framelist_load in its original base as an independent ordering
reference and compares new expansion against it, including reverse catalogue
detector order, a primary-HDU file and duplicate list rows. It covers selected
and omitted BPM, a direct filename containing spaces, missing selected BPM and
member, empty/oversized/NUL/quoted-space lists, directories, absent base, unknown
or ambiguous catalogue, explicit kind without fallback and contradictory BPM.

All seventeen cases pass in agent C90, C17 and C90 ASan/UBSan. ASAN_OPTIONS is
detect_leaks=0 and UBSAN_OPTIONS is halt_on_error=1; LeakSanitizer and whole-engine
memory acceptance are not claimed. Allocation controls cover 34 successful
omitted-BPM and 40 selected-BPM positions in transient/persistent modes, twenty
cycles each, plus all 43 positions of a missing-selected-BPM failure path.
Tracked new owners return to zero. The latter failure remains IO or memory
failure if construction fails earlier, never a partial success.

The adapter checks cwd unchanged inside the C probe; the Python driver checks
its own cwd, fixture byte hashes (including synthetic FITS bytes) and source
hashes. Identical request/error output from two unrelated directories is
required. Legacy whitespace syntax remains deliberate; quoted-space failure is
a limitation control, not support for quoting. No real astronomical inputs,
image arithmetic, numerical engine, notebook or installation ran.

## Delivery and next gate

CMake adds the opt-in input_request_probe target and native_input_request CTest
beside the accepted configuration/runtime/CLI tests. It links the same Eclipse
parser library, without changing its sources or adding a new dependency.
Agent evidence under docs/developer/fixtures/m1-inputs-agent-2026-10-29 records
source/probe identities, compiler commands, reports and selected logs. The
agent used the existing recorded manual probe build; actual selected-tool
Mac/representative Chapman CMake checks remain pending. No target sanitizer
or completed general path/layout/numerical processing qualification is claimed.

Next: private target configure/build and the four focused tests using the
existing selected tools. Then owner review and the first concrete numerical
service through the common template. Numerical extraction still needs its own
bounded equivalence and failure gate; M1 is not complete. Preserve all prior
evidence and installations; no repeat tool qualification or duplicate Chapman
host run is needed. This increment authorizes no automatic merge/cleanup.
