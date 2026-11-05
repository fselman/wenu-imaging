/* Internal C17 preparation services. No file discovery, fitting or publication. */
#ifndef MEF_LINEARITY_PREPARE_H
#define MEF_LINEARITY_PREPARE_H
#include "mef_linearity_pairs.h"
typedef enum { MEF_PREPARE_BIAS=1, MEF_PREPARE_FLAT=2 } mef_prepare_role;
typedef struct {
    const image_t *raw;
    const image_t *master; /* required only for FLAT: active, scan-corrected ADU */
    mef_bias_settings settings; /* resolved from detector + processing TOMLs */
    mef_prepare_role role;
    size_t max_working_pixels; /* raw + copy + active + borrowed master */
} mef_linearity_prepare_frame_input;
typedef struct {
    mef_allocator allocator;
    image_t *active; /* owned: corrected bias, or corrected/master-subtracted flat */
    pixelvalue *row_correction; /* raw-row order, before QC median sorting */
    size_t rows;
    mef_bias_settings settings;
    mef_prepare_role role;
} mef_linearity_prepare_frame_result;
/* Borrowed inputs never change. Output starts NULL and stays NULL on error.
 * Reuses the legacy correction on a private copy, with native staged rounding.
 * No active BPM in electronic scans; nonfinite scan samples fail before mutation.
 * Existing Eclipse image/scratch allocations retain their own allocator policy. */
mef_status mef_linearity_prepare_frame(const mef_linearity_prepare_frame_input *,
    const mef_allocator *, mef_linearity_prepare_frame_result **);
void mef_linearity_prepare_frame_destroy(mef_linearity_prepare_frame_result *);
typedef struct {
    image_sample_stats first, second, difference; /* same common raw population */
} mef_linearity_prepared_roi;
typedef struct {
    mef_allocator allocator;
    mef_linearity_pairs_result *raw; /* unchanged raw diagnostics + identities */
    mef_linearity_prepared_roi *row; /* corresponding pair/ROI order */
    pixelvalue *row_correction; /* frames then the 2 raw biases, raw-row order */
    size_t trace_rows;
    mef_bias_settings settings;
} mef_linearity_prepared_result;
/* Master stage/source agreement is an explicit FILE/recipe admission obligation,
 * not inferred from image values. This service validates dimensions/finite master.
 * Corrects both raw biases for trace evidence; preserves RAW RON/gain definitions.
 * Corrected flat pairs are measured on exactly the raw four-plane population.
 * No noise/covariance estimate or new gain calibration is implied. */
mef_status mef_linearity_prepare_pairs(const mef_linearity_pairs_input *,
    const image_t *master, size_t max_working_pixels,
    const mef_allocator *, mef_linearity_prepared_result **);
void mef_linearity_prepared_destroy(mef_linearity_prepared_result *);
#endif
