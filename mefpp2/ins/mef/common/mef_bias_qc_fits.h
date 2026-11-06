/* Additive bias-scalar/1 header serializer. No pixel processing. */
#ifndef MEF_BIAS_QC_FITS_H
#define MEF_BIAS_QC_FITS_H
#include "mef_product_qc.h"
struct qfits_header;
/* On success returns a private header of additions only. Never mutates legacy
 * cards. Output must initially be NULL; caller destroys it. Length/collision/
 * unknown-code/nonfinite failures leave output NULL. Archive may be incomplete
 * for later detectors; selected detector must already be populated. */
int mef_bias_qc_fits_header(const mef_product_qc *, size_t,
    struct qfits_header **, char *, size_t);
#endif
