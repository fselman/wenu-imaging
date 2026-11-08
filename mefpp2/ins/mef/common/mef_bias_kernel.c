/* Select detector-local corrected frames and form their temporal median master.
 * Input is a private corrected cube in ADU; the optional active BPM selects
 * frame means and master statistics, not output pixels. Every return consumes
 * the cube; only a successful return transfers the new master to the caller.
 */
#include "mef_bias_kernel.h"

image_t *mef_bias_stack(cube_t *cube, int minimum_frames, double rejection_kappa,
    mef_bias_statistics *statistics, int *frame_decisions)
{
    return mef_bias_stack_masked(
        cube, minimum_frames, rejection_kappa, statistics, frame_decisions, NULL);
}

image_t *mef_bias_stack_masked(cube_t *cube, int minimum_frames, double rejection_kappa,
    mef_bias_statistics *statistics, int *frame_decisions, const pixelmap *active_mask)
{
    return mef_bias_stack_masked_opts(cube, minimum_frames, rejection_kappa, statistics,
        frame_decisions, active_mask, MEDIAN_EVEN_AVERAGE);
}

image_t *mef_bias_stack_masked_opts(cube_t *cube, int minimum_frames, double rejection_kappa,
    mef_bias_statistics *statistics, int *frame_decisions, const pixelmap *active_mask,
    median_even_handling median_mode)
{
    return mef_bias_stack_masked_diagnostic(cube, minimum_frames, rejection_kappa, statistics,
        frame_decisions, active_mask, median_mode, NULL);
}

image_t *mef_bias_stack_masked_diagnostic(cube_t *cube, int minimum_frames, double rejection_kappa,
    mef_bias_statistics *statistics, int *frame_decisions, const pixelmap *active_mask,
    median_even_handling median_mode, const mef_bias_diagnostic *diagnostic)
{
    image_sample_stats active_statistics;
    double *frame_means_adu;
    int *admission_flags;
    double mean_level_adu, frame_mean_sigma_adu, rejection_low_adu, rejection_high_adu;
    int frame_index, frame_count, accepted_count;
    image_t *master_bias;
    pixelvalue master_median;
    frame_means_adu = NULL;
    admission_flags = NULL;
    master_bias = NULL;
    if (statistics == NULL) {
        cube_del(cube);
        return NULL;
    }
    statistics->measured = 0;
    statistics->zero_spread = 0;
    statistics->accepted = 0;
    if (cube == NULL || cube->np < minimum_frames ||
        (median_mode != MEDIAN_EVEN_AVERAGE && median_mode != MEDIAN_EVEN_LOWER)) {
        goto cleanup;
    }
    frame_count = cube->np;
    frame_means_adu = malloc((size_t)frame_count * sizeof(*frame_means_adu));
    admission_flags = malloc((size_t)frame_count * sizeof(*admission_flags));
    if (frame_means_adu == NULL || admission_flags == NULL) {
        goto cleanup;
    }
    /* [BIAS-FRAME-SELECTION]
     * Form one rejection interval from all submitted corrected frame means.
     */
    mean_level_adu = 0.00;
    for (frame_index = 0; frame_index < frame_count; ++frame_index) {
        if (active_mask == NULL) {
            frame_means_adu[frame_index] = image_getmean(cube->plane[frame_index]);
        } else {
            if (image_getstats_masked_checked(
                    cube->plane[frame_index], active_mask, NULL, 0, &active_statistics) != 0 ||
                !active_statistics.level_available) {
                goto cleanup;
            }
            frame_means_adu[frame_index] = active_statistics.mean;
        }
        mean_level_adu += frame_means_adu[frame_index];
    }
    mean_level_adu /= (double)frame_count;

    frame_mean_sigma_adu = 0.0;
    for (frame_index = 0; frame_index < frame_count; ++frame_index) {
        frame_mean_sigma_adu += (frame_means_adu[frame_index] - mean_level_adu) *
                                (frame_means_adu[frame_index] - mean_level_adu);
    }
    frame_mean_sigma_adu /= (double)(frame_count - 1);
    frame_mean_sigma_adu = sqrt(frame_mean_sigma_adu);
    rejection_low_adu = mean_level_adu - rejection_kappa * frame_mean_sigma_adu;
    rejection_high_adu = mean_level_adu + rejection_kappa * frame_mean_sigma_adu;
    statistics->average = mean_level_adu;
    statistics->sigma = frame_mean_sigma_adu;
    statistics->low = rejection_low_adu;
    statistics->high = rejection_high_adu;
    statistics->measured = 1;
    if (frame_mean_sigma_adu == 0.0) {
        /* A collapsed strict interval cannot admit any frame. Stop explicitly,
         * before stacking, rather than silently admitting equal frame means. */
        statistics->zero_spread = 1;
        e_error("Bias zero-spread failure: detector [%s], %d frame means, sigma=0 ADU; "
                "cannot form a nonzero rejection interval; processing stopped before stacking",
            diagnostic != NULL && diagnostic->detector_id != NULL && *diagnostic->detector_id
                ? diagnostic->detector_id
                : "unspecified",
            frame_count);
        for (frame_index = 0; frame_index < frame_count; ++frame_index) {
            if (frame_decisions != NULL) {
                frame_decisions[frame_index] = 0;
            }
            e_error("Bias zero-spread input %d [%s]: corrected mean=%.17g ADU", frame_index + 1,
                diagnostic != NULL && diagnostic->input_names != NULL &&
                        diagnostic->input_names[frame_index] != NULL
                    ? diagnostic->input_names[frame_index]
                    : "name unavailable",
                frame_means_adu[frame_index]);
        }
        goto cleanup;
    }

    /* Exact endpoints remain excluded, even when the interval is very narrow. */
    accepted_count = 0;
    for (frame_index = 0; frame_index < frame_count; ++frame_index) {
        admission_flags[frame_index] = frame_means_adu[frame_index] > rejection_low_adu &&
                                       frame_means_adu[frame_index] < rejection_high_adu;
        if (frame_decisions != NULL) {
            frame_decisions[frame_index] = admission_flags[frame_index];
        }
        accepted_count += admission_flags[frame_index];
    }
    if (accepted_count < minimum_frames) {
        goto cleanup;
    }
    if (accepted_count < frame_count && cube_reject_planes(&cube, admission_flags) != 0) {
        goto cleanup;
    }
    /* [BIAS-TEMPORAL-STACK]
     * Stack every active coordinate, including BPM-excluded output pixels.
     */
    master_bias = cube_avg_median_opts(cube, median_mode);
    if (master_bias == NULL) {
        goto cleanup;
    }
    if (image_getmedian_checked(master_bias, &master_median) != 0) {
        image_del(master_bias);
        master_bias = NULL;
        goto cleanup;
    }
    statistics->median = master_median;
    statistics->stdev = image_getstdev(master_bias);
    if (active_mask != NULL) {
        if (image_getstats_masked_checked(master_bias, active_mask, NULL, 0, &active_statistics) !=
                0 ||
            !active_statistics.stdev_available) {
            image_del(master_bias);
            master_bias = NULL;
            goto cleanup;
        }
        statistics->median = active_statistics.median;
        statistics->stdev = active_statistics.stdev;
    }
    statistics->accepted = accepted_count;
cleanup:
    if (frame_means_adu != NULL) {
        free(frame_means_adu);
    }
    if (admission_flags != NULL) {
        free(admission_flags);
    }
    cube_del(cube);
    return master_bias;
}
