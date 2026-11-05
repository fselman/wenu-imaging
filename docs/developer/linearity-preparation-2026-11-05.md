## Actual Mac overscan gate passed - 5 November 2026

Owner returned d8bf5608c73b3aee8b5411b3193f4184bd0f7b5a qualification passed at
mac-linearity-prepare-5QEzvc2c. Native4/4 in5.91s plus required6TOML+5viewer
controls; checkout, installed_files and exported_source all true. Reuse exact
retained source/build; do not replay this gate. See [receipt](evidence/linearity-preparation-2026-11-05/mac-receipt.md).

Next is the authorized FITS/linearity-recipe/ASDF integration, using detector and
processing TOMLs, existing corrected masters/memberships and direct-site archive.
Read existing metadata first; no repeated bias generation, singleton extraction,
old gate, physical fit, installation, merge or cleanup. Full corrected ROI ASDF
products do not exist yet. Earlier pending-Mac statements below are historical.

# Row-overscan preparation candidate - 5 November 2026

Refs #235/#236; draft PR #227. Owner reviewed the TOML-led detailed design at
5b3a493 and instructed implementation. This increment implements overscan
preparation kernels and the TOML resolver. Complete real-data recipe/ASDF
orchestration follows the changed-code actual-Mac overscan gate.

## Implemented boundary

- pycavi_linearity_config resolves detector and processing TOMLs without PAF
  fallback. It freezes exact input text/hashes, separates full bands from sampled
  rectangles, validates row coverage/containment/trim/ROIs and explicit controls.
- The processing TOML adds version1 numerical preparation controls with the
  previously recorded scientific values. The viewer calls the same resolver
  for numerical candidate profiles; reference-only WFI remains unchanged.
- mef_overscan_correction_traced adds an optional trace to the existing arithmetic,
  copying each estimate before QC median sorting. Legacy interfaces passNULL/0.
- mef_linearity_prepare_frame corrects a private raw copy, crops it and subtracts
  an active corrected master only for flats. Bias role forbids a master. Enabled
  scan reads, geometry and logical-pixel limits are validated.
- mef_linearity_prepare_pairs reuses unchanged raw-pair statistics, then prepares
  flats two at a time. Corrected member and difference statistics use the exact
  raw four-plane population. Owned results retain ordered scan traces, raw
  diagnostics, copied metadata and explicit availability. The master is subtracted
  once; the raw bias pair is corrected separately for trace evidence. Existing
  all-bias construction remains in mef_cal_bias; its behavior is unchanged.

The native services take typed resolved settings. The Python resolver is NOT yet
connected to a FITS-to-ASDF command by this increment. Real file admission must
verify readout/HDU/master/configuration lineage and feed those settings through
that recipe before new observational products can exist. Do not call this a
completed end-to-end recipe or relabel old ASDF data as corrected.

## Checks actually run

Agent Linux GCC C17 Release builds normal mefpp and focused probes. Four native
controls pass: new preparation, affected existing sample/pair paths, and the
existing bias-service comparison with its independent legacy reference. New
43/44-read fixtures cover nonconstant row ramps, first/last raw and active rows,
exact legacy singleton-path equality, staged subtraction, common populations,
independent analytical means/sample scatter, empty/singleton availability,
invalid geometry/scan/master/budgets and detached owners. Each width passes128
persistent custom-owner allocation-failure positions. This is not general
Eclipse/dependency OOM qualification. New preparation source is warning-free;
existing dependency warnings remain.

Six TOML controls and five footprint/viewer controls pass. No FITS observations,
new ASDF publication, physical fit, installation or dependency provisioning ran.
Existing local CMake was reused. The first build launch omitted the opt-in probe
flag, so it built no target; this was corrected before native compilation.
New preparation fixtures were rerun as their code/coverage changed; no unchanged
full historical matrix was replayed.

[Evidence receipt](evidence/linearity-preparation-2026-11-05/agent-receipt.json)
records checks and log hashes. [Mathematical guide](linearity-preparation-guide-v1.pdf)
and [LaTeX](linearity-preparation-guide-v1.tex) describe final kernel equations,
units, population, ownership and limits:2pages, visually checked, no overfull boxes.

## Actual Intel Mac gate and next work

Pycavi2/tests/qualify_linearity_prepare_mac.py exports exact fetched source into
a fresh private build run, preserves clean normal main/installed files/exported
source, uses C17/Xcode and niceness>=10, and runs exactly four native controls
plus six TOML and five viewer checks. It builds normal mefpp, installs nothing,
reads no observations and provisions no dependencies. The ASDF runtime is unused
and untouched. Runner source/dispatch is inspected here; actual execution is
pending. Obtain fresh actual-Mac checkout evidence before fetch; give one
dependent command group at a time.

After that receipt, integrate kernels, the existing complete bias recipe, file
bindings, direct-site replay, native transports and common ASDF writer into the
linearity preparation section. Preserve all ten bias input decisions, master
membership, full corrected ROI coverage, raw diagnostic definitions and160direct
sites. Actual corrected products must carry exact TOMLs, applied settings, scan
evidence, source/master graph and stage. Then independently compute/save
residual/ratio diagnostics and inspect corrected data before physical modelling.
No noise/covariance assumptions or fit are supplied by these kernels. Preserve old
archives and retained runs. No merge, installation or cleanup occurs here.
