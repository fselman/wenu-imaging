# Native explicit paths — M3 candidate

30 October 2026. Refs #159, #163, #165, #166. Based on accepted PR #161,
merged main `ded31e876582dcbe044c2b99167c9d36e8c6ee03`.

The C `mefpp` executable can explicitly select input files/lists, calibration
files, PAF configuration, output directory, scratch directory and log. This
candidate uses the existing serial numerical engine directly. Python is used
only by the test driver. No caller-directory change or staged input tree is
needed by the new C path; existing invocation without these flags retains the
legacy route for comparison.

## Invocation and path rules

```bash
/path/to/candidate/mefpp \
  --pafname /configuration/selected.paf \
  --output-dir /attempt/products --work-dir /attempt/scratch \
  --list-base /observations/raw \
  --bias /calibrations/master-bias.fits --biassub \
  --bpm /calibrations/bad-pixels.fits --mff /calibrations/master-flat.fits \
  --science /lists/science.list
```

This is an interface example, not a request to run on observations or activate
an installation. Use fresh private attempt/output/scratch paths when qualifying.

| Selection | Resolution / requirement |
|---|---|
| Any of `--output-dir`, `--work-dir`, `--list-base`, `--log-file` | Activates explicit mode; requires an explicit `--pafname` and both output/work directories |
| PAF, input list, direct FITS or calibration argument | Absolute, or relative to the invocation directory; existing inputs canonicalized once |
| Relative member inside a legacy list | Requires `--list-base`; never silently uses the caller directory |
| Absolute list member | Uses that path; no list base needed |
| Output/work directory | Existing writable directory, explicitly selected; no automatic creation |
| Log | Fresh `work-dir/mefpp.log`, or fresh `--log-file` resolved from invocation directory; exclusive creation |
| Omitted BPM | No PAF-prefix/caller/output-directory discovery in explicit mode |
| Outputs | Existing legacy product names under output directory; duplicate basenames/planned paths or existing destinations rejected before processing |

`--split` uses the same resolved members and explicit output directory. Direct
science FITS and lists share the existing cube/header/overscan/calibration
processing. Existing calibration FITS dimensions must match the selected
configured cropped extensions; this is a shape check, not detector identity or
scientific suitability validation. M4 retains the physical identity/layout work.

The parser reuses Eclipse's legacy whitespace tokenizer, including its optional
type column. It does not introduce quoting or a new list format. Paths supplied
as CLI arguments and directory bases may contain spaces; a whitespace-containing
filename cannot be encoded in a legacy whitespace-separated list. Select such a
file directly instead. Relative list members are not implicitly list-relative;
provide the original explicit base. Multiple independent bases can be represented
by absolute members (within the legacy token format).

The current native fixed-buffer boundary is retained: canonical input/directory
and generated output paths must be shorter than `FILENAMESZ - 40` (472 bytes),
with suffix room. Lists are bounded to 16 MiB, 100000 rows and lines shorter than
1023 bytes; embedded NUL/CR is rejected. There is no unlimited-path claim.
Full resolved arguments/members/planned outputs and final cwd are recorded in
the explicit log. FITS provenance keeps the existing card semantics and short
original names. Existing qfits long-string serialization #125 is separate.

## Ownership, outputs and scratch

The context owns the resolver and resolved names. Existing legacy callers pass
NULL resolver state. No numerical algorithms, thresholds, shared mosaic
normalization, configuration catalogs or Python inspector code change.

Output preflight prevents deterministic collisions and overwriting existing
files in a private attempt. It is not an atomic concurrent-writer reservation
or all-products transaction; no concurrent-invocation acceptance is claimed.
Preserve failed attempts and inspect partial products after an I/O interruption.
The serial allocator's swap-directory selector is set to the supplied work path;
no swap/allocation policy or global/thread-safety contract changes. Forced swap
is unqualified: existing #164 omits the O_CREAT mode argument, and #144 retains
wider allocation-failure limitations. Ordinary RAM-backed functional acceptance
must not be described as OOM/swap acceptance.

The single science-FITS branch now allocates its overscan statistics arrays,
matching the list branch (#166). Typed and untyped list ownership is explicit,
including partial missing-member cleanup (#163).

## Qualification and remaining gates

See [agent results](m3-native-paths-agent-results-2026-10-30.md). Required target
qualification uses selected tools, a clean source export, private C90 build,
normal `mefpp` plus `cli_capture_probe`, and these two CTests:
`native_explicit_paths` and `native_cli_capture`. Astropy/NumPy are test-driver
dependencies already used by the project; the C executable gains no Python
runtime dependency. `MEFPP_PATH_TEST_WORK_PARENT` optionally selects an existing
local fixture parent; the default is build/test-work. Do not disable preservation
assertions to accommodate a filesystem that changes mode bits.

The native test prepares two tiny instrument-specific two-extension fixtures,
runs the legacy C route, checks independent known-answer arrays, then compares
explicit runs from two unrelated callers with exact pixel values and header
cards/order. Only generated ORIGFILE identifiers and references to those IDs
are normalized to product categories for comparison; no other cards are ignored.
WFI's unchanged 45000 dome threshold accepts different levels from OmegaCAM's
55000 threshold; its independent dome value is 32000/19600. WFI continuous
known-answer checks allow 1e-6 relative float rounding; legacy/explicit comparison
remains exact for both instruments. Bias and BPM known answers remain exact.

Controls include read-only raw/config/list/calibration files and caller dirs,
separate output/scratch/log paths, paths with spaces, existing calibrations,
direct science FITS, optional type columns and split pixels. Rejections cover
ordered duplicates, two distinct same-basename members, missing/partial inputs,
missing list base, incompatible calibration geometry and an existing output
sentinel. Rejections must be controlled positive failure exits, never signals.
Hashes, modes, mtimes and empty caller directories are checked afterward.

Actual Intel Mac and representative shared Chapman qualification is pending.
Do not install, switch the configured engine, merge, or close #163/#165/#166 until
their applicable target/owner gates. M3/#159 remains open for its cumulative
execution and inspector requirements; this increment does not claim complete
M3, scientific acceptance, single-detector layout generalization, grouped
service dispatch, ASDF persistence or a JSON policy change.
