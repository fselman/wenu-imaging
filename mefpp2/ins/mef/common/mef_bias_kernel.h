/* Internal legacy arithmetic boundary. Not an installed API. */
#ifndef MEF_BIAS_KERNEL_H
#define MEF_BIAS_KERNEL_H
#include "eclipse.h"
typedef struct {
    float average, sigma, low, high, median, stdev;
    int accepted, measured;
    int zero_spread; /* Exact double-precision test; never infer from float sigma. */
} mef_bias_statistics;
/* Borrowed for the duration of one call; NULL names fall back to indices. */
typedef struct {
    const char *detector_id;
    char *const *input_names;
} mef_bias_diagnostic;
/* Consumes cube on success or failure. decisions, if supplied, has cube->np
 * entries. Statistics are stored with the legacy float conversions. */
image_t *mef_bias_stack(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions);
/* Same stack arithmetic; explicit active-area mask selects frame means and
 * product statistics, not output pixels. Consumes cube on every return. */
image_t *mef_bias_stack_masked(cube_t *, int, double, mef_bias_statistics *, int *, const pixelmap *);
image_t *mef_bias_stack_masked_opts(cube_t *, int, double, mef_bias_statistics *, int *,
    const pixelmap *, median_even_handling);
/* Same arithmetic and ownership; reports exact zero-spread failure using the
 * supplied identities. Existing entry points use a NULL diagnostic context. */
image_t *mef_bias_stack_masked_diagnostic(cube_t *, int, double, mef_bias_statistics *,
    int *, const pixelmap *, median_even_handling, const mef_bias_diagnostic *);
#endif
