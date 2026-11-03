
#ifndef ECLIPSE_DETECTOR_JOINT_H
#define ECLIPSE_DETECTOR_JOINT_H
#include "optimization.h"
#include "matrix.h"
/* First joint-wrapper increment: DIRECT PIXEL samples only, ADU and seconds.
 * An ROI mean must not be passed as a pixel. Spatial aggregation, covariance
 * preparation, shutter profiles and scientific acceptance are later work.
 * Input populations are already selected with their BPM/coverage/saturation
 * policy; this numerical service does not silently change them.
 */
typedef struct {
    char detector_id[64], amplifier_id[64];
    double signal_min, signal_max; /* full monotonic/inversion validity interval */
} detector_joint_amplifier;
typedef struct { int amplifier, x, y; } detector_joint_site; /* active pixel, 1-based */
typedef struct {
    int site, input_index;
    double seconds, signal;
} detector_joint_observation;
typedef struct {
    int amplifiers, sites, observations, starts;
    const detector_joint_amplifier *amplifier;
    const detector_joint_site *site;
    const detector_joint_observation *observation;
    /* H in C=H H^T: M by 1 positive diagonal OR M by M lower triangular.
     * Absolute measurement covariance, supplied/justified by the caller;
     * common bias and other correlations must not be silently discarded. */
    const matrix *noise_factor;
    /* P=1+sites+2*amplifiers: delta, L[site], (c2,c3)[amplifier].
     * One signed delta in seconds for ALL observations/detectors.
     * L is per identified physical pixel, not per frame, in linear ADU/s.
     * Coefficients have units ADU^-1 and ADU^-2. No free bias intercept.
     * Initial simplexes: starts consecutive (P+1) by P physical blocks. */
    const double *scales, *lower, *upper, *initial_simplexes;
} detector_joint_problem;
typedef struct {
    optimization_options optimizer;
    int inversion_iterations;
    double inversion_tolerance; /* ADU, absolute bracket-width limit */
    double rank_tolerance, max_scaled_condition;
    double start_parameter_tolerance, start_cost_tolerance;
    double minimum_signal_span; /* ADU, per amplifier; explicit, may be zero */
} detector_joint_options;
typedef enum {
    DETECTOR_JOINT_CANDIDATE=0, /* numerical candidate, NOT a science acceptance */
    DETECTOR_JOINT_UNCONVERGED=1,
    DETECTOR_JOINT_RANK_UNAVAILABLE=2,
    DETECTOR_JOINT_CONDITION_UNAVAILABLE=3,
    DETECTOR_JOINT_COVERAGE_UNAVAILABLE=4,
    DETECTOR_JOINT_STARTS_INCONSISTENT=5
} detector_joint_status;
typedef struct {
    detector_joint_status status;
    int parameters, amplifiers, sites, observations, starts, best_start;
    detector_joint_amplifier *amplifier;
    detector_joint_site *site;
    detector_joint_observation *observation;
    optimization_result **start;
    matrix_qr_result *local;
    double *residuals; /* unwhitened observed minus predicted, ADU */
    matrix *noise_factor; /* owned exact supplied H, retained with numerical options */
    double *scales, *lower, *upper;
    detector_joint_options options;
    matrix *covariance; /* physical parameter covariance, local approximation */
} detector_joint_result;
/* No accepted-calibration status exists in this first increment. Multiple
 * starts/rank/conditioning are numerical checks; shutter profiles, adequate
 * instrument coverage and validated aggregation remain required before science
 * publication. All input arrays borrowed/immutable; result owns copied identities
 * and each nested allocation. *out must be a separate empty owner. Return 0 for
 * candidate or explicit unavailability; -1 on invalid input, allocation or hard
 * numerical/callback failure, with *out unchanged. Never invent unavailable zeros.
 */
int detector_joint_response_fit_checked(const detector_joint_problem *problem,
    const detector_joint_options *options, detector_joint_result **out);
void detector_joint_result_del(detector_joint_result *result);
#endif
