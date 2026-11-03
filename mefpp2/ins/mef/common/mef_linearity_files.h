#ifndef MEF_LINEARITY_FILES_H
#define MEF_LINEARITY_FILES_H
#include "mef_linearity_samples.h"
#include "mef_layout.h"
typedef struct {
    const mef_layout_map *map;
    mef_image_ref reference;
    const char *pair_id;
    int input_index;
} mef_linearity_file_frame;
typedef enum { MEF_LINEARITY_MASK_OMITTED=1, MEF_LINEARITY_MASK_REASON8,
    MEF_LINEARITY_MASK_BINARY } mef_linearity_mask_encoding;
typedef struct {
    /* Numerical/geometry choices only. frames is count; raw/frame/master_bias/
     * bpm_flags/bpm_binary/samples must be NULL and bpm_count zero, because this
     * adapter loads them explicitly. No values are silently overwritten. */
    mef_linearity_sample_input sample;
    const mef_linearity_file_frame *input;
    const mef_layout_map *bias_map, *bpm_map;
    const mef_image_ref *bias_reference, *bpm_reference;
    mef_linearity_mask_encoding mask_encoding;
    int binary_good_value; /* required 0 or 1 only for binary; never inferred */
    const char *mask_registry; /* required for REASON8 */
    const char *exposure_key; /* full qfits keyword spelling */
    int exposure_hdu;
    double pair_time_tolerance; /* seconds, >=0, never exposure rounding */
    size_t max_loaded_pixels; /* sum of all raw/calibration plane pixels */
} mef_linearity_files_input;
typedef struct {
    mef_allocator allocator;
    mef_linearity_sample_result *samples;
    char **input_paths, *bias_path, *bpm_path;
    char *bias_asset_id, *bpm_asset_id;
    mef_bound_detector *input_binding, bias_binding, bpm_binding;
    int frames, exposure_hdu, bpm_supplied, binary_good_value;
    mef_linearity_mask_encoding mask_encoding;
    char exposure_key[81], mask_registry[33];
    double pair_time_tolerance;
    size_t max_loaded_pixels;
} mef_linearity_files_result;
/* Header preflight all bindings/units/readout/binning/active/config geometry,
 * explicit path/HDU references and exposure metadata before loading arrays.
 * Every declared pair must occur exactly twice with |time1-time2| <= explicit
 * tolerance. Preserve input order and exact header times; no adjacency, sorting,
 * lamp correction or scientific level/range acceptance is inferred.
 * Active bias/BPM only; legacy binary polarity is declared and converted through
 * the existing M4 loader. No reason bits are invented. Borrowed sources must be
 * frozen by caller; existing M4 source identity/load guards remain in force.
 * Reuse selected M4 loads, then the existing typed sample service. Result owns
 * source path/binding snapshots and samples, outliving input maps/configuration.
 * No uncertainty estimation, fit, product/ASDF publication or installation.
 * Return status; *out starts NULL and failures preserve it. No new reentrancy
 * or dependency-OOM claim. Allocator covers adapter and sample/snapshot owners. */
mef_status mef_linearity_from_files(const mef_linearity_files_input *,
    const mef_allocator *,mef_linearity_files_result **out);
void mef_linearity_files_destroy(mef_linearity_files_result *);
#endif
