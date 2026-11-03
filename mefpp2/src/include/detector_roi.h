
#ifndef ECLIPSE_DETECTOR_ROI_H
#define ECLIPSE_DETECTOR_ROI_H
#include "detector_joint.h"
/* ROI coordinates are inclusive FITS active pixels, never electronic scans. */
typedef struct { char roi_id[64]; int amplifier, xmin, xmax, ymin, ymax; } detector_roi;
typedef struct {
    detector_measurements data;
    const int (*dimensions)[2]; /* active width,height for each amplifier */
    int rois;
    const detector_roi *roi;
    /* Optional M by K finite pixel predictions/Jacobian/other vector columns.
     * The SAME membership/equal weights project every column. Never evaluate
     * a nonlinear response at an ROI mean instead of predicting pixels first. */
    const matrix *pixel_vectors;
    double covariance_rank_tolerance, max_factor_condition;
    size_t max_dense_elements; /* explicit per-matrix software resource limit */
} detector_roi_problem;
typedef struct {
    int roi, input_index;
    double seconds, mean; /* mean is unavailable (NaN) when count==0 */
    size_t count;
} detector_roi_row;
typedef enum {
    DETECTOR_ROI_READY=0,
    DETECTOR_ROI_EMPTY=1,
    DETECTOR_ROI_COVARIANCE_RANK_UNAVAILABLE=2,
    DETECTOR_ROI_COVARIANCE_CONDITION_UNAVAILABLE=3
} detector_roi_status;
typedef struct {
    detector_roi_status status;
    int rois, frames, rows, active_rows;
    size_t geometric_overlap_pairs, shared_observations, union_observations, union_sites;
    detector_roi *roi;
    detector_roi_row *row; /* ROI-major, frame first-appearance order; empty retained */
    size_t *offset; /* rows+1, CSR membership boundaries */
    int *member; /* source observation indices; same index can occur in overlapping rows */
    int *active_to_row; /* numerical matrices index only nonempty rows */
    int *union_index; /* distinct selected observation indices, in source order */
    detector_joint_amplifier *amplifier;
    detector_joint_site *site;
    detector_joint_observation *observation;
    int amplifiers, sites, observations;
    int (*dimensions)[2];
    matrix *source_noise_factor;
    matrix *projected; /* active_rows by K, NULL if no optional vectors */
    matrix *latent_factor; /* B=A H, active row order, not necessarily triangular */
    matrix *covariance; /* B B^T, original active row order, even when singular */
    matrix_qr_result *factor_qr;
    int factor_qr_transposed; /* QR used B^T if rows<=M; otherwise B (rank only) */
    matrix *noise_factor; /* lower, positive diagonal, FULL RANK ONLY */
    int *factor_to_active; /* whitening row i -> original active row index */
    double covariance_rank_tolerance, max_factor_condition;
    size_t max_dense_elements;
} detector_roi_result;
/* Exact arithmetic-mean operator A: each admitted member has weight 1/count.
 * C_roi=(A H)(A H)^T, preserving overlap/shared-bias correlations. Qualified
 * pivoted QR of B^T yields C in a recorded row permutation and a positive-
 * diagonal lower factor; no new Cholesky, hidden jitter or diagonalization.
 * Duplicate ROIs remain correlated/singular, not independent measurements.
 * Unavailable factor stays NULL; empty rows are explicit, never zero means.
 * ROI output is NOT a detector_joint_site and cannot substitute an ROI mean
 * into the direct-pixel fitter. This service prepares operators/covariance,
 * not raw extraction, a fitted illumination-shape assumption or a calibration.
 * Inputs borrowed/immutable; result owns snapshots and all nested allocations.
 * Return 0 including explicit unavailability, -1 invalid input/allocation/
 * nonfinite arithmetic with separate empty/occupied *out unchanged.
 */
int detector_roi_aggregate_checked(const detector_roi_problem *problem,detector_roi_result **out);
void detector_roi_result_del(detector_roi_result *result);
#endif
