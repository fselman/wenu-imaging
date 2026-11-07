# Standalone native bias recipe — 6 November 2026

## Executive summary

The uninstalled `mefpp_bias_recipe` candidate now connects the existing serial bias
operation to output-path selection, private detector products, final native MEF
assembly, native ASDF QC and the selected product log. It calls no Pycavi or
Python. Bias arithmetic is unchanged. Strict new-code C17 checks and four actual
kernel/QC-copy lifetime profiles pass in the agent environment. Full command build
and synthetic FITS/ASDF integration remain pending on the retained Mac tools.
Real whole-mosaic processing and viewer work have not started.

## Reviewed baseline and earlier decisions

The owner approved retaining final MEFs, temporary detector separation, a
coordination boundary, serial execution first, and one native ASDF per final
FITS. Output selection remains mutually exclusive `--output-dir` or complete
`--output`; the latter supplies the directory and retains its filename. Generated
bias names are `CMDP.<recipe-start-time>.001.fits`, with corresponding `.asdf` and
`.log` siblings. Capture the recipe start once. Existing destinations are refused.

The previous path helper passed 11 Mac checks, the native QC writer passed ten
Mac checks in 2.589s at1434606, and the native assembler passed eight Mac groups
in5.630s plus three independent Astropy checks at316d2a2. Preserve their retained
evidence. This increment integrates those modules rather than replaying their
unchanged gates. The current normal/installed legacy `mefpp` and one-detector
`mefpp_m5` remain unchanged; the latter is an integration comparison reference.

Source review showed the old M5 entry handled one detector and wrote a JSON
transport for Python completion. That path stays available for compatibility.
The new standalone entry directly calls `mef_bias_files_execute_measurements`,
which retains the reviewed `mef_operation_run` lifecycle and unchanged
`mef_cal_bias_measurements`/kernel. Its typed QC builder delegates serialization
to the common native ASDF writer; there is no recipe-specific ASDF serializer,
JSON handoff or upstream runtime requirement in the new command.

## Explicit command inputs

```
mefpp_bias_recipe cal bias
  (--pafname CONFIG.paf | --config CONFIG.toml)
  --bias ABSOLUTE_INPUT_LIST
  (--output-dir DIRECTORY | --output COMPLETE_FITS_PATH)
  --reference-detector ID --mad (yes|no)
  [--ron-first ZERO_BASED --ron-second ZERO_BASED] [--high-sigma K]
  --detector-id EXTNAME --config-detector ZERO_BASED
  --readout-id ID --bin-x N --bin-y N --amplifier-id ID
  --input-bpm (omitted|BPM_FITS) --hdu N [--hdu N ...]
  [...repeat detector blocks...]
```

The detector block begins at `--detector-id`. One `--hdu` applies the explicitly
declared index independently to every input; alternatively provide exactly one
index per ordered input. This permits extension order to differ by file. Select
the BPM independently per detector with `--bpm-hdu`, `--bpm-good-value` (0/1),
`--bpm-coordinates` (raw/active), and optional `--bpm-expected-extname`. No BPM
filename, polarity, readout, amplifier claim, RON pair or detector selection is
inferred from upstream directories or default PAF filenames. High sigma retains
the existing approved default5; an explicit finite positive override is supported.
MAD and the BPM selection must be explicit. Only ADU/count QC is produced.

The first integrated entry covers named MEF detector extensions: logical IDs
must equal their asserted raw EXTNAMEs. Raw-primary and logical-ID/EXTNAME alias
profiles remain available through the older one-detector operation but are not
claimed supported by this integrated command. The caller supplies the complete
selected detector set and explicit primary-reference ID; a manifest cannot
discover an intentionally or accidentally omitted declaration. Configuration
slots, physical input HDUs and final output ordinals remain independent.

The input-list entries must be absolute, in the intended recipe order; duplicates
are refused. Configuration/list/BPM arguments may resolve against invocation cwd;
raw locations are canonicalized for the actual operation and recorded explicitly.
Output paths resolve once against cwd. The output parent, including `bias/` or
`cal/bias/` if selected, must already exist. The engine neither discovers the
orchestration/raw/products roles nor changes cwd or creates selected output roots.
Existing ORIGFILE one-card/68-character basename limits remain explicit (#125).

## Lifecycle, ownership and truthful completion

1. Sample one start time, parse options and resolve exclusive final paths.
2. Read the selected native configuration and ordered input list. Catalogue raw
   headers once, bind every detector independently in each file, and validate
   geometry, configuration slots and selected BPM metadata before output creation.
3. Reserve the selected product log exclusively. Create one private
   `.mefpp-bias-XXXXXX` directory inside that same products directory. Logs record
   source/start/configuration/input list, canonical raw paths and detector progress.
4. Serially load only the current detector/BPM, call the existing bias operation
   and publisher, copy its QC into owned metadata, then destroy its image result,
   request/context and mask. Private one-detector FITS remain for assembly.
5. At the coordination barrier, require all selected detectors to have completed.
   Bias performs no new harmonization. Validate the complete typed QC descriptor,
   assemble the final MEF and write its corresponding ASDF with external libasdf.
6. Remove only this successful invocation's private detector files/directory;
   failed cleanup is logged and never deletes final products. Close/check the
   selected log. Only then print `BIAS_RECIPE_COMPLETE` and return zero.

On failure, return nonzero, retain useful private work/log and any already
completed final MEF/ASDF, and report no overall success. There is no automatic
retry/replacement or multi-file atomic transaction. The log's `OUTPUTS_WRITTEN`
line explicitly requires a zero command exit for final success. No raw file is
opened for writing. Caller-held stable files remain essential; this is not an
OS snapshot/lock or cryptographic input-verification scheme.

No full-mosaic pixel cube is retained by the coordinator. The existing per-detector
loader and kernel still have their qualified raw-plane/private-copy memory costs.
Owned metadata grows with inputs/detectors and flagged-pixel locations; no measured
peak-memory or new allocator-failure qualification is claimed.

## QC preservation

`mef_bias_product_qc` copies native per-input raw/corrected active, prescan and
overscan samples, sample partitions, scan-correction summaries/settings, acceptance
and actual input HDUs. Product records retain masked/unmasked master statistics,
raw pair difference, already-computed RON, high-offset count/threshold/degeneracy
and sparse coordinates, existing legacy rejection/product diagnostics, and explicit
unavailable variance. Each raw record is embedded once; calibration references
are deduplicated by canonical path with per-detector HDU bindings.

Stage, region, unit, estimator and nonfinite/mask meanings follow the existing
bias QC bridge. The historical multiplication of MAD by1.4826 is retained when
assembling the `scaled_mad` field; no estimator is reimplemented. RON itself is
copied from the native result. New parameter rows retain explicit MAD/RON choices,
high sigma and selected BPM polarity/coordinate convention. Empty coordinate
sets are null with an explicit zero-flagged-pixels reason because the existing
schema's measured vectors require at least one element; measured hot count zero
still distinguishes that known empty set from unrequested MAD.

Configuration is the exact native effective typed-bits snapshot embedded as text
inside ASDF. Digests remain explicitly unverified unless supplied by the existing
container contract. No mosaic-averaged gain/RON is invented, and no plot is made.

## Verification and limits

Announced agent checks use the actual unchanged bias subroutine on synthetic
6x4 arrays: two detectors/four inputs across unmasked MAD+RON, masked MAD+RON,
unmasked RON without MAD, and masked neither-MAD-nor-RON profiles. They check exact
copied values/acceptance/mappings, input-pixel preservation and QC validity after
native results/images are destroyed. All four profiles pass. Strict C17 new-code
warnings-as-errors and Python AST checks pass. No actual ASDF writer is replaced
or mocked: unused write code is discarded only for this metadata-copy probe.

The first ad-hoc agent probe link omitted the existing `mef_paths.c` dependency
and failed before any test (#253). The corrected direct command includes that
unchanged module. Retained agent evidence is under
`/workspace/scratch/b0416c2b7710/bias-recipe-checks`: original build.log/compile-command.json,
corrected command/build, and final-build.log/final-probe.log. The existing CMake
common library already includes the path module. Legacy NULL-free diagnostics
remain visible; no legacy destructor or numerical code is changed here.

The Mac integration driver prepares the established tiny synthetic FITS fixture
and executes eight groups through the actual new command from an empty
orchestration directory. Raw fixtures and comparison products are frozen and
fingerprinted. It checks:

- Relative output directory and generated name, one MEF/ASDF/log and no leftover
  successful private products.
- Complete relative output-name inheritance and independently reordered per-file
  HDUs, including exact detector pixels/cards versus the existing M5 command.
- TOML settings, explicit BPM/MAD/RON omissions and truthful unavailable QC.
- Both/neither destination options and protected FITS/ASDF/log/dangling outputs.
- Bad mappings, duplicate detectors, unknown primary reference and invalid RON pair.
- Nonbinary selected BPM content: failed status/log and retained private work,
  with no final FITS/ASDF or false completion marker.

Three successful cases are independently opened with Astropy and retained ASDF6,
including local schema validation and exact QC comparison to existing native
one-detector results. Only generated DATE/ORIGFILE/NEXTEND/CHECKSUM differences are
excluded from header comparisons. Small expected JSON files are test data, not
production transport. No Pycavi is imported. CMake and libasdf runtime are absent
in the agent environment, so the complete new entry/build path and these target
tests are prepared but unexecuted. No full-recipe success is claimed yet.

Build the opt-in candidate with C17, `MEFPP_BUILD_BIAS_RECIPE=ON`, exact
`MEFPP_SOURCE_REVISION` and the retained `MEFPP_ASDF_PREFIX`. No install command,
dependency download, normal-executable activation or unchanged-gate replay is
included. After Mac synthetic acceptance, obtain current exact real input/config/
BPM/RON and directory evidence for the actual whole-mosaic recipe invocation.
Owner inspection of its real MEF and ASDF precedes the Bias saved-plot viewer.
Overall #245 remains open; no merge or branch/evidence cleanup is authorized.
