# ESO data preflight and immutable raw inputs

Owner direction, 31 October 2026: all inputs to the new workflow, including ESO,
should pass data preflight governed by WAD. The owner explicitly restates:
**original raw data must never be modified**. This increment implements an
explicit read-only service and shared CLI for OmegaCAM/WFI raw imaging inputs;
it does not silently activate a new gate in the installed legacy reductions.
Tracks #184; candidate cross-keyword filter finding/correction #190 remains
target-pending. Native M4 and full WAD/ASDF runtime integration are separate.

## Immutable source contract

The service opens raw FITS only through the existing inspector's `rb` stream and
Astropy `mode='readonly'`. No `.data` access, header repair, in-place update,
checksum rewrite, gain substitution, pixel conversion or raw-copy publication
occurs. It writes only a separate new report, refusing existing destinations,
source aliases and any destination within a raw input file's parent directory.
The API itself only returns an assessment. Directory/filename structure supplies
no ESO classification guesses. Any later approved metadata preparation must write
new copies; original raw headers, payload, ordering and file identities remain.

Synthetic controls compare source whole-file hashes, permissions and mtime;
reject attempted write-mode opens and scaled image reads; and verify that invalid
metadata produces diagnostics rather than edits. Normal inspection is header-only;
source identity uses stat evidence, not full pixel hashes or an atomic snapshot.

## Shared service and instrument conventions

- [pycavi_preflight.py](../../Pycavi2/pycavi/pycavi_preflight.py) exports
  `preflight_files(paths, invocation_base=...)` for notebooks/CLI and the initial
  ESO raw-imaging adapters. Inputs are explicit bounded file lists; no recursive
  collection/partitioning/association policy is introduced.
- [pycavi_project.py](../../Pycavi2/pycavi/pycavi_project.py) exposes the shared
  `inspect_fits_headers` reader entry point, reusing the qualified M3 bounded
  parser, nonregular-input checks, limits and diagnostics. Existing project
  inspection behavior remains. The public `pycavi preflight` command delegates
  to the same new API. Source invocation through that file works without install.
- Instrument mappings come from existing
  [omegacam.cfg](../../Pycavi2/pycavi/config/omegacam.cfg) and
  [wfi.cfg](../../Pycavi2/pycavi/config/wfi.cfg), with a configuration hash and
  mapping version. No source configuration files are changed.

Correct complete synthetic ESO mosaics (32/8 detectors) pass with
`proposed_additions={}` and `preparation_required=false`; no FITS copies are
needed or made. Blocked assessments leave preparation requirement undetermined,
not an instruction to rewrite raw files. Required metadata includes instrument,
nonnegative exposure, raw DPR category/type/imaging technique, and filters for
science/standard/flat roles. Unknown read mode/gain is visible; no fallback to
unitless GAIN or unity is manufactured.

Each normalized attribute retains the exact source keyword/HDU and authority.
Raw DPR values remain unchanged: WFI `FLAT,SCREEN` and OmegaCAM `FLAT,DOME`
map to the configured dome-flat role separately. Filter comes from the existing
ESO instrument keyword, or reported FILTER when the instrument keyword is
absent. Two reported values must agree. Repeated extension fields must agree
with primary metadata, including cross-keyword FILTER versus native ESO filter.
Malformed unrelated telemetry remains visible as warnings with retained readable
metadata; selected-card errors/duplicates and incompatible required fields block.

Image records preserve original HDU order and resolve identities from unique
EXTNAME values checked against the existing instrument configuration; no detector
is assigned by its HDU number. Missing/unknown/duplicate identities block. Partial
coverage is reported without dropping image records. Detector-specific CONAD keys
are read from the existing mapping with declared electron/ADU convention and
reported-unverified authority; missing gain is unknown, nonpositive gain is an
error, and no value is substituted. Existing WFI zero-CONAD issue #131 remains
independent; preflight may expose it but cannot repair it or certify applicability.

## Assessment limits and rollout

Records use provisional `wad-data-preflight-1` / `eso-header-mapping-1` notation.
They are governed by WAD vocabulary/authority/assessment design, not advertised
as qualified ASDF schemas. Readiness is scoped to **raw-imaging metadata intake**;
calibration/scientific validation and pixel integrity are explicitly not assessed.
This adapter is not the preflight profile for already processed ESO products,
which have different metadata requirements. Additional instruments/profile types
must have explicit mappings and qualification rather than generic ESO guessing.
The existing ASI preflight/preparation interface remains separately available;
convergence of adapters into the full WAD runtime and automatic pipeline intake
is subsequent integration. Current production reducers are not changed or gated.

## Evidence

Agent environment: existing Python 3.12.14, Astropy 6.1.7, NumPy 1.26.4, no new
packages. ESO suite initially passes 10/10 in 1.098 s and inspector regression
24/24 in 6.593 s. After public CLI/raw-report protection, 10/10 in 1.263 s and
24/24 in 6.576 s. A final cross-keyword filter regression reproduces #190 (one
failure: primary ESO filter r_SDSS versus extension FILTER Blue was missed).
The correction compares both spellings; final affected ESO suite passes 10/10
in 2.389 s; the final public-help/report-reference checks pass 10/10 in
3.144 s. Image evidence references the shared asset HDU instead of duplicating
header tables in the JSON. No further inspector replay: its reader/CLI source did not change
for this adapter-only correction. All failed and successful evidence is retained.

The ten controls cover complete ESO mosaics requiring no preparation, native
flat conventions, shuffled identity/order, unknowns and partial coverage,
missing required metadata, same/cross-keyword conflicts, invalid identities/
values, forced no-array/no-write access, file hashes/mode/mtime/caller bases,
limits/FIFO/missing/duplicate inputs, public/backend CLI equality and report
source/destination protection. Inspector regression retains its independent
24-group source/client coverage, using tiny synthetic client bodies and no
external solver/native processing. Logs/source identities:
[the evidence directory](fixtures/agent-eso-preflight-2026-10-31/).

[The target runner](../../Pycavi2/tests/qualify_eso_preflight.py) is prepared for
selected Mac/representative Chapman tools, guarded private exports and protected
installations/clean checkouts; it executes only the ten new synthetic contracts.
Actual target execution is pending, followed by bounded read-only preflight of
explicit actual OmegaCAM/WFI raw inputs. No raw observation was opened in the
agent workspace. No install, source repair, reduction, merge/cleanup, full WAD
runtime or M4 completion is implied by agent tests.
