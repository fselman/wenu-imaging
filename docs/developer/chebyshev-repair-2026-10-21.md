# Chebyshev illumination repair, 21 October 2026

Fernando authorized this focused repair after the Intel Mac CP Puppis pilot.
Tracking: [issue 3](https://github.com/fselman/wenu-imaging/issues/3).
Implementation baseline: `b01c3c0689d3cbb4344f15a2130e44bca5da079a`.

## Findings and scope

The weighted degree-(5,5) fit has 36 coefficients. Export and explicit evaluation
incorrectly used only orders 0–4, or 25 terms. The saved map used the full fit,
whereas the residual diagnostic used the truncated model. On the Mac calibration
stars, the difference was 0.0035617408 mag RMS, reaching 0.0109371690 mag.

Include orders 0 through the specified degree in both basis directions. Retain
the existing weighted fit, coordinate scaling, file syntax, and sparse omission
of zero coefficients. Evaluation of a parsed sparse file treats omitted
coefficients as zero. A legacy export missing its highest-order basis raises a
clear regeneration error: the missing fitted coefficients cannot be recovered
from that file. Regenerate from the original fit or the same photometric data;
do not relabel its degree or pad it with invented fitted coefficients.

Repair notebook 07c and the dedicated 08a Chebyshev notebook: correct argument
binding, align image and contour grid orientation, and explicitly save corrected
and spatial residual plots. Keep current scientific selections and fit defaults.
07c is marked obsolete in its original introduction; its repair supports
reproducing the pilot, while 08a remains the dedicated Chebyshev workflow.
This work does not apply corrections to image pixels or change catalogue
correction signs, reference transformations, masks, exposure normalization or
mefpp behavior.

## Reported Mac evidence before this repair

Python environment: `~/anaconda3/envs/wenu-imaging`, Python 3.11.14.
Orchestration directory: `~/Software/wenu-imaging-testing`.
Pilot output: `~/Pictures/OCAM/CPPup-wenu-imaging-test`.

| Clipped statistic | Before correction | Complete fitted model |
|---|---:|---:|
| Full-sample scatter | 0.0325 mag | 0.01580937 mag |
| Withheld-star mean | -0.01513529 mag | -0.00453857 mag |
| Withheld-star scatter | 0.03094636 mag | 0.01630766 mag |

The seeded split (NumPy default_rng, seed 42) used 1782 training and 446 withheld
stars, with fit rank 36. This supports within-field prediction; it does not
establish absolute accuracy, generalization to other observations, or ESO Phase
3 compliance. These are user-reported Mac results, not measurements rerun by
the development host. The residual mean remains nonzero.

## Regression checks

Run from the repository root, in a Python environment with NumPy, pandas and
SymPy installed:

```bash
python -m unittest discover -s Pycavi2/tests -v
```

Tests compare exported, parsed and explicitly evaluated models against NumPy's
independent Chebyshev evaluator at corners and interior points, including
degree zero, unequal axis degrees, degree five and sparse zero coefficients.
They verify weighted recovery of a known degree-five surface, rejection of a
truncated legacy basis, and notebook plot calls against the actual function
signatures, coordinate orientation and explicit save paths. Plot contract tests
execute the notebook plotting cells with argument-capturing functions; they do
not render figures or import the network-active calibration module.

Four offline regression tests pass on the Linux development host. Native Mac
rerun of the repaired source and copied notebooks remains the next validation.

## Updating the Mac without overwriting the pilot

After review and merge, synchronize the Mac checkout with `git pull --ff-only`.
Its editable installation will use the updated module after restarting notebook
kernels. Previously copied notebooks are independent files: Git does not update
them. Preserve `wenu-imaging-testing` with its local edits and outputs. Prepare a
new orchestration directory, copy the existing project configuration deliberately,
and copy the repaired notebook templates there. Do not run `pycavi_setup` over
the existing orchestration directory because setup overwrites copied resources.
For 07c, explicitly select index 0 for this single-coadd pilot; its original
template selection of index 2 is preserved in this repair.

Regenerate coefficient files and diagnostics in an isolated verification copy of
the calibration working directory. Compare full and exported evaluation: their
difference should be at floating-point roundoff, rather than millimagnitudes.
Only then review the existing downstream correction path before modifying any
science product or catalogue. Existing truncated coefficient files remain
historical evidence and must not be silently overwritten or reused as full fits.

## Deferred audit items

The mefpp executable/resource-directory interface, remaining Kriging/readback
notebook calls, historical radial-coordinate diagnostics, GUI lifecycle and
Phase 3 product metadata remain outside this focused repair. Kriging has not
been demonstrated to fail on this Mac; its historical failure comment does not
identify a platform. No broad notebook cleanup or scientific-default changes
are included.
