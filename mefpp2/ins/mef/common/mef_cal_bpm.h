/* Typed in-memory BPM numerical service. Not an installed/frozen ABI. */
#ifndef MEF_CAL_BPM_H
#define MEF_CAL_BPM_H
#include "mef_runtime.h"
#include "detector_response.h"
typedef struct mef_bpm_result mef_bpm_result;
typedef struct {
    const image_t *const *frames; /* Raw ADU flats in resolved request order. */
    size_t count, configuration_detector;
    const image_t *master_bias; /* Selected active, scan-corrected ADU master. */
} mef_bpm_input;
typedef struct {
    /* Exactly one form for a selected prior BPM, both NULL for omission.
     * All maps/flags use ACTIVE coordinates. No detector mask touches scans. */
    const unsigned char *prior_flags;
    size_t prior_count;
    const pixelmap *prior_binary; /* Already explicitly converted to 1=good. */
    unsigned int reject_bits; /* 0..255, explicit (typically 255). */
    const pixelmap *const *samples; /* Active per-plane usable-sample selections. */
    const int (*rois)[4];
    size_t roi_count;
    int with_mad;
    int saturation_set;
    double saturation_raw, upper_fraction; /* Raw physical ADU; explicit 0<f<=1. */
} mef_bpm_options;
typedef struct {
    image_sample_stats active_corrected, prescan, overscan;
    size_t saturated, margin_excluded, sample_excluded, nonfinite, reference_samples;
    int included_in_fit;
    double reference_fraction_median; /* Relative to local usable saturation. */
} mef_bpm_frame_qc;
typedef enum { MEF_BPM_PRIOR_OMITTED=1, MEF_BPM_PRIOR_FLAGS8, MEF_BPM_PRIOR_BINARY } mef_bpm_prior;
typedef struct {
    size_t input_count;
    const mef_bpm_frame_qc *frames;
    mef_bpm_prior prior;
    unsigned int reject_bits;
    int bias_applied, provisional_numerical_only;
    int saturation_set;
    double saturation_raw, upper_fraction;
    /* This service does NOT certify acquisition pairs/exposure/saturation
     * coverage, characterize timing, calculate gain/RON or publish products.
     * File-level admission and shared ASDF completion follow separately. */
} mef_bpm_qc;
/* Requires resolved CAL_BPM v1, one detector, one selected MEF_CAL_BIAS and
 * optional matching MEF_CAL_BPM. Immutable raw frames; private copies use the
 * existing scan correction/trim and cube_sub_im before cube_response_checked.
 * Configuration owns algorithm/threshold choice. Options/ROIs/samples borrowed.
 * Result owns request/QC/flags and outlives context, frames and calibrations.
 * Legacy binary prior has no invented reason: combined reasons unavailable,
 * while the combined selection preserves its rejected pixels. With byte prior,
 * combined reasons = prior OR new; new reasons remain separately accessible.
 * Saturation options create usable-sample maps after scan/bias treatment using
 * usable_limit = saturation_raw - (raw - corrected). Entire frames lacking
 * reference samples are explicitly excluded, retaining original indices/QC.
 * Final selection ALSO rejects unavailable fits. NULL/occupied outputs fail
 * intact; status authoritative even when diagnostic allocation fails.
 * Uses operation template; no I/O, cwd change, discovery or reentrancy claim. */
mef_status mef_cal_bpm(mef_context *, const mef_bpm_input *, const mef_bpm_options *,
    mef_bpm_result **out, mef_error **error);
void mef_bpm_result_destroy(mef_bpm_result *);
const detector_response_result *mef_bpm_result_response(const mef_bpm_result *);
const unsigned char *mef_bpm_result_prior_flags(const mef_bpm_result *);
const unsigned char *mef_bpm_result_combined_flags(const mef_bpm_result *);
const pixelmap *mef_bpm_result_selection(const mef_bpm_result *);
const mef_bpm_qc *mef_bpm_result_qc(const mef_bpm_result *);
const mef_request *mef_bpm_result_request(const mef_bpm_result *);
/* One original zero-based flat index per response->reference_levels entry. */
const size_t *mef_bpm_result_fit_indices(const mef_bpm_result *);
#endif
