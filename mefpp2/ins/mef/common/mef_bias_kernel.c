/* Bias branch extracted from mef_build_cal, retaining arithmetic/order and
 * strict rejection endpoints. Eclipse retains its own allocation policy. */
#include "mef_bias_kernel.h"

image_t *mef_bias_stack(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions)
{
    return mef_bias_stack_masked(cube, minimum, kappa, statistics, decisions, NULL);
}
image_t *mef_bias_stack_masked(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions, const pixelmap *map)
{
    return mef_bias_stack_masked_opts(cube,minimum,kappa,statistics,decisions,map,MEDIAN_EVEN_AVERAGE);
}
image_t *mef_bias_stack_masked_opts(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions, const pixelmap *map,
    median_even_handling mode)
{
    return mef_bias_stack_masked_diagnostic(cube, minimum, kappa, statistics,
        decisions, map, mode, NULL);
}
image_t *mef_bias_stack_masked_diagnostic(cube_t *cube, int minimum, double kappa,
    mef_bias_statistics *statistics, int *decisions, const pixelmap *map,
    median_even_handling mode, const mef_bias_diagnostic *diagnostic)
{
    image_sample_stats measured;
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
    statistics->zero_spread = 0;
    statistics->accepted = 0;
    if (cube == NULL || cube->np < minimum || (mode != MEDIAN_EVEN_AVERAGE && mode != MEDIAN_EVEN_LOWER)) goto cleanup;
    count = cube->np;
    means = malloc((size_t)count * sizeof(*means));
    valid = malloc((size_t)count * sizeof(*valid));
    if (means == NULL || valid == NULL) goto cleanup;
    average = 0.00;
    for (i = 0; i < count; ++i) {
        if (map == NULL) means[i] = image_getmean(cube->plane[i]);
        else {
            if (image_getstats_masked_checked(cube->plane[i], map, NULL, 0, &measured) != 0 ||
                !measured.level_available) goto cleanup;
            means[i] = measured.mean;
        }
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
    if (sigma == 0.0) {
        /* A collapsed strict interval cannot admit any frame. Stop explicitly,
         * before stacking, rather than silently admitting equal frame means. */
        statistics->zero_spread = 1;
        e_error("Bias zero-spread failure: detector [%s], %d frame means, sigma=0 ADU; "
            "cannot form a nonzero rejection interval; processing stopped before stacking",
            diagnostic != NULL && diagnostic->detector_id != NULL && *diagnostic->detector_id ?
                diagnostic->detector_id : "unspecified", count);
        for (i = 0; i < count; ++i) {
            if (decisions != NULL) decisions[i] = 0;
            e_error("Bias zero-spread input %d [%s]: corrected mean=%.17g ADU", i + 1,
                diagnostic != NULL && diagnostic->input_names != NULL &&
                diagnostic->input_names[i] != NULL ? diagnostic->input_names[i] :
                    "name unavailable", means[i]);
        }
        goto cleanup;
    }
    kept = 0;
    for (i = 0; i < count; ++i) {
        valid[i] = means[i] > low && means[i] < high;
        if (decisions != NULL) decisions[i] = valid[i];
        kept += valid[i];
    }
    if (kept < minimum) goto cleanup;
    if (kept < count && cube_reject_planes(&cube, valid) != 0) goto cleanup;
    stacked = cube_avg_median_opts(cube,mode);
    if (stacked == NULL) goto cleanup;
    if (image_getmedian_checked(stacked, &median) != 0) {
        image_del(stacked); stacked = NULL; goto cleanup;
    }
    statistics->median = median;
    statistics->stdev = image_getstdev(stacked);
    if (map != NULL) {
        if (image_getstats_masked_checked(stacked, map, NULL, 0, &measured) != 0 ||
            !measured.stdev_available) { image_del(stacked); stacked = NULL; goto cleanup; }
        statistics->median = measured.median;
        statistics->stdev = measured.stdev;
    }
    statistics->accepted = kept;
cleanup:
    if (means != NULL) free(means);
    if (valid != NULL) free(valid);
    cube_del(cube);
    return stacked;
}
