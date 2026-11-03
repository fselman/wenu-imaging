/* Opt-in raw-plane admission, not a complete linearity recipe or stable ABI. */
#ifndef MEF_LINEARITY_SAMPLES_H
#define MEF_LINEARITY_SAMPLES_H
#include "mef_config.h"
#include "mef_bias_settings.h"
#include "detector_roi.h"
#include "image_handling.h"
#include "pixelmaps.h"
typedef struct {
    char asset_id[128], pair_id[64];
    int input_index, hdu; /* explicit original frame index, zero-based HDU */
    double seconds; /* positive header integration time; never grouped/rounded */
} mef_linearity_frame;
typedef struct {
    const mef_config *configuration;
    size_t configuration_detector;
    detector_joint_amplifier identity; /* one resolved amplifier plane per call */
    int amplifier_index; /* index in the SAME list used to bind input ROIs */
    int frames;
    const image_t *const *raw;
    const mef_linearity_frame *frame;
    const image_t *master_bias; /* active, scan-corrected, ADU */
    const unsigned char *bpm_flags; /* active unsigned 8-bit, 0 good */
    size_t bpm_count;
    unsigned int reject_bits; /* explicit; no polarity inference */
    const pixelmap *const *samples; /* optional active per-frame Eclipse 1=good */
    int rois;
    const detector_roi *roi; /* entire bound list; only selected amplifier used */
    double saturation_raw; /* finite positive physical raw ADU, >= rejects */
    size_t max_sites, max_observations; /* explicit software resource ceilings */
} mef_linearity_sample_input;
typedef struct {
    size_t outside_roi, bpm_excluded, sample_excluded, nonfinite, saturated, admitted;
} mef_linearity_population;
typedef enum { MEF_LINEARITY_NOISE_UNAVAILABLE=1 } mef_linearity_noise_state;
typedef struct {
    mef_allocator allocator;
    mef_config *configuration;
    mef_bias_settings scan;
    detector_joint_amplifier identity;
    int amplifier_index, width, height, frames, rois, sites, observations;
    mef_linearity_frame *frame;
    mef_linearity_population *population;
    detector_roi *roi; /* selected entries, result-local amplifier index zero */
    detector_joint_site *site; /* distinct admitted active pixels, row-major */
    detector_joint_observation *observation; /* frame order, then row-major */
    mef_linearity_noise_state noise_state; /* NO invented identity covariance */
    unsigned int reject_bits;
    int bpm_supplied;
    double saturation_raw;
} mef_linearity_sample_result;
/* Reuse existing mef_overscan_correction, image_getvig and image_sub_local on
 * private copies. Active BPM never touches electronic scans. Overlapping ROIs
 * select their UNION, never duplicate observations. Raw saturation is checked
 * before subtraction, including equality. Frame index/time/pair/asset/HDU are
 * retained without chronological sorting, pairing inference or lamp scaling.
 * Population exclusions have exclusive precedence: outside ROI, BPM, per-frame
 * selection, nonfinite, saturation, admitted. All active pixels are counted.
 * Scan reads must be finite. Geometry and finite master bias are mandatory.
 * Result owns metadata/configuration/ROIs/samples, not full input images/BPM.
 * Sites with no admitted observations are removed. Empty success is explicit
 * through zero counts; these samples have no noise factor and must NOT be sent
 * to the joint fitter until a valid absolute noise/covariance model is attached.
 * One resolved amplifier plane only: no implicit multi-amplifier splitting or
 * raw FITS/HDU resolution. No I/O, product publication or reentrancy claim.
 * *out starts NULL. Failure leaves output/borrowed inputs unchanged.
 * Optional allocator covers service owners; Eclipse internals use qfits.
 */
mef_status mef_linearity_samples(const mef_linearity_sample_input *,
    const mef_allocator *, mef_linearity_sample_result **out);
void mef_linearity_samples_destroy(mef_linearity_sample_result *);
#endif
