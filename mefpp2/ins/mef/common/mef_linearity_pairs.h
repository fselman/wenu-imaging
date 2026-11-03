#ifndef MEF_LINEARITY_PAIRS_H
#define MEF_LINEARITY_PAIRS_H
#include "mef_linearity_samples.h"
#include "detector.h"
typedef struct {
    const mef_config *configuration;
    size_t configuration_detector;
    detector_joint_amplifier identity;
    int amplifier_index, frames, rois, with_mad;
    const image_t *const *raw;
    const mef_linearity_frame *frame;
    const image_t *raw_bias[2]; /* same RAW geometry/readout; NEVER overscan corrected */
    const char *raw_bias_asset[2];
    int raw_bias_hdu[2];
    const detector_roi *roi; /* bound active rectangles, selected amplifier only */
    const unsigned char *bpm_flags;
    size_t bpm_count;
    const pixelmap *bpm_binary; /* alternative explicit Eclipse 1=good */
    unsigned int reject_bits;
    double saturation_raw, pair_time_tolerance;
    size_t max_rows;
} mef_linearity_pairs_input;
typedef struct {
    detector_roi roi; /* active bounds, original amplifier index */
    int raw_zone[4];
    size_t bpm_excluded, saturated;
    image_sample_stats difference; /* bias-only population, not flat-selected */
    int ron_available, ron_mad_available;
    double ron_adu, ron_mad_adu;
} mef_linearity_bias_roi;
typedef struct {
    int roi, first, second; /* selected ROI index and original input ARRAY positions */
    size_t bpm_excluded, saturated; /* separate from kernel's derived selection */
    detector_gain_pair_result measurement;
    int variance_available, signal_available;
    double mean_signal, single_flat_variance, single_bias_variance; /* ADU, ADU^2 */
} mef_linearity_pair_row;
typedef struct {
    mef_allocator allocator;
    mef_config *configuration;
    detector_joint_amplifier identity;
    int amplifier_index, frames, rois, pairs;
    size_t configuration_detector, max_rows;
    size_t rows;
    mef_linearity_frame *frame;
    char raw_bias_asset[2][128];int raw_bias_hdu[2];
    mef_linearity_bias_roi *bias;
    mef_linearity_pair_row *row; /* pair first-appearance order, then configured ROI order */
    int bpm_supplied, bpm_binary_supplied, with_mad;
    unsigned int reject_bits;
    double saturation_raw, pair_time_tolerance;
} mef_linearity_pairs_result;
/* Measurement-only pass: reuse detector_gain_pair_checked and raw difference
 * stats on common four-plane populations. ROIs translate to RAW zones; no scan
 * correction, trimming, master subtraction, lamp normalization or new clipping.
 * Explicit two-member pairs need not be adjacent. All exact times/IDs retained.
 * Source raw-bias identities are shared across rows, never independent repeats.
 * Bias-only RON uses its own finite/BPM/saturation population, separately from
 * each flat-dependent gain population. Exclusion precedence BPM/nonfinite/sat.
 * Kernel bpm_excluded includes supplied BPM plus saturation selections; the row
 * retains their separate counts. Overlapping ROIs give correlated measurements,
 * not independent calibration points. No gain interval, pair-suitability cut,
 * variance curve interpolation, noise distribution or covariance is selected.
 * Gain AVAILABLE is arithmetic availability, not instrument acceptance.
 * Result owns metadata/configuration/table, borrowed pixels immutable. NULL/
 * occupied output fails intact. Allocator covers service/snapshot owners;
 * existing Eclipse temporary owners retain their qualified allocation contract. */
mef_status mef_linearity_measure_pairs(const mef_linearity_pairs_input *,
    const mef_allocator *,mef_linearity_pairs_result **out);
void mef_linearity_pairs_destroy(mef_linearity_pairs_result *);
#endif
