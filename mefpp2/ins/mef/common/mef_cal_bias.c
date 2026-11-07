#include "mef_cal_bias.h"
#include "mef_bias_settings.h"
#include "mef_bias_kernel.h"
#include "mefp_lib.h"
#include <float.h>
#include <limits.h>

struct mef_bias_result {
    mef_allocator allocator;
    image_t *signal;
    mef_request *request;
    mef_bias_qc qc;
    mef_bias_measurements measurements;
};

static void release(const mef_allocator *allocator, const void *pointer)
{
    if (pointer != NULL) allocator->release(allocator->user, (void *)pointer);
}
void mef_bias_result_destroy(mef_bias_result *result)
{
    mef_allocator a;
    if (result == NULL) return;
    a = result->allocator;
    image_del(result->signal);
    mef_request_destroy(result->request);
    release(&a, result->qc.scan_median);
    release(&a, result->qc.scan_stdev);
    release(&a, result->qc.accepted);
    release(&a, result->measurements.frames);
    pixelmap_del((pixelmap *)result->measurements.high_offset_flags);
    release(&a, result);
}
const image_t *mef_bias_result_signal(const mef_bias_result *result)
{
    return result == NULL ? NULL : result->signal;
}
const mef_bias_qc *mef_bias_result_qc(const mef_bias_result *result)
{
    return result == NULL ? NULL : &result->qc;
}
const mef_request *mef_bias_result_request(const mef_bias_result *result)
{
    return result == NULL ? NULL : result->request;
}
const mef_bias_measurements *mef_bias_result_measurements(const mef_bias_result *result)
{
    return result == NULL || result->measurements.frames == NULL ? NULL : &result->measurements;
}
static int finite_value(double value)
{
    return value == value && value >= -DBL_MAX && value <= DBL_MAX;
}
static int interval(const int *pair, int width)
{
    return pair[0] >= 1 && pair[1] >= pair[0] && pair[1] <= width;
}
static mef_status validate(mef_context *context, const mef_bias_input *input,
    mef_bias_settings *settings, const mef_bias_measurement_options *options)
{
    const mef_request_spec *request;
    const mef_resolved_request_spec *resolved;
    size_t i, j, pixels;
    int width, height, scan_width;
    if (context == NULL || input == NULL || input->frames == NULL ||
        input->count == 0 || input->count > INT_MAX ||
        input->count > (size_t)-1 / sizeof(mef_bias_frame_measurements)) return MEF_ERR_INPUT;
    resolved = mef_request_resolved_view(mef_context_request(context));
    if (resolved == NULL) return MEF_ERR_INPUT;
    request = &resolved->request;
    if (request->operation != MEF_OP_CAL_BIAS || request->operation_version != 1 ||
        request->input_count != input->count) return MEF_ERR_INPUT;
    if (resolved->bpm_selection_count != 1) return MEF_ERR_UNSUPPORTED;
    if (options == NULL || options->bpm == NULL) {
        if (request->calibration_count != 0 ||
            resolved->bpm_selections[0].state != MEF_BPM_OMITTED) return MEF_ERR_UNSUPPORTED;
    } else {
        if (request->calibration_count != 1 || resolved->calibration_roles[0] != MEF_CAL_BPM ||
            resolved->bpm_selections[0].state != MEF_BPM_SELECTED) return MEF_ERR_UNSUPPORTED;
    }
    if (options != NULL && ((options->with_mad != 0 && options->with_mad != 1) ||
        (options->ron_pair_set != 0 && options->ron_pair_set != 1) ||
        (options->bpm_active_only != 0 && options->bpm_active_only != 1) ||
        (options->bpm_active_only && options->bpm == NULL) ||
        !finite_value(options->high_sigma) || options->high_sigma <= 0.0 ||
        (options->ron_pair_set && (options->ron_first >= input->count ||
        options->ron_second >= input->count || options->ron_first == options->ron_second ||
        !strcmp(request->inputs[options->ron_first].resolved_path,
                request->inputs[options->ron_second].resolved_path)))))
        return MEF_ERR_INPUT;
    if (options && ((options->ron_clip_enabled != 0 && options->ron_clip_enabled != 1) ||
        (options->ron_clip_enabled && (!options->ron_pair_set ||
        !finite_value(options->ron_clip.sigma_low) || options->ron_clip.sigma_low <= 0 ||
        !finite_value(options->ron_clip.sigma_high) || options->ron_clip.sigma_high <= 0 ||
        options->ron_clip.max_iterations < 1 || options->ron_clip.max_iterations > 1000)))) return MEF_ERR_INPUT;
    if (mef_config_bias_settings(mef_context_config(context),
            input->configuration_detector, settings) != MEF_OK)
        return MEF_ERR_CONFIG;
    if (settings->minimum_frames < 3 || !finite_value(settings->kappa) ||
        settings->kappa < 0.0 || settings->rejection[0] < 0 ||
        settings->rejection[1] < 0) return MEF_ERR_CONFIG;
    if (input->count < (size_t)settings->minimum_frames) return MEF_ERR_INPUT;
    if (input->frames[0] == NULL) return MEF_ERR_INPUT;
    width = input->frames[0]->lx;
    height = input->frames[0]->ly;
    if (width <= 0 || height <= 0 || width > MAX_COLUMN_NUMBER ||
        height > MAX_LINE_NUMBER || width > INT_MAX / height)
        return MEF_ERR_INPUT;
    if (!interval(settings->trim, width) ||
        !interval(settings->trim + 2, height) ||
        settings->trim[0] == settings->trim[1] ||
        settings->trim[2] == settings->trim[3]) return MEF_ERR_CONFIG;
    scan_width = 0;
    if (settings->use_prescan) {
        if (!interval(settings->prescan, width)) return MEF_ERR_CONFIG;
        scan_width += settings->prescan[1] - settings->prescan[0] + 1;
    }
    if (settings->use_overscan) {
        if (!interval(settings->overscan, width)) return MEF_ERR_CONFIG;
        scan_width += settings->overscan[1] - settings->overscan[0] + 1;
    }
    if (settings->rejection[0] >= scan_width ||
        settings->rejection[1] >= scan_width - settings->rejection[0])
        return MEF_ERR_CONFIG;
    pixels = (size_t)width * (size_t)height;
    for (i = 0; i < input->count; ++i) {
        if (strcmp(request->inputs[i].detector_id, request->inputs[0].detector_id))
            return MEF_ERR_UNSUPPORTED;
        /* M4: the caller supplies the same validated plane for primary or MEF
         * storage. Numerical validation must not depend on the file's HDU. */
        if (input->frames[i] == NULL || input->frames[i]->data == NULL ||
            input->frames[i]->lx != width || input->frames[i]->ly != height)
            return MEF_ERR_INPUT;
        for (j = 0; j < pixels; ++j)
            if (!finite_value(input->frames[i]->data[j])) return MEF_ERR_INPUT;
    }
    if (options != NULL && options->bpm != NULL) {
        const pixelmap *map;
        map = options->bpm;
        if (map->data == NULL || map->lx != width || map->ly != height) return MEF_ERR_INPUT;
        for (j = 0; j < pixels; ++j)
            if (map->data[j] != PIXELMAP_0 && map->data[j] != PIXELMAP_1) return MEF_ERR_INPUT;
    }
    return MEF_OK;
}

mef_status mef_cal_bias(mef_context *context, const mef_bias_input *input,
    mef_bias_result **out, mef_error **error)
{
    return mef_cal_bias_measurements(context, input, NULL, out, error);
}
mef_status mef_cal_bias_measurements(mef_context *context, const mef_bias_input *input,
    const mef_bias_measurement_options *options, mef_bias_result **out, mef_error **error)
{
    pixelmap *active_map;
    const pixelmap *raw_map;
    mef_bias_frame_measurements *frame_qc;
    mef_bias_measurements *measurement;
    int zone[4], x, y;
    size_t position;
    const mef_allocator *a;
    const mef_resolved_request_spec *resolved;
    mef_bias_settings settings;
    mef_bias_statistics stats;
    mef_bias_result *pending;
    mef_status status;
    mef_bb work;
    mef_ccd detector;
    cube_t *cube;
    image_t *cropped;
    char **names;
    size_t i;
    const char *detail;
    detail = "Invalid or unsupported bias request, image data or geometry";
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL))
        return MEF_ERR_INPUT;
    pending = NULL;
    frame_qc = NULL;
    active_map = NULL;
    raw_map = options == NULL ? NULL : options->bpm;
    cube = NULL;
    names = NULL;
    a = mef_context_allocator(context);
    status = validate(context, input, &settings, options);
    if (status != MEF_OK) goto cleanup;
    resolved = mef_request_resolved_view(mef_context_request(context));

    /* Construct a safely destructible pending owner, before numerical work. */
    detail = "Cannot allocate pending bias result or QC arrays";
    status = MEF_ERR_MEMORY;
    pending = a->allocate(a->user, sizeof(*pending));
    if (pending == NULL) goto cleanup;
    memset(pending, 0, sizeof(*pending));
    pending->allocator = *a;
    pending->signal = NULL;
    pending->request = NULL;
    pending->qc.scan_median = NULL;
    pending->qc.scan_stdev = NULL;
    pending->qc.accepted = NULL;
    pending->qc.input_frames = input->count;
    pending->qc.variance_state = MEF_BIAS_VARIANCE_UNAVAILABLE_LEGACY;
    pending->qc.bpm_selection = MEF_BPM_OMITTED;
    pending->qc.bpm_applied = 0;
    pending->qc.ron_estimate_available = 0;
    pending->qc.scan_median = a->allocate(a->user, input->count * sizeof(float));
    pending->qc.scan_stdev = a->allocate(a->user, input->count * sizeof(float));
    pending->qc.accepted = a->allocate(a->user, input->count * sizeof(int));
    names = a->allocate(a->user, input->count * sizeof(*names));
    if (pending->qc.scan_median == NULL || pending->qc.scan_stdev == NULL ||
        pending->qc.accepted == NULL || names == NULL) goto cleanup;
    status = mef_request_create_resolved(resolved, a, &pending->request, error);
    if (status != MEF_OK) goto cleanup;

    if (options != NULL) {
        measurement = &pending->measurements;
        measurement->count = input->count;
        frame_qc = a->allocate(a->user, input->count * sizeof(*frame_qc));
        if (frame_qc == NULL) { status = MEF_ERR_MEMORY; goto cleanup; }
        memset(frame_qc, 0, input->count * sizeof(*frame_qc));
        measurement->frames = frame_qc;
        pending->qc.bpm_selection = resolved->bpm_selections[0].state;
        pending->qc.bpm_applied = raw_map != NULL;
        if (raw_map != NULL) {
            active_map = pixelmap_getvig((pixelmap *)raw_map, settings.trim[0],
                settings.trim[2], settings.trim[1], settings.trim[3]);
            if (active_map == NULL) { status = MEF_ERR_COMPUTATION; goto cleanup; }
        }
        if (options->ron_pair_set) {
            measurement->ron_first = options->ron_first;
            measurement->ron_second = options->ron_second;
            if (image_pair_stats_checked(input->frames[options->ron_first],
                input->frames[options->ron_second], raw_map, raw_map, settings.trim,
                options->with_mad, &measurement->raw_difference) != 0) {
                status = MEF_ERR_COMPUTATION; goto cleanup;
            }
            measurement->ron_stdev_available = measurement->raw_difference.stdev_available;
            measurement->ron_mad_available = measurement->raw_difference.mad_available;
            measurement->ron_stdev_adu = measurement->raw_difference.stdev / sqrt(2.0);
            measurement->ron_mad_adu = 1.4826 * measurement->raw_difference.mad / sqrt(2.0);
            pending->qc.ron_estimate_available = measurement->ron_stdev_available;
            if (options->ron_clip_enabled) {
                if (image_pair_stats_clipped_checked(input->frames[options->ron_first],
                    input->frames[options->ron_second],raw_map,raw_map,settings.trim,
                    &options->ron_clip,&measurement->clipped_difference) != 0) {
                    status = MEF_ERR_COMPUTATION; goto cleanup;
                }
                measurement->ron_clipped_available = measurement->clipped_difference.converged &&
                    measurement->clipped_difference.sample.stdev_available;
                measurement->ron_clipped_adu = measurement->clipped_difference.sample.stdev / sqrt(2.0);
            }
        }
    }

    /* This local legacy bridge supplies only fields read by overscan. Its
     * geometry is a copy: the historical helper temporarily changes indices. */
    memcpy(detector.prescan_x, settings.prescan, sizeof(settings.prescan));
    memcpy(detector.overscan_x, settings.overscan, sizeof(settings.overscan));
    memcpy(detector.trimreg, settings.trim, sizeof(settings.trim));
    work.ccd = &detector;
    work.xtnum = 1;
    work.nxts = 1;
    work.use_prescan = settings.use_prescan;
    work.use_overscan = settings.use_overscan;
    memcpy(work.scanrej, settings.rejection, sizeof(settings.rejection));
    work.bias_frame_name = names;
    work.bias_scan_median = (float *)pending->qc.scan_median;
    work.bias_scan_stdev = (float *)pending->qc.scan_stdev;
    detail = "Cannot copy or overscan-correct a selected bias image";
    status = MEF_ERR_COMPUTATION;
    cube = cube_new(input->frames[0]->lx, input->frames[0]->ly, (int)input->count);
    if (cube == NULL) goto cleanup;
    for (i = 0; i < input->count; ++i) {
        names[i] = (char *)resolved->request.inputs[i].resolved_path;
        cube->plane[i] = image_copy((image_t *)input->frames[i]);
        if (cube->plane[i] == NULL) goto cleanup;
        if (options != NULL) {
            frame_qc = (mef_bias_frame_measurements *)pending->measurements.frames + i;
            if (image_getstats_masked_checked(input->frames[i], raw_map, settings.trim,
                    options->with_mad, &frame_qc->active_raw) != 0) goto cleanup;
            zone[2] = settings.trim[2]; zone[3] = settings.trim[3];
            if (settings.use_prescan) {
                zone[0] = settings.prescan[0]; zone[1] = settings.prescan[1];
                if (image_getstats_masked_checked(input->frames[i], NULL, zone,
                    options->with_mad, &frame_qc->prescan) != 0) goto cleanup;
            }
            if (settings.use_overscan) {
                zone[0] = settings.overscan[0]; zone[1] = settings.overscan[1];
                if (image_getstats_masked_checked(input->frames[i], NULL, zone,
                    options->with_mad, &frame_qc->overscan) != 0) goto cleanup;
            }
        }
        /* Detector BPM does not apply to empty electronic scan reads. */
        cropped = mef_overscan_correction(cube->plane[i], &work, (int)i, "bias");
        if (cropped == NULL) goto cleanup;
        image_del(cube->plane[i]);
        cube->plane[i] = cropped;
        if (options != NULL && image_getstats_masked_checked(cropped, active_map, NULL,
            options->with_mad, &frame_qc->active_corrected) != 0) goto cleanup;
    }
    cube->lx = cube->plane[0]->lx;
    cube->ly = cube->plane[0]->ly;
    detail = "Bias rejection or median stacking failed; no result transferred";
    pending->signal = mef_bias_stack_masked(cube, settings.minimum_frames,
        settings.kappa, &stats, (int *)pending->qc.accepted, active_map);
    cube = NULL; /* Kernel always consumes the working cube. */
    if (pending->signal == NULL) goto cleanup;

    /* Structural postcondition, followed by explicit legacy-QC collection. */
    detail = "Bias result dimensions do not match the requested trim region";
    if (pending->signal->lx != settings.trim[1] - settings.trim[0] + 1 ||
        pending->signal->ly != settings.trim[3] - settings.trim[2] + 1)
        goto cleanup;
    pending->qc.frame_mean_average = stats.average;
    pending->qc.frame_mean_sigma = stats.sigma;
    pending->qc.rejection_low = stats.low;
    pending->qc.rejection_high = stats.high;
    pending->qc.product_median = stats.median;
    pending->qc.product_stdev = stats.stdev;
    pending->qc.accepted_frames = stats.accepted;
    if (options != NULL) {
        pixelmap *flags;
        measurement = &pending->measurements;
        if (image_getstats_masked_checked(pending->signal, active_map, NULL, options->with_mad,
                &measurement->master) != 0 ||
            image_getstats_masked_checked(pending->signal, NULL, NULL, options->with_mad,
                &measurement->master_unmasked) != 0) goto cleanup;
        if (measurement->master.mad_available) {
            measurement->high_offset_threshold = measurement->master.median +
                options->high_sigma * 1.4826 * measurement->master.mad;
            if (!finite_value(measurement->high_offset_threshold)) goto cleanup;
            flags = pixelmap_new(pending->signal->lx, pending->signal->ly);
            if (flags == NULL) goto cleanup;
            measurement->high_offset_flags = flags;
            measurement->high_offset_available = 1;
            measurement->high_offset_degenerate = measurement->master.mad == 0.0;
            for (y = 0; y < flags->ly; ++y) for (x = 0; x < flags->lx; ++x) {
                position = (size_t)y * (size_t)flags->lx + (size_t)x;
                flags->data[position] = pending->signal->data[position] >
                    measurement->high_offset_threshold ? PIXELMAP_1 : PIXELMAP_0;
                measurement->high_offset_count += flags->data[position] == PIXELMAP_1;
            }
            pixelmap_updatecount(flags);
        }
    }
    *out = pending;
    pending = NULL;
    status = MEF_OK;
cleanup:
    cube_del(cube);
    pixelmap_del(active_map);
    if (a != NULL) release(a, names);
    mef_bias_result_destroy(pending);
    if (status != MEF_OK && error != NULL && *error == NULL)
        (void)mef_error_create(status, detail, a, error);
    return status;
}
