/* Internal operation-specific C90 API, not an installed/frozen ABI. */
#ifndef MEF_CAL_BIAS_H
#define MEF_CAL_BIAS_H
#include "mef_runtime.h"
#include "image_handling.h"

typedef struct mef_bias_result mef_bias_result;
typedef struct {
    /* Raw ADU images in exactly the resolved request input order. All frames
     * represent the same detector. Borrowed read-only during this call only. */
    const image_t *const *frames;
    size_t count;
    /* Explicit configuration mapping; never inferred from detector ID/HDU. */
    size_t configuration_detector;
} mef_bias_input;
typedef enum { MEF_BIAS_VARIANCE_UNAVAILABLE_LEGACY = 1 } mef_bias_variance_state;
typedef struct {
    mef_bias_variance_state variance_state;
    mef_bpm_selection_state bpm_selection;
    int bpm_applied, ron_estimate_available;
    float frame_mean_average, frame_mean_sigma, rejection_low, rejection_high;
    float product_median, product_stdev;
    int accepted_frames;
    size_t input_frames;
    const float *scan_median, *scan_stdev;
    const int *accepted; /* One per original frame, including rejected frames. */
} mef_bias_qc;

/* Copies raw pixels before existing overscan/trimming and stacking. Requires a
 * resolved CAL_BIAS v1 request, one detector and explicit BPM omission. Selected
 * BPM/calibrations return UNSUPPORTED, never silently ignored. Finite data and
 * valid legacy geometry required. M4 primary/extension planes share this entry;
 * the loader owns selector validation. No I/O, cwd changes, publication or discovery.
 * Result/error start NULL; occupied outputs are rejected intact. Status is
 * authoritative if diagnostic allocation fails. Result outlives context/input.
 * Legacy-compatible ADU signal only: variance UNAVAILABLE until M6a; no new
 * uncertainty-off mode or RON estimator. Eclipse internals are not reentrant
 * or fully allocation-failure qualified by this boundary.
 */
mef_status mef_cal_bias(mef_context *context, const mef_bias_input *input,
    mef_bias_result **out, mef_error **error);
void mef_bias_result_destroy(mef_bias_result *result);
/* Borrowed views valid until result destruction. */
const image_t *mef_bias_result_signal(const mef_bias_result *result);
const mef_bias_qc *mef_bias_result_qc(const mef_bias_result *result);
const mef_request *mef_bias_result_request(const mef_bias_result *result);
#endif
