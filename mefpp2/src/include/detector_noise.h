#ifndef ECLIPSE_DETECTOR_NOISE_H
#define ECLIPSE_DETECTOR_NOISE_H
#include "detector_joint.h"
typedef struct { int input_index, amplifier, y; } detector_noise_scan_group;
typedef struct {
    detector_measurements data; /* finite fit-admitted samples; noise_factor MUST be NULL */
    const double *independent_variance; /* one per observation, ADU squared, >=0 */
    const matrix *master_factor; /* sites x Kb, ADU: master covariance Fb Fb^T */
    int scan_applied, scan_groups;
    const detector_noise_scan_group *scan_group;
    const matrix *scan_factor; /* groups x Ks, ADU: correction covariance Fs Fs^T */
    int independent_components; /* MUST be 1: the three component blocks independent */
    double rank_tolerance, max_factor_condition;
    size_t max_dense_elements; /* explicit PER matrix element ceiling */
} detector_noise_problem;
typedef enum { DETECTOR_NOISE_READY=0, DETECTOR_NOISE_RANK_UNAVAILABLE=1,
    DETECTOR_NOISE_CONDITION_UNAVAILABLE=2 } detector_noise_status;
typedef struct {
    detector_noise_status status;
    int amplifiers, sites, observations, scan_applied, scan_groups;
    detector_joint_amplifier *amplifier;
    detector_joint_site *site;
    detector_joint_observation *observation; /* original order */
    detector_joint_observation *ordered_observation; /* QR factor row order; READY only */
    detector_noise_scan_group *scan_group;
    int *observation_to_scan; /* original order; -1 for explicit no-scan case */
    int *factor_to_observation; /* whitening row -> original observation */
    double *independent_variance; /* original order */
    matrix *master_factor, *scan_factor, *latent_factor, *covariance;
    matrix_qr_result *factor_qr;
    matrix *noise_factor; /* positive-diagonal lower factor, QR row order */
    double rank_tolerance, max_factor_condition;
    size_t max_dense_elements;
} detector_noise_result;
/* Assemble C=D + Pb Fb Fb^T Pb^T + Ps Fs Fs^T Ps^T, ADU squared.
 * Pb repeats a physical site's master error across exposures. Ps maps named
 * (original frame index, amplifier index, active row) correction errors. Both
 * coefficients are -1 because master and scan are subtracted. Scan/master
 * factors may encode arbitrary correlations WITHIN each block. The three blocks
 * must be caller-established independent; cross-block correlations need another
 * model and are unsupported, never silently dropped. Factors/variances must be
 * supplied explicitly: no gain/RON/scan-estimator default, jitter or uncertainty
 * estimation. Even a known-zero master factor must be explicitly supplied.
 * scan_applied=0 requires zero groups and NULL group/factor; otherwise every
 * observation must map exactly once. Unused valid groups are allowed.
 * Qualified pivoted QR of the latent factor transpose supplies rank, condition
 * and a lower factor. C remains in original order. Only READY exposes ordered
 * observations + factor with an explicit permutation. Predictions/Jacobians
 * must follow the SAME permutation; no pixel/frame identity is changed.
 * Inputs immutable; result owns all snapshots. 0 includes rank/condition
 * unavailability, never science acceptance. -1 invalid input, allocation or
 * nonfinite arithmetic, *out unchanged. *out must start NULL. Dense reference
 * construction only; no full-mosaic scaling/reentrancy claim.
 */
int detector_noise_assemble_checked(const detector_noise_problem *,detector_noise_result **out);
void detector_noise_result_del(detector_noise_result *);
/* Borrowed view valid only during result lifetime; fail intact unless READY. */
int detector_noise_measurements(const detector_noise_result *,detector_measurements *out);
#endif
