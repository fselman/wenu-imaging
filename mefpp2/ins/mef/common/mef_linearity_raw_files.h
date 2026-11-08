#ifndef MEF_LINEARITY_RAW_FILES_H
#define MEF_LINEARITY_RAW_FILES_H
#include "mef_linearity_files.h"
typedef struct {
    /* Metadata/choices only: all borrowed image/frame/mask/bias pointers in
     * pairs must be NULL, bpm_count/raw_bias_hdu zero. No master is needed. */
    mef_linearity_pairs_input pairs;
    const mef_linearity_file_frame *input;
    const mef_layout_map *raw_bias_map[2], *bpm_map;
    const mef_image_ref *raw_bias_reference[2], *bpm_reference;
    mef_linearity_mask_encoding mask_encoding;
    int binary_good_value;
    const char *mask_registry, *exposure_key;
    int exposure_hdu;
    size_t max_loaded_pixels;
} mef_linearity_raw_files_input;
/* RAW measurement only: preflight bindings, masks, exact times/pairs and budget,
 * then reuse the existing selected-plane loaders and raw pair service. Never call the
 * corrected sample service; no overscan/master or dense pixel-observation owner.
 * At most this one detector's selected planes are loaded. Budget counts flat,
 * raw bias and optional BPM pixels, not total process bytes or dependency scratch.
 * Returned ordinary files owner has pairs non-NULL and samples/bias_path NULL;
 * it owns resolved paths and binding snapshots and uses the existing destructor.
 * Caller freezes sources, classifies the two biases and verifies readout claims.
 * No inferred choices, source locking, atomic publication or fitted calibration.
 * NULL/occupied output fails unchanged, also on partial allocation/load failure. */
mef_status mef_linearity_raw_from_files(const mef_linearity_raw_files_input *,
    const mef_allocator *, mef_linearity_files_result **);
#endif
