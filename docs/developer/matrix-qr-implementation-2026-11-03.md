# Checked Eclipse QR increment - 3 November 2026

Owner authorized implementation after reviewing the joint shutter/linearity
interface and teaching appendix at 1b1823bf. This increment implements only the
reviewed reusable matrix extension; the checked optimizer and joint detector
wrapper are subsequent work. PR #227; ownership/failure contract relates to #75.

`matrix_leastsq_qr_checked` solves design * solution ~= rhs for row-major M by P
design, M >= P, and one M by 1 RHS. This explicitly differs from the legacy
`matrix_leastsq` orientation XA=B. Borrowed inputs are immutable; the output
owner must be NULL. Errors return -1 without publishing a partial result.
`matrix_qr_result_del` owns every result allocation, using existing qfits memory
accounting. Legacy functions and their allocation paths remain unchanged.

Column scales mean design[:,k] * scale[k]; the returned solution has the original
parameter order and units. Column-pivoted Householder reflections use hypot norms
and unit-scaled reflector vectors. Rank uses pivot norm / largest initial scaled
column norm against the explicit relative tolerance (0 < tolerance < 1). The
result records rank, pivots, upper triangular R in scaled pivot order, projection
residual norm, and a full-rank solution. Rank deficiency returns no solution and
no available condition estimate. It never publishes invented zero coefficients.

The scaled condition diagnostic computes ||R||_1 ||inverse(R)||_1 via triangular
column solves without storing an inverse. It describes scaled triangular R,
not the exact 2-norm condition number of the unscaled design. This first increment
retains R for future triangular covariance solves; it does not yet implement
covariance or choose scientific rank/conditioning thresholds. Overflow and
nonfinite arithmetic fail explicitly; the method is not claimed to support every
representable extreme-scale system.

## Preparation verification

Isolated Linux GCC C17 Release build of QR controls and normal mefpp passed.
Exactly native_matrix_qr and native_matrix_qr_allocation passed 2/2 in 0.04 s.
Known-answer checks cover a noisy straight line, three-parameter quadratic with
independently orthogonal residual, scalar/diagonal systems, pivot-factor
reconstruction, strongly scaled columns, exact/near/zero rank, caller tolerance,
invalid shape/data/scales, overflow, occupied output, immutable input and the
unchanged legacy XA=B result. All ten allocation positions were exercised with
single and persistent NULL returns; qfits owner/resources and inputs were
preserved. Existing dependency warnings are retained; new QR source is warning
free in the final build. These checks are preparation, not actual Mac acceptance.

The Mac runner reuses qualify_gain_pair_mac.py's exact-source export,
installation/checkout preservation and retained-log scaffolding, selecting only
the two new QR entries and building normal mefpp. Its Python syntax was checked.
No unchanged gain/RON replay, observations, install, activation, merge or cleanup.
Actual Mac gate is pending, followed by changed-code Chapman validation before
full actual-data testing there. Evidence is retained beside this note.
