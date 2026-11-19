#ifndef MEF_BIAS_PRODUCT_QC_H
#define MEF_BIAS_PRODUCT_QC_H
#include "mef_bias_files.h"
#include "mef_bias_settings.h"
#include "mef_product_paths.h"
#include "mef_product_qc.h"
typedef struct mef_bias_product_qc mef_bias_product_qc;
/* Archive copies numerical QC before each result/image is released. Paths,
 * configuration and identity strings stay borrowed until archive destruction.
 * No Python/JSON handoff, pixel estimator or input discovery. */
mef_bias_product_qc *mef_bias_product_qc_new(const mef_config *,
    const mef_product_paths *, const char *start, const char *revision,
    const char *const *inputs, size_t input_count, size_t detector_count);
int mef_bias_product_qc_add(mef_bias_product_qc *, size_t output_index,
    const char *id, const char *amplifier, const char *readout,
    size_t configuration_detector, int bin_x, int bin_y,
    const mef_bias_result *, const mef_bias_measurement_options *,
    const mef_bias_settings *, int raw_rows, const char *bpm_path,
    int bpm_hdu, int bpm_good_value);
/* Capture selected final FITS headers after assembly, before ASDF publication. */
int mef_bias_product_qc_headers(mef_bias_product_qc *, const char *const *, size_t,
    const char *const *, size_t, const char *, const char *, char *, size_t);
int mef_bias_product_qc_input_list(mef_bias_product_qc *,const char *);
int mef_bias_product_qc_check(mef_bias_product_qc *, char *, size_t);
const mef_product_qc *mef_bias_product_qc_view(const mef_bias_product_qc *);
int mef_bias_product_qc_write(mef_bias_product_qc *, char *, size_t);
void mef_bias_product_qc_destroy(mef_bias_product_qc *);
#endif
