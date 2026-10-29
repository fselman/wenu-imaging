# M1 first implementation: owned configuration snapshot

29 October 2026. Owner authorized implementation after the retained effective
input map, with explicit emphasis on programming practices. This increment
implements the configuration boundary before extracting numerical subroutines.
It does not complete M1 or replace the accepted operation template.

## Boundary and ownership

`mefpp2/ins/mef/common/mef_config.h` exposes an opaque, internally owned
`mef_config` and status-returning constructor/dump functions. The adapter copies
only the constructor-mapped fields from `mef_bb`: 137 global getter entries and
14 entries per detector. Small arrays and actual legacy numeric types are
preserved; 109 strings and the detector array are independently owned. Runtime
FITS-derived CCD fields, loaded images/cubes, mutable traversal state, request
bindings and save flags are excluded. No whole-`mef_bb` copy is made.

The source is borrowed only during construction and may be destroyed immediately
after success. The caller initializes the output to NULL; occupied outputs are
rejected without replacement. Every partial construction follows one cleanup
path. Destruction accepts NULL. Numeric values are copied from stored legacy
values, including the five double fields historically narrowed through a float
temporary; this adapter never reparses their original decimal strings.

The optional allocator has per-object callbacks and user data; there is no
mutable global allocator or failure hook. Its callbacks and user data must remain
valid until destruction. Default allocation uses the C library directly,
explicitly bypassing Eclipse's function-like allocation macros. The legacy
allocation system is unchanged. Snapshot diagnostics are optional borrowed static
strings, so reporting an allocation failure needs no further allocation. They
are internal adapter diagnostics, not an implementation of the future operation
error-object/result API in the M0 sketch.

The internal field catalog drives member copying, string cleanup and global
dump entries. Detector settings have a separate typed record. This is an
incremental private representation, not the final TOML subset schema or an
installed public ABI. Later extraction can split its internals without exposing
the legacy work object to numerical routines.

## Inspection and build isolation

The deterministic JSON inspection dump uses PAF keys, explicit C types, integer
and string values, and canonical big-endian hexadecimal object bits for float32
and float64. It preserves signed zero and avoids locale-dependent decimal
rounding. Unsupported floating representations return a status. Strings retain
their UTF-8 bytes and JSON control/quote/backslash escaping. This is a testing
and inspection format, not the WAD/ASDF persistence contract.

`MEFPP_BUILD_CONFIG_PROBES` defaults to **OFF**. When explicitly enabled, CMake
builds a separate static snapshot library and `config_paf_snapshot`, which calls
the real PAF constructor, makes the snapshot, destroys the legacy object and
dumps the surviving settings. It does not call the mefpp recipe or read FITS.
Use a new output directory: the probe's output pathname is caller supplied and
is opened for writing. The test runner always creates a fresh private directory.
The new library is not linked into `mefpp` and is not installed. The `.def`
catalog is included in native source provenance.

With `BUILD_TESTING=ON`, the opt-in `native_config_snapshot` CTest runs the
synthetic ownership tests and the actual PAF-constructor comparison. Build its
probe target first and select only that CTest for this increment. The Python
runner also accepts an explicit compiler, SDK root and C90/C17 mode, so direct
header/snapshot tests do not require upgrading Chapman's system CMake.

## Checks and remaining work

Agent Ubuntu x86_64 / GCC 13.3 checks passed: strict C90 and C17 snapshot units;
585 OCAM and 249 WFI exact mapped values; an additional 249-field text/signed-zero
fixture; all 111 allocation positions rejected cleanly per fixture; twenty
copy/destruction cycles per fixture; occupied/invalid outputs; missing configured
strings/detector array; source destruction before dump; and stream write errors.
The unchanged actual PAF constructor also produced matching OCAM/WFI snapshots
in a private C90 link with unused legacy sections discarded.

ASan/UBSan passed for the C90 synthetic snapshot tests. LeakSanitizer cannot
inspect `/proc` in this container and failed before reporting a leak result;
the retained successful sanitizer run explicitly used `detect_leaks=0`.
Per-object allocation accounting returned to zero at every checked boundary.
The separate actual-PAF probe was not sanitizer-instrumented. Retained source
identity checks matched all 127 fetched upstream input blobs.

The returned Intel Mac and Chapman C90 CMake configure/probe builds and focused
CTest now pass; see the [paired receipt](../../../developer/m1-config-paired-results-2026-10-29.md).
These are owner-returned terminal results, not independently inspected target
archives. They qualify this opt-in configuration increment, not the full engine.
Target C17/sanitizer runs and remaining M1 lifecycle work are not claimed. No installation,
notebook change, native recipe execution, calibration recalculation, pixel
comparison, scientific acceptance or QC estimator is part of this increment.
Request/context/result/error lifecycles, effective CLI override capture and
numerical service extraction remain subsequent M1 work. PAF remains active;
TOML parsing is still M2. Owner-selected `mef_cal_*`, `mef_sci_pp` names and the
explicit later qc phase remain as recorded in the neighboring template.
