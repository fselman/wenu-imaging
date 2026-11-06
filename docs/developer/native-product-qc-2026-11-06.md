# Native product QC — 6 November 2026

## Executive summary

The new native writer prepares one ASDF for one final MEF product without
Pycavi. It records supplied QC values, embeds each raw-input record once, and
retains detector-specific participation and HDU mappings. It does not change
bias arithmetic or process images. Agent structural checks pass; actual
libasdf writing and independent Python readback remain pending on the Mac.
Final MEF assembly and connection to the standalone recipe are still pending.

## Earlier decisions retained

The controlling design is [bias MEF/native ASDF](design/bias-mef-native-asdf-v1.md).
Final products remain MEFs. Detector separation is temporary, with a coordination
boundary before assembly. Invoke the recipe in orchestration, read untouched raw
data, and write FITS/ASDF/logs to the explicitly selected products directory.
Keep mutually exclusive `--output-dir` and complete `--output`; the latter retains
its basename and supplies the parent directory. Generated names share one recipe
start timestamp and a product sequence. ASDF replaces the final `.fits` suffix.
Whole-mosaic real-data acceptance precedes Bias viewer work. Plots are generated
once separately and displayed with coordinate information.

The preceding path-helper increment passed 11 checks on the actual Mac in
1.693 seconds using an explicit Xcode SDK. The earlier failed build directory
was preserved. That result does not qualify this new writer.

## Concrete container

Application schema **2.0.0** differs from file standard **ASDF 1.6.0**. The
application version changes because inputs now use embedded record IDs rather
than separate QC sidecars. Existing 1.1 records and completed diagnostics are
not modified or migrated. The logical measurement fields remain explicit:
name, value, unit, status/reason, stage, method, region, sample count and sources.

| Section under `qc` | Contents |
| --- | --- |
| `file` | Final FITS identity, basename, location and optional supplied digest |
| `record` | Application schema, assessment identity and recipe-start time |
| `provenance` | Producer/revision, recipe, start time, sequence, log and exact configuration snapshot |
| `characterization.detectors` | Product QC, detector identity, configuration slot and output HDU |
| `inputs` | Original list ordering, internal record links and use/rejection per detector |
| `embedded_input_records` | Each raw input once, with original index, source HDUs and detector QC |
| `calibrations` | Calibration/BPM references and explicit detector-to-source-HDU bindings |
| `extensions` | Product scope and input-reference/measurement policies |

The configuration snapshot is the exact existing `mef_config_dump` typed-bits
JSON text embedded inside ASDF. This avoids a second native configuration parser
and creates no JSON handoff file. Calibration QC locations may be absent; the
writer does not copy or traverse their ancestry. An applied BPM must reference a
known BPM calibration bound to that detector. Unavailable/invalid measurements
have null values and a reason, rather than fabricated numbers. Counts serialize
as integers; supplied double values and profiles serialize without QC computation.

## Implementation boundary

`mef_product_qc.h` exposes borrowed C descriptors. The validator checks identities,
ordering, coverage, references, measurement states and finite values. The external
libasdf writer constructs detached mappings and attaches each once, retaining the
qualified workaround for #219. Optional Float16 is unused; no dependency is
installed or modified. There is no Pycavi import, subprocess or Python final writer.

The writer requires a nonempty regular final FITS at the supplied path, but does
not parse its HDUs or pixels. The recipe caller must validate the actual MEF and
supply accurate provenance/QC. Digests are supplied by the caller or explicitly
marked unverified; the writer computes none. A metadata descriptor is not proof
that the referenced image has the claimed scientific contents.

ASDF is written to a private sibling, checked for file standard 1.6.0, reopened
with libasdf, and checked for schema/product identity and detector/input counts.
Exclusive hard-link publication refuses an existing destination, including a
dangling symlink. The private file is removed afterward. Failure preserves the
final FITS. This is exclusive publication, not a multi-file transaction or a
power-loss durability guarantee. The recipe must report success only after FITS,
ASDF and log completion. No recipe/CMake entry is activated by this increment.

## Verification and limits

Before execution, each test group is described below and in the driver comments:

1. Strict C17 build and execution of the actual C validator: three valid metadata
   cases and 22 refusal cases, grouped into two unittest tests. Inputs are invented
   descriptors; expected results are acceptance/refusal with a diagnostic. No
   astronomical data, image calculation or Pycavi method is exercised.
2. Compile-only inspection of the actual writer against the public libasdf 0.3.0
   headers pinned at `2c9f26c1515128485e1d688ce5410f00a87243a5`. A minimal generated
   configuration header is used for syntax inspection only. This does not link
   or execute libasdf and is not native-ASDF runtime qualification.
3. Pending Mac gate: compile/link the actual writer against the retained qualified
   prefix, then run eight publication/readback tests plus the two validator tests.
   Tiny byte sentinels stand for final/raw/BPM files; they are deliberately not
   valid FITS images. Python ASDF independently validates the new schema, exact
   supplied values (including signed zero), embedded references and detector/HDU
   mappings. Other controls check integer counts, BPM context, invalid metadata,
   overwrite/dangling-link refusal, basename inheritance, missing FITS and temporary
   cleanup. Only these tiny sentinels are fingerprinted for preservation.

Agent results: two structural tests passed, covering all 25 metadata cases;
strict C17 writer syntax inspection passed. No actual ASDF file was produced in
the agent environment. The Mac tests are written but unexecuted. The retained
library, Python environment and main checkout are to be preserved; no installation,
old qualification replay, real-data reduction, viewer change, merge or cleanup.

Remaining work under #245: actual native-ASDF target acceptance, reviewed final
MEF assembly, standalone recipe integration, then a full-mosaic real bias run
from orchestration into the selected products directory and owner inspection.

## Actual Mac finding and checker correction — #249

The first actual Mac gate at `cee1ee38d30bf322c1af64d4f3c554ba9c747dc8`
compiled and linked the real writer against the retained libasdf. Seven of ten
tests passed in a 4.905-second run. All three positive publication cases completed
the C write/readback steps, then failed in Python schema validation before the
exact-value assertions. The error was `RefResolutionError` for the application's
canonical schema ID, `asdf://wenu-imaging/schemas/product-qc-2.0.0`.

Supplying the schema file URI alone was insufficient: internal references resolve
against its canonical ID. The corrected verifier registers the unchanged local
schema bytes under that ID within an `asdf.config_context()`, using ASDF6's public
`add_resource_mapping` API. No schema download or installed-runtime change is
needed. Schema content, C writer, C validator, probe and numerical code are unchanged.

Preserve `/Users/fselman/Software/build/wenu-imaging/mac-native-product-qc-4wToOOTg`
including its original `source`, `checks.log` and result JSON. The test driver now
accepts `--reuse-probe` and `--verifier` so a new checks directory can exercise the
original binary/source with only the corrected checker. Its result explicitly
records whether compilation occurred and the reused executable path. Retry
controls and expected values are unchanged; full target acceptance is still pending.

Agent verification for this correction is limited to Python syntax and execution
of the changed reuse path with the previously compiled structural-validator probe.
That path must run the two structural tests, create no new executable, and record
`compiled_now=false`. This does not exercise ASDF lookup or its corrected runtime
behavior. #249 stays open until the retained Mac runtime passes all ten controls.
