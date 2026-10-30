/* Internal legacy arithmetic boundary. Not an installed API. */
#ifndef MEF_BIAS_KERNEL_H
#define MEF_BIAS_KERNEL_H
#include "eclipse.h"
typedef struct {
    float average, sigma, low, high, median, stdev;
    int accepted, measured;
} mef_bias_statistics;
/* Consumes cube on success or failure. decisions, if supplied, has cube->np
 * entries. Statistics are stored with the legacy float conversions. */
image_t *mef_bias_stack(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions);
#endif
