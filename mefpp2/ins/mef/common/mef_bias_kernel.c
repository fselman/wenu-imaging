/* Bias branch extracted from mef_build_cal, retaining arithmetic/order and
 * strict rejection endpoints. Eclipse retains its own allocation policy. */
#include "mef_bias_kernel.h"

image_t *mef_bias_stack(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions)
{
    double *means;
    int *valid;
    double average, sigma, low, high;
    int i, count, kept;
    image_t *stacked;
    pixelvalue median;
    means = NULL;
    valid = NULL;
    stacked = NULL;
    if (statistics == NULL) { cube_del(cube); return NULL; }
    statistics->measured = 0;
    if (cube == NULL || cube->np < minimum) goto cleanup;
    count = cube->np;
    means = malloc((size_t)count * sizeof(*means));
    valid = malloc((size_t)count * sizeof(*valid));
    if (means == NULL || valid == NULL) goto cleanup;
    average = 0.00;
    for (i = 0; i < count; ++i) {
        means[i] = image_getmean(cube->plane[i]);
        average += means[i];
    }
    average /= (double)count;
    sigma = 0.0;
    for (i = 0; i < count; ++i)
        sigma += (means[i] - average) * (means[i] - average);
    sigma /= (double)(count - 1);
    sigma = sqrt(sigma);
    low = average - kappa * sigma;
    high = average + kappa * sigma;
    statistics->average = average;
    statistics->sigma = sigma;
    statistics->low = low;
    statistics->high = high;
    statistics->measured = 1;
    kept = 0;
    for (i = 0; i < count; ++i) {
        valid[i] = means[i] > low && means[i] < high;
        if (decisions != NULL) decisions[i] = valid[i];
        kept += valid[i];
    }
    if (kept < minimum) goto cleanup;
    if (kept < count && cube_reject_planes(&cube, valid) != 0) goto cleanup;
    stacked = cube_avg_median(cube);
    if (stacked == NULL) goto cleanup;
    if (image_getmedian_checked(stacked, &median) != 0) {
        image_del(stacked); stacked = NULL; goto cleanup;
    }
    statistics->median = median;
    statistics->stdev = image_getstdev(stacked);
    statistics->accepted = kept;
cleanup:
    free(means);
    free(valid);
    cube_del(cube);
    return stacked;
}
