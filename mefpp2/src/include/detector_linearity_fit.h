#ifndef ECLIPSE_DETECTOR_LINEARITY_FIT_H
#define ECLIPSE_DETECTOR_LINEARITY_FIT_H
#include "detector_noise.h"
/* Recipe composition boundary for already corrected, fit-admitted DIRECT PIXELS.
 * The caller supplies established absolute noise and correction/sample provenance.
 * No gain, distribution, interval, covariance or optimizer default is selected.
 */
typedef struct {
    detector_noise_problem noise;
    int starts;
    const double *scales, *lower, *upper, *initial_simplexes;
    detector_joint_options fit;
    const detector_joint_profile_request *profile; /* mandatory explicit request */
    const char *sample_set_id, *noise_model_id, *correction_pipeline_id;
} detector_linearity_fit_problem;
typedef struct {
    char detector_id[64], amplifier_id[64];
    double c2, c3; /* S_linear = S + c2*S^2 + c3*S^3, ADU^-1, ADU^-2 */
    double declared_signal_min, declared_signal_max; /* inversion/monotonic branch */
    double observed_signal_min, observed_signal_max; /* actual admitted ADU coverage */
    /* Local conditional covariance in order [common delta, c2, c3]. Full
     * covariance including cross-amplifier terms stays in profile->base. */
    double covariance[9];
} detector_linearity_curve;
typedef enum {
    DETECTOR_LINEARITY_NOISE_UNAVAILABLE=0,
    DETECTOR_LINEARITY_FIT_UNAVAILABLE=1,
    DETECTOR_LINEARITY_PROFILE_UNAVAILABLE=2,
    DETECTOR_LINEARITY_CURVE_CANDIDATE=3 /* numerical only; NEVER science acceptance */
} detector_linearity_fit_status;
typedef struct {
    detector_linearity_fit_status status;
    char sample_set_id[128], noise_model_id[128], correction_pipeline_id[128];
    detector_noise_result *noise; /* original order, factor order and permutation */
    detector_joint_profile_result *profile; /* owns free fit and all profile points */
    int curves; /* zero and curve NULL when any numerical gate unavailable */
    detector_linearity_curve *curve;
    double common_delta_seconds; /* NaN unless curves > 0; one value for all CCDs */
} detector_linearity_fit_result;
/* Compose supplied covariance -> SAME QR-ordered samples and factor -> joint
 * profile fitter -> amplifier-specific candidate curves. Physical site indices
 * and original frame indices are preserved; ROI means are not substituted.
 * Covariance is fixed for the whole free fit/profile. This does not estimate or
 * validate a physical noise model or manufacture correction/master products.
 * Return 0 publishes an owned candidate OR explicit unavailable diagnostic.
 * Return -1 leaves *out unchanged on bad input/allocation/hard numerical failure.
 * All sources borrowed; result outlives them. *out must start NULL. No file I/O,
 * automatic application, acceptance, fitting interval or photometric correction.
 */
int detector_linearity_fit_checked(const detector_linearity_fit_problem *,detector_linearity_fit_result **out);
void detector_linearity_fit_result_del(detector_linearity_fit_result *);
#endif
