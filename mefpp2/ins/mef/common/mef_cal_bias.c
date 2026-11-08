/* Build one detector's bias master from borrowed raw images and a resolved request.
 * Validate bindings/geometry, measure optional raw QC, correct private frame
 * copies, select/stack them, and measure the master. A pending result owns every
 * allocation until success; failure returns no partial result to the caller.
 */

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

static void release_owned(const mef_allocator *allocator, const void *pointer)
{
    if (pointer != NULL) {
        allocator->release(allocator->user, (void *)pointer);
    }
}

void mef_bias_result_destroy(mef_bias_result *result)
{
    mef_allocator allocator;
    if (result == NULL) {
        return;
    }
    allocator = result->allocator;
    image_del(result->signal);
    mef_request_destroy(result->request);
    release_owned(&allocator, result->qc.scan_median);
    release_owned(&allocator, result->qc.scan_stdev);
    release_owned(&allocator, result->qc.accepted);
    release_owned(&allocator, result->measurements.frames);
    pixelmap_del((pixelmap *)result->measurements.high_offset_flags);
    release_owned(&allocator, result);
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

static int is_finite_level(double value)
{
    return value == value && value >= -DBL_MAX && value <= DBL_MAX;
}

static int valid_interval(const int *pair, int width)
{
    return pair[0] >= 1 && pair[1] >= pair[0] && pair[1] <= width;
}

static mef_status validate_bias_inputs(mef_context *context, const mef_bias_input *input,
    mef_bias_settings *bias_settings, const mef_bias_measurement_options *options)
{
    const mef_request_spec *request;
    const mef_resolved_request_spec *resolved;
    size_t frame_index, pixel_index, pixels;
    int width, height, scan_width;
    if (context == NULL || input == NULL || input->frames == NULL || input->count == 0 ||
        input->count > INT_MAX || input->count > (size_t)-1 / sizeof(mef_bias_frame_measurements)) {
        return MEF_ERR_INPUT;
    }
    resolved = mef_request_resolved_view(mef_context_request(context));
    if (resolved == NULL) {
        return MEF_ERR_INPUT;
    }
    request = &resolved->request;
    if (request->operation != MEF_OP_CAL_BIAS || request->operation_version != 1 ||
        request->input_count != input->count) {
        return MEF_ERR_INPUT;
    }
    if (resolved->bpm_selection_count != 1) {
        return MEF_ERR_UNSUPPORTED;
    }
    if (options == NULL || options->bpm == NULL) {
        if (request->calibration_count != 0 ||
            resolved->bpm_selections[0].state != MEF_BPM_OMITTED) {
            return MEF_ERR_UNSUPPORTED;
        }
    } else {
        if (request->calibration_count != 1 || resolved->calibration_roles[0] != MEF_CAL_BPM ||
            resolved->bpm_selections[0].state != MEF_BPM_SELECTED) {
            return MEF_ERR_UNSUPPORTED;
        }
    }
    if (options != NULL &&
        ((options->with_mad != 0 && options->with_mad != 1) ||
            (options->ron_pair_set != 0 && options->ron_pair_set != 1) ||
            (options->bpm_active_only != 0 && options->bpm_active_only != 1) ||
            (options->bpm_active_only && options->bpm == NULL) ||
            !is_finite_level(options->high_sigma) || options->high_sigma <= 0.0 ||
            (options->ron_pair_set &&
                (options->ron_first >= input->count || options->ron_second >= input->count ||
                    options->ron_first == options->ron_second ||
                    !strcmp(request->inputs[options->ron_first].resolved_path,
                        request->inputs[options->ron_second].resolved_path))))) {
        return MEF_ERR_INPUT;
    }
    if (options &&
        ((options->ron_clip_enabled != 0 && options->ron_clip_enabled != 1) ||
            (options->ron_clip_enabled &&
                (!options->ron_pair_set || !is_finite_level(options->ron_clip.sigma_low) ||
                    options->ron_clip.sigma_low <= 0 ||
                    !is_finite_level(options->ron_clip.sigma_high) ||
                    options->ron_clip.sigma_high <= 0 || options->ron_clip.max_iterations < 1 ||
                    options->ron_clip.max_iterations > 1000)))) {
        return MEF_ERR_INPUT;
    }
    if (mef_config_bias_settings(
            mef_context_config(context), input->configuration_detector, bias_settings) != MEF_OK) {
        return MEF_ERR_CONFIG;
    }
    if ((bias_settings->median_even_handling != MEDIAN_EVEN_AVERAGE &&
            bias_settings->median_even_handling != MEDIAN_EVEN_LOWER) ||
        bias_settings->minimum_frames < 3 || !is_finite_level(bias_settings->kappa) ||
        bias_settings->kappa < 0.0 || bias_settings->rejection[0] < 0 ||
        bias_settings->rejection[1] < 0) {
        return MEF_ERR_CONFIG;
    }
    if (input->count < (size_t)bias_settings->minimum_frames) {
        return MEF_ERR_INPUT;
    }
    if (input->frames[0] == NULL) {
        return MEF_ERR_INPUT;
    }
    width = input->frames[0]->lx;
    height = input->frames[0]->ly;
    if (width <= 0 || height <= 0 || width > MAX_COLUMN_NUMBER || height > MAX_LINE_NUMBER ||
        width > INT_MAX / height) {
        return MEF_ERR_INPUT;
    }
    if (!valid_interval(bias_settings->trim, width) ||
        !valid_interval(bias_settings->trim + 2, height) ||
        bias_settings->trim[0] == bias_settings->trim[1] ||
        bias_settings->trim[2] == bias_settings->trim[3]) {
        return MEF_ERR_CONFIG;
    }
    scan_width = 0;
    if (bias_settings->use_prescan) {
        if (!valid_interval(bias_settings->prescan, width)) {
            return MEF_ERR_CONFIG;
        }
        scan_width += bias_settings->prescan[1] - bias_settings->prescan[0] + 1;
    }
    if (bias_settings->use_overscan) {
        if (!valid_interval(bias_settings->overscan, width)) {
            return MEF_ERR_CONFIG;
        }
        scan_width += bias_settings->overscan[1] - bias_settings->overscan[0] + 1;
    }
    if (bias_settings->rejection[0] >= scan_width ||
        bias_settings->rejection[1] >= scan_width - bias_settings->rejection[0]) {
        return MEF_ERR_CONFIG;
    }
    pixels = (size_t)width * (size_t)height;
    for (frame_index = 0; frame_index < input->count; ++frame_index) {
        if (strcmp(request->inputs[frame_index].detector_id, request->inputs[0].detector_id)) {
            return MEF_ERR_UNSUPPORTED;
        }

        /* The caller supplies the same validated plane for primary or MEF
         * storage. Numerical validation must not depend on the file's HDU. */

        if (input->frames[frame_index] == NULL || input->frames[frame_index]->data == NULL ||
            input->frames[frame_index]->lx != width || input->frames[frame_index]->ly != height) {
            return MEF_ERR_INPUT;
        }
        for (pixel_index = 0; pixel_index < pixels; ++pixel_index) {
            if (!is_finite_level(input->frames[frame_index]->data[pixel_index])) {
                return MEF_ERR_INPUT;
            }
        }
    }
    if (options != NULL && options->bpm != NULL) {
        const pixelmap *bpm;
        bpm = options->bpm;
        if (bpm->data == NULL || bpm->lx != width || bpm->ly != height) {
            return MEF_ERR_INPUT;
        }
        for (pixel_index = 0; pixel_index < pixels; ++pixel_index) {
            if (bpm->data[pixel_index] != PIXELMAP_0 && bpm->data[pixel_index] != PIXELMAP_1) {
                return MEF_ERR_INPUT;
            }
        }
    }
    return MEF_OK;
}

mef_status mef_cal_bias(
    mef_context *context, const mef_bias_input *input, mef_bias_result **out, mef_error **error)
{
    return mef_cal_bias_measurements(context, input, NULL, out, error);
}

mef_status mef_cal_bias_measurements(mef_context *context, const mef_bias_input *input,
    const mef_bias_measurement_options *options, mef_bias_result **out, mef_error **error)
{
    pixelmap *active_bpm;
    const pixelmap *raw_bpm;
    mef_bias_frame_measurements *frame_measurements;
    mef_bias_measurements *detector_measurements;
    int scan_region[4], x, y;
    size_t position;
    const mef_allocator *allocator;
    const mef_resolved_request_spec *resolved;
    mef_bias_settings bias_settings;
    mef_bias_statistics stack_statistics;
    mef_bias_diagnostic diagnostic;
    mef_bias_result *pending_result;
    mef_status status;
    mef_bb overscan_bridge;
    mef_ccd legacy_detector_geometry;
    cube_t *corrected_frames;
    image_t *corrected_frame;
    char **input_names;
    size_t frame_index;
    const char *detail;
    detail = "Invalid or unsupported bias request, image data or geometry";
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) {
        return MEF_ERR_INPUT;
    }
    pending_result = NULL;
    frame_measurements = NULL;
    active_bpm = NULL;
    raw_bpm = options == NULL ? NULL : options->bpm;
    corrected_frames = NULL;
    input_names = NULL;
    allocator = mef_context_allocator(context);
    status = validate_bias_inputs(context, input, &bias_settings, options);
    if (status != MEF_OK) {
        goto cleanup;
    }
    resolved = mef_request_resolved_view(mef_context_request(context));

    /* Construct a safely destructible pending owner, before numerical work. */

    detail = "Cannot allocate pending bias result or QC arrays";
    status = MEF_ERR_MEMORY;
    pending_result = allocator->allocate(allocator->user, sizeof(*pending_result));
    if (pending_result == NULL) {
        goto cleanup;
    }
    memset(pending_result, 0, sizeof(*pending_result));
    pending_result->allocator = *allocator;
    pending_result->signal = NULL;
    pending_result->request = NULL;
    pending_result->qc.scan_median = NULL;
    pending_result->qc.scan_stdev = NULL;
    pending_result->qc.accepted = NULL;
    pending_result->qc.input_frames = input->count;
    pending_result->qc.variance_state = MEF_BIAS_VARIANCE_UNAVAILABLE_LEGACY;
    pending_result->qc.bpm_selection = MEF_BPM_OMITTED;
    pending_result->qc.bpm_applied = 0;
    pending_result->qc.ron_estimate_available = 0;
    pending_result->qc.scan_median =
        allocator->allocate(allocator->user, input->count * sizeof(float));
    pending_result->qc.scan_stdev =
        allocator->allocate(allocator->user, input->count * sizeof(float));
    pending_result->qc.accepted = allocator->allocate(allocator->user, input->count * sizeof(int));
    input_names = allocator->allocate(allocator->user, input->count * sizeof(*input_names));
    if (pending_result->qc.scan_median == NULL || pending_result->qc.scan_stdev == NULL ||
        pending_result->qc.accepted == NULL || input_names == NULL) {
        goto cleanup;
    }
    status = mef_request_create_resolved(resolved, allocator, &pending_result->request, error);
    if (status != MEF_OK) {
        goto cleanup;
    }

    if (options != NULL) {
        detector_measurements = &pending_result->measurements;
        detector_measurements->count = input->count;
        frame_measurements =
            allocator->allocate(allocator->user, input->count * sizeof(*frame_measurements));
        if (frame_measurements == NULL) {
            status = MEF_ERR_MEMORY;
            goto cleanup;
        }
        memset(frame_measurements, 0, input->count * sizeof(*frame_measurements));
        detector_measurements->frames = frame_measurements;
        pending_result->qc.bpm_selection = resolved->bpm_selections[0].state;
        pending_result->qc.bpm_applied = raw_bpm != NULL;
        if (raw_bpm != NULL) {
            active_bpm = pixelmap_getvig((pixelmap *)raw_bpm, bias_settings.trim[0],
                bias_settings.trim[2], bias_settings.trim[1], bias_settings.trim[3]);
            if (active_bpm == NULL) {
                status = MEF_ERR_COMPUTATION;
                goto cleanup;
            }
        }

        /* [BIAS-RAW-PAIR-RON]
         * Raw-pair noise is independent of later scan correction and admission.
         */

        if (options->ron_pair_set) {
            detector_measurements->ron_first = options->ron_first;
            detector_measurements->ron_second = options->ron_second;
            if (image_pair_stats_checked(input->frames[options->ron_first],
                    input->frames[options->ron_second], raw_bpm, raw_bpm, bias_settings.trim,
                    options->with_mad, &detector_measurements->raw_difference) != 0) {
                status = MEF_ERR_COMPUTATION;
                goto cleanup;
            }
            detector_measurements->ron_stdev_available =
                detector_measurements->raw_difference.stdev_available;
            detector_measurements->ron_mad_available =
                detector_measurements->raw_difference.mad_available;
            detector_measurements->ron_stdev_adu =
                detector_measurements->raw_difference.stdev / sqrt(2.0);
            detector_measurements->ron_mad_adu =
                1.4826 * detector_measurements->raw_difference.mad / sqrt(2.0);
            pending_result->qc.ron_estimate_available = detector_measurements->ron_stdev_available;
            if (options->ron_clip_enabled) {
                if (image_pair_stats_clipped_checked(input->frames[options->ron_first],
                        input->frames[options->ron_second], raw_bpm, raw_bpm, bias_settings.trim,
                        &options->ron_clip, &detector_measurements->clipped_difference) != 0) {
                    status = MEF_ERR_COMPUTATION;
                    goto cleanup;
                }
                detector_measurements->ron_clipped_available =
                    detector_measurements->clipped_difference.converged &&
                    detector_measurements->clipped_difference.sample.stdev_available;
                detector_measurements->ron_clipped_adu =
                    detector_measurements->clipped_difference.sample.stdev / sqrt(2.0);
            }
        }
    }

    /* [BIAS-SCAN-CORRECTION]
     * Use a local geometry copy because the shared scan helper temporarily
     * converts its column bounds to zero-based indices. Raw inputs stay borrowed.
     */

    memcpy(
        legacy_detector_geometry.prescan_x, bias_settings.prescan, sizeof(bias_settings.prescan));
    memcpy(legacy_detector_geometry.overscan_x, bias_settings.overscan,
        sizeof(bias_settings.overscan));
    memcpy(legacy_detector_geometry.trimreg, bias_settings.trim, sizeof(bias_settings.trim));
    overscan_bridge.ccd = &legacy_detector_geometry;
    overscan_bridge.xtnum = 1;
    overscan_bridge.nxts = 1;
    overscan_bridge.use_prescan = bias_settings.use_prescan;
    overscan_bridge.use_overscan = bias_settings.use_overscan;
    memcpy(overscan_bridge.scanrej, bias_settings.rejection, sizeof(bias_settings.rejection));
    overscan_bridge.bias_frame_name = input_names;
    overscan_bridge.bias_scan_median = (float *)pending_result->qc.scan_median;
    overscan_bridge.bias_scan_stdev = (float *)pending_result->qc.scan_stdev;
    detail = "Cannot copy or overscan-correct a selected bias image";
    status = MEF_ERR_COMPUTATION;
    corrected_frames = cube_new(input->frames[0]->lx, input->frames[0]->ly, (int)input->count);
    if (corrected_frames == NULL) {
        goto cleanup;
    }
    for (frame_index = 0; frame_index < input->count; ++frame_index) {
        input_names[frame_index] = (char *)resolved->request.inputs[frame_index].resolved_path;
        corrected_frames->plane[frame_index] = image_copy((image_t *)input->frames[frame_index]);
        if (corrected_frames->plane[frame_index] == NULL) {
            goto cleanup;
        }
        if (options != NULL) {
            frame_measurements =
                (mef_bias_frame_measurements *)pending_result->measurements.frames + frame_index;
            if (image_getstats_masked_checked(input->frames[frame_index], raw_bpm,
                    bias_settings.trim, options->with_mad, &frame_measurements->active_raw) != 0) {
                goto cleanup;
            }
            scan_region[2] = bias_settings.trim[2];
            scan_region[3] = bias_settings.trim[3];
            if (bias_settings.use_prescan) {
                scan_region[0] = bias_settings.prescan[0];
                scan_region[1] = bias_settings.prescan[1];
                if (image_getstats_masked_checked(input->frames[frame_index], NULL, scan_region,
                        options->with_mad, &frame_measurements->prescan) != 0) {
                    goto cleanup;
                }
            }
            if (bias_settings.use_overscan) {
                scan_region[0] = bias_settings.overscan[0];
                scan_region[1] = bias_settings.overscan[1];
                if (image_getstats_masked_checked(input->frames[frame_index], NULL, scan_region,
                        options->with_mad, &frame_measurements->overscan) != 0) {
                    goto cleanup;
                }
            }
        }

        /* Detector BPM does not apply to empty electronic scan reads. */

        corrected_frame = mef_overscan_correction(
            corrected_frames->plane[frame_index], &overscan_bridge, (int)frame_index, "bias");
        if (corrected_frame == NULL) {
            goto cleanup;
        }
        image_del(corrected_frames->plane[frame_index]);
        corrected_frames->plane[frame_index] = corrected_frame;
        if (options != NULL && image_getstats_masked_checked(corrected_frame, active_bpm, NULL,
                                   options->with_mad, &frame_measurements->active_corrected) != 0) {
            goto cleanup;
        }
    }
    corrected_frames->lx = corrected_frames->plane[0]->lx;
    corrected_frames->ly = corrected_frames->plane[0]->ly;
    detail = "Bias rejection or median stacking failed; no result transferred";
    diagnostic.detector_id = resolved->request.inputs[0].detector_id;
    diagnostic.input_names = input_names;
    pending_result->signal =
        mef_bias_stack_masked_diagnostic(corrected_frames, bias_settings.minimum_frames,
            bias_settings.kappa, &stack_statistics, (int *)pending_result->qc.accepted, active_bpm,
            (median_even_handling)bias_settings.median_even_handling, &diagnostic);
    corrected_frames = NULL; /* Kernel always consumes the working cube. */
    if (pending_result->signal == NULL) {
        if (stack_statistics.zero_spread) {
            detail = "Bias zero-spread failure: computed frame-mean sigma is exactly zero; "
                     "processing stopped before stacking; detector and input means reported in "
                     "error log";
        }
        goto cleanup;
    }

    /* Structural postcondition, followed by explicit legacy-QC collection. */

    detail = "Bias result dimensions do not match the requested trim region";
    if (pending_result->signal->lx != bias_settings.trim[1] - bias_settings.trim[0] + 1 ||
        pending_result->signal->ly != bias_settings.trim[3] - bias_settings.trim[2] + 1) {
        goto cleanup;
    }
    pending_result->qc.frame_mean_average = stack_statistics.average;
    pending_result->qc.frame_mean_sigma = stack_statistics.sigma;
    pending_result->qc.rejection_low = stack_statistics.low;
    pending_result->qc.rejection_high = stack_statistics.high;
    pending_result->qc.product_median = stack_statistics.median;
    pending_result->qc.product_stdev = stack_statistics.stdev;
    pending_result->qc.accepted_frames = stack_statistics.accepted;
    pending_result->qc.median_even_handling = bias_settings.median_even_handling;

    /* [BIAS-MASTER-QC]
     * Characterize the completed master; high-offset flags do not replace pixels.
     */

    if (options != NULL) {
        pixelmap *flags;
        detector_measurements = &pending_result->measurements;
        if (image_getstats_masked_checked(pending_result->signal, active_bpm, NULL,
                options->with_mad, &detector_measurements->master) != 0 ||
            image_getstats_masked_checked(pending_result->signal, NULL, NULL, options->with_mad,
                &detector_measurements->master_unmasked) != 0) {
            goto cleanup;
        }
        if (detector_measurements->master.mad_available) {
            detector_measurements->high_offset_threshold =
                detector_measurements->master.median +
                options->high_sigma * 1.4826 * detector_measurements->master.mad;
            if (!is_finite_level(detector_measurements->high_offset_threshold)) {
                goto cleanup;
            }
            flags = pixelmap_new(pending_result->signal->lx, pending_result->signal->ly);
            if (flags == NULL) {
                goto cleanup;
            }
            detector_measurements->high_offset_flags = flags;
            detector_measurements->high_offset_available = 1;
            detector_measurements->high_offset_degenerate =
                detector_measurements->master.mad == 0.0;
            for (y = 0; y < flags->ly; ++y) {
                for (x = 0; x < flags->lx; ++x) {
                    position = (size_t)y * (size_t)flags->lx + (size_t)x;
                    flags->data[position] = pending_result->signal->data[position] >
                                                    detector_measurements->high_offset_threshold
                                                ? PIXELMAP_1
                                                : PIXELMAP_0;
                    detector_measurements->high_offset_count += flags->data[position] == PIXELMAP_1;
                }
            }
            pixelmap_updatecount(flags);
        }
    }
    *out = pending_result;
    pending_result = NULL;
    status = MEF_OK;
cleanup:
    cube_del(corrected_frames);
    pixelmap_del(active_bpm);
    if (allocator != NULL) {
        release_owned(allocator, input_names);
    }
    mef_bias_result_destroy(pending_result);
    if (status != MEF_OK && error != NULL && *error == NULL) {
        (void)mef_error_create(status, detail, allocator, error);
    }
    return status;
}
