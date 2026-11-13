#ifndef MEF_BPM_FILES_H
#define MEF_BPM_FILES_H
#include "mef_cal_bpm.h"
#include "mef_detector_cube.h"
#include "mef_layout.h"
typedef struct mef_bpm_files_result mef_bpm_files_result;
typedef enum { MEF_BPM_PROVISIONAL=1, MEF_BPM_QUICK } mef_bpm_acquisition;
typedef enum { MEF_BPM_MASK_OMITTED=1, MEF_BPM_MASK_FLAGS8, MEF_BPM_MASK_BINARY } mef_bpm_mask_encoding;
typedef struct {
    mef_bpm_acquisition mode;
    const size_t *pair_ids; /* Required quick: count entries, each ID < count. */
    const char *exposure_key; /* Full qfits name, no inferred keyword. */
    int exposure_hdu; /* Explicit header HDU for every file (usually primary). */
    double saturation_raw, upper_fraction, minimum_span_fraction, maximum_pair_difference;
    mef_bpm_mask_encoding mask_encoding;
    int binary_good_value, prior_active_only, with_mad;
    unsigned int reject_bits;
    const char *mask_registry; /* Explicit when FLAGS8. */
    const int (*rois)[4];
    size_t roi_count;
} mef_bpm_files_options;
typedef struct {
    mef_bpm_acquisition mode;
    size_t input_count, usable_pairs, distinct_times, distinct_levels, paired_levels, configuration_detector;
    const double *integration_seconds;
    const size_t *pair_ids;
    /* Quick: complete-pair mean reference fractions. Provisional: per frame. */
    double minimum_reference_fraction, maximum_reference_fraction, span_fraction;
    double saturation_raw, upper_fraction, minimum_span_fraction, maximum_pair_difference;
    char exposure_key[81];
    int exposure_hdu;
    const int (*rois)[4];
    size_t roi_count;
    mef_bpm_mask_encoding mask_encoding;
    int prior_active_only, binary_good_value;
    unsigned int reject_bits;
    char mask_registry[33];
    char readout_id[MEF_LAYOUT_TEXT];
    int bin_x, bin_y;
    int shared_cube, qc_requested, pair_consistency_passed, coverage_passed;
} mef_bpm_files_qc;
/* Header-only preflight: every request path/HDU/detector/config slot, selected
 * bias/prior map, readout/binning/unit/active geometry and EXPTIME/pair metadata.
 * Then reuse selected-plane loads and qualified typed numerical service.
 * Quick requires >=5 usable pairs at >=5 distinct times AND measured levels;
 * provisional requires >=2 distinct measured levels, explicitly labelled.
 * Cuts/span/pair tolerance supplied, never invented. Entire unusable frames are
 * explicitly recorded by original index; no mask is applied to electronic reads.
 * Caller freezes files/maps during the call. No filesystem discovery, cwd
 * change or product publication. Owned result outlives all borrowed inputs.
 * Pointer/error outputs start NULL, remain unchanged on error. */
mef_status mef_bpm_from_files(mef_context *, const mef_layout_map *const *, size_t,
    const char *detector, const mef_layout_map *bias, const mef_layout_map *prior,
    const mef_bpm_files_options *, mef_bpm_files_result **, mef_error **);
mef_status mef_bpm_from_cube(mef_context *,const mef_layout_map *const *,size_t,
    const char *,const mef_layout_map *,const mef_layout_map *,const mef_bpm_files_options *,
    const mef_detector_cube *,mef_bpm_files_result **,mef_error **);
void mef_bpm_files_result_destroy(mef_bpm_files_result *);
const mef_bpm_result *mef_bpm_files_result_service(const mef_bpm_files_result *);
const mef_bpm_files_qc *mef_bpm_files_result_qc(const mef_bpm_files_result *);
#endif
