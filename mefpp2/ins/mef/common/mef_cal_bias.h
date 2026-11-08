/* Internal operation-specific C90 API, not an installed/frozen ABI. */
#ifndef MEF_CAL_BIAS_H
#define MEF_CAL_BIAS_H
#include "mef_runtime.h"
#include "image_handling.h"
#include "image_stats.h"

typedef struct mef_bias_result mef_bias_result;
typedef struct {
    /* Raw ADU images in exactly the resolved request input order. All frames
     * represent the same detector. Borrowed read-only during this call only. */
    const image_t *const *frames;
    size_t count;
    /* Explicit configuration mapping; never inferred from detector ID/HDU. */
    size_t configuration_detector;
} mef_bias_input;
/* Opt-in numerical QC. BPM is a borrowed raw-coordinate Eclipse map (1=good),
 * corresponding to the selected MEF_CAL_BPM request. NULL requires explicit
 * omission. No filename/HDU/polarity inference or silent geometry conversion.
 * MAD is optional. RON pair indices are explicit, distinct, zero based; when
 * enabled subtraction uses RAW frames before ANY overscan correction.
 * high_sigma is finite, positive (initial owner choice 5). Clipping is optional and separate from these legacy diagnostics. */
typedef struct {
    const pixelmap *bpm;
    int with_mad, ron_pair_set;
    int bpm_active_only; /* File provenance: mask was embedded from active coordinates. */
    size_t ron_first, ron_second;
    double high_sigma;
    int ron_clip_enabled;
    image_clip_options ron_clip;
} mef_bias_measurement_options;
typedef struct {
    image_sample_stats active_raw, active_corrected, prescan, overscan;
} mef_bias_frame_measurements;
typedef struct {
    size_t count;
    const mef_bias_frame_measurements *frames;
    image_sample_stats master, master_unmasked, raw_difference;
    size_t ron_first, ron_second;
    int ron_stdev_available, ron_mad_available;
    double ron_stdev_adu, ron_mad_adu;
    image_clipped_stats clipped_difference;
    int ron_clipped_available;
    double ron_clipped_adu;
    int high_offset_available, high_offset_degenerate;
    double high_offset_threshold;
    size_t high_offset_count;
    /* 1=flagged high offset (NOT a good-pixel BPM), active coordinates. This
     * diagnostic inspects every finite master pixel, including known defects. */
    const pixelmap *high_offset_flags;
} mef_bias_measurements;

typedef enum { MEF_BIAS_VARIANCE_UNAVAILABLE_LEGACY = 1 } mef_bias_variance_state;
typedef struct {
    mef_bias_variance_state variance_state;
    mef_bpm_selection_state bpm_selection;
    int bpm_applied, ron_estimate_available;
    float frame_mean_average, frame_mean_sigma, rejection_low, rejection_high;
    float product_median, product_stdev;
    int accepted_frames;
    int median_even_handling;
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
mef_status mef_cal_bias_measurements(mef_context *, const mef_bias_input *,
    const mef_bias_measurement_options *, mef_bias_result **, mef_error **);
/* Borrowed QC outlives input/context, owned by result. NULL on legacy call. */
const mef_bias_measurements *mef_bias_result_measurements(const mef_bias_result *);
void mef_bias_result_destroy(mef_bias_result *result);
/* Borrowed views valid until result destruction. */
const image_t *mef_bias_result_signal(const mef_bias_result *result);
const mef_bias_qc *mef_bias_result_qc(const mef_bias_result *result);
const mef_request *mef_bias_result_request(const mef_bias_result *result);
#endif
