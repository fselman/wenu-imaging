# Joint shutter/linearity numerical interface review

3 November 2026. Status: proposed interfaces, not implemented.

Read the [typeset PDF](joint-shutter-linearity-interface-2026-11-03.pdf).
The matching [LaTeX source](joint-shutter-linearity-interface-2026-11-03.tex)
is retained alongside it. All six rendered pages were visually checked. Section 1 explicitly states that
all detectors contribute accepted measurements to one covariance-weighted joint
estimate of the common signed shutter offset, rather than averaging separate
per-detector fits. A one-page teaching appendix explains Nelder–Mead simplex,
Householder QR, column pivoting and their roles and limitations.

## Completed prerequisite

The gain/RON candidate e0b1647649515aa203932876887b6dff5983871f passed the actual
Intel Mac C17 gate: native_gain_pair/native_gain_pair_allocation 2/2 in 2.58 s.
All three controls (checkout, installed_files, exported_source) passed.
Retained evidence:
`/Users/fselman/Software/build/wenu-imaging/mac-gain-pair-AdGQvwqZ`.
Issue #228's corrected synthetic oracle is accepted/closed.
No unchanged native tests were replayed for this documentation increment.

## Source review and proposed work

The existing Eclipse optimizer provides simplex scaffolding; its current
interface does not supply the checked bounds/context/convergence contract.
The existing matrix least-squares routine uses normal equations and supplies
neither pivoted QR nor the required rank/condition diagnostics.
The PDF proposes checked extensions in those existing modules and a later
detector wrapper. No optimizer is duplicated inside a recipe.

Retain one signed mosaic duration offset, amplifier inverse-response cubics,
constrained bias, fixed declared measurement covariance, signal-space residuals,
monotonicity and measured validity ranges. Pixel prediction precedes ROI
aggregation; an ROI-mean approximation requires explicit validation.
A converged fit alone is insufficient: coverage, numerical rank, conditioning,
multiple starts and shutter-profile checks must support an identified result.

The two new reusable numerical interfaces are presented before implementation,
as requested. The later detector wrapper remains conditional on explicit
pixel/ROI evaluation and covariance-preparation contracts; the current BPM
service is not claimed to provide those yet. No new defect threshold, lamp-drift
fit, corrected science reduction, installation, merge or cleanup is authorized.
