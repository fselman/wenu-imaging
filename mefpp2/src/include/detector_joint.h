
#ifndef ECLIPSE_DETECTOR_JOINT_H
#define ECLIPSE_DETECTOR_JOINT_H
#include "optimization.h"
#include "matrix.h"
/* First joint-wrapper increment: DIRECT PIXEL samples only, ADU and seconds.
 * An ROI mean must not be passed as a pixel. Spatial aggregation, covariance
 * preparation and scientific acceptance are later work. Shutter profiles use
 * the explicit separate request below.
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
/* Borrowed, already admitted finite pixel measurements and absolute noise.
 * This shared view has no optimizer/starting-point requirement. */
typedef struct {
    int amplifiers, sites, observations;
    const detector_joint_amplifier *amplifier;
    const detector_joint_site *site;
    const detector_joint_observation *observation;
    const matrix *noise_factor;
} detector_measurements;
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
 * starts/rank/conditioning are numerical checks; a shutter profile, adequate
 * instrument coverage and validated aggregation remain required before science
 * publication. All input arrays borrowed/immutable; result owns copied identities
 * and each nested allocation. *out must be a separate empty owner. Return 0 for
 * candidate or explicit unavailability; -1 on invalid input, allocation or hard
 * numerical/callback failure, with *out unchanged. Never invent unavailable zeros.
 */
int detector_joint_response_fit_checked(const detector_joint_problem *problem,
    const detector_joint_options *options, detector_joint_result **out);
void detector_joint_result_del(detector_joint_result *result);

/* Conditional shutter profile. At EACH fixed delta, refit all other parameters
 * using caller-supplied nuisance simplexes. There is no covariance change,
 * per-detector delay or implicit lamp-drift parameter. Routines above retain
 * their candidate-only behavior and ABI fields.
 */
typedef struct {
    int points, starts;
    const double *delta; /* strictly increasing seconds, inside delta bounds */
    /* points * starts blocks, each P rows by (P-1) nuisance physical values.
     * Full parameter order with delta removed. Independent declared starts;
     * no hidden warm start, coefficient clipping or interpolation. */
    const double *initial_simplexes;
    optimization_options optimizer;
    double delta_chi2; /* explicit positive cost-rise threshold, no confidence default */
    double cost_tolerance; /* absolute chi-square comparison with free-fit minimum */
    double boundary_tolerance; /* seconds for detecting a bound-limited minimum */
} detector_joint_profile_request;
typedef enum {
    DETECTOR_JOINT_PROFILE_NOT_RUN=0,
    DETECTOR_JOINT_PROFILE_POINT_OK=1,
    DETECTOR_JOINT_PROFILE_POINT_INADMISSIBLE=2,
    DETECTOR_JOINT_PROFILE_POINT_UNCONVERGED=3,
    DETECTOR_JOINT_PROFILE_POINT_INCONSISTENT=4
} detector_joint_profile_point_status;
typedef enum {
    DETECTOR_JOINT_PROFILE_BRACKETED=0, /* on declared grid only, NOT science acceptance */
    DETECTOR_JOINT_PROFILE_BASE_UNAVAILABLE=1,
    DETECTOR_JOINT_PROFILE_INCOMPLETE=2,
    DETECTOR_JOINT_PROFILE_GRID_UNBRACKETED=3,
    DETECTOR_JOINT_PROFILE_BOUNDARY_LIMITED=4,
    DETECTOR_JOINT_PROFILE_INCONSISTENT_MINIMUM=5,
    DETECTOR_JOINT_PROFILE_DISCONNECTED=6,
    DETECTOR_JOINT_PROFILE_FLAT_ON_GRID=7
} detector_joint_profile_status;
typedef struct {
    detector_joint_profile_status status;
    detector_joint_result *base; /* owned free-delta fit and input provenance */
    int points, starts;
    double *delta, *initial_simplexes, *cost, *delta_cost, *reference_cost;
    detector_joint_profile_point_status *point_status;
    int *best_start;
    optimization_result **fit; /* point-major, then start; nuisance parameters */
    optimization_options optimizer;
    double delta_chi2, cost_tolerance, boundary_tolerance;
    double minimum_delta, minimum_cost;
    /* Grid indices bracketing threshold crossings. An inside index -1 means
     * the free minimum (minimum_delta, minimum_cost) is the inside anchor.
     * No crossing is interpolated and no symmetric uncertainty is invented. */
    int left_outside, left_inside, right_inside, right_outside;
    size_t evaluations, callback_calls; /* total base + profile optimizer counts */
    size_t preflight_calls; /* extra model checks outside optimizer budgets */
    int flat_on_grid; /* range including the free minimum <= cost_tolerance */
} detector_joint_profile_result;
/* Return 0 publishes an owned diagnostic even if the profile is unavailable.
 * -1 is invalid input, allocation or hard numerical failure; *out unchanged.
 * A point with infeasible declared initial vertices is explicitly unavailable,
 * never replaced with an infinite/zero invented cost. All starts must converge
 * and agree; a fitted conditional cost below the free minimum beyond the stated
 * tolerance is inconsistent. Bracketing applies only to the supplied finite grid
 * and threshold convention, not unsearched delays or frequentist coverage.
 */
int detector_joint_shutter_profile_checked(const detector_joint_problem *problem,
    const detector_joint_options *options, const detector_joint_profile_request *request,
    detector_joint_profile_result **out);
void detector_joint_profile_result_del(detector_joint_profile_result *result);
#endif
