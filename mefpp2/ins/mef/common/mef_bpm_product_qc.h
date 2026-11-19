/* Native BPM metadata adapter. The shared product writer owns ASDF I/O. */
#ifndef MEF_BPM_PRODUCT_QC_H
#define MEF_BPM_PRODUCT_QC_H
#include "mef_bpm_publish.h"
#include "mef_product_qc.h"
typedef struct mef_bpm_product_qc mef_bpm_product_qc;
/* Result, output path and publication options remain borrowed until destroy.
 * Call after FITS publication. Metadata is copied without loading image files,
 * fitting response, applying a mask, or selecting a different population. */
mef_bpm_product_qc *mef_bpm_product_qc_new(const mef_bpm_files_result *,
    const char *fits_path, const mef_bpm_publish_options *, char *, size_t);
const mef_product_qc *mef_bpm_product_qc_view(const mef_bpm_product_qc *);
void mef_bpm_product_qc_destroy(mef_bpm_product_qc *);
#endif
