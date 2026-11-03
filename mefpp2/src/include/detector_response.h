/* Checked response adapter; existing Eclipse fitters remain authoritative. */
#ifndef ECLIPSE_DETECTOR_RESPONSE_H
#define ECLIPSE_DETECTOR_RESPONSE_H
#include "detector.h"
#include "pixelmaps.h"
#include <stddef.h>

typedef struct {
    int proportional; /* 0 robust, 1 median ratio; not conversion gain. */
    const pixelmap *reference; /* 1=good. Never excludes a pixel from fitting. */
    const pixelmap *const *samples; /* Optional one 1=usable map per plane. */
    const int (*rois)[4]; /* Union, FITS inclusive xmin,xmax,ymin,ymax. */
    size_t roi_count; /* Zero means whole active plane; rois must then be NULL. */
    double low, high; /* Strict normalized response acceptance endpoints. */
} detector_response_options;

typedef struct {
    image_t *slope, *intercept, *residual, *normalized;
    pixelmap *valid; /* 1=numerically available, not a defect selection. */
    int *sample_count;
    unsigned char *fit_state; /* 0=unavailable, 1=fit, 2=legacy LS fallback. */
    unsigned char *reasons; /* New response bits only: 4=low, 8=high. */
    double *reference_levels;
    int plane_count, proportional;
    double normalization;
} detector_response_result;

/* Corrected active ADU cube and options borrowed, never mutated. ROI union and
 * reference map select medians/normalization only; all pixels are evaluated.
 * samples select per-pixel measurements, e.g. precomputed saturation coverage.
 * Finite data only contribute; no clipping. Empty reference planes fail.
 * Reuses median_pixelvalue (legacy even convention), fit_slope_robust and
 * fit_proportional, with the legacy float stores and division. Robust needs
 * >=2 distinct x; proportional rejects near-zero x. Insufficient per-pixel
 * coverage has valid=0/reasons=0, never certification or an invented reason.
 * Residual is robust mean absolute ADU (or -1 fallback), proportional MSE ADU^2.
 * Return 0 on success, -1 on invalid/degenerate/allocation/computation error.
 * out must start NULL; untouched on error. No I/O or reentrancy/OOM qualification
 * beyond the checked boundary; existing fitters retain their allocation policy.
 */
int cube_response_checked(const cube_t *, const detector_response_options *,
    detector_response_result **out);
void detector_response_result_del(detector_response_result *);
#endif
