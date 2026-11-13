#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias.h"
#include "mef_bias_qc_fits.h"
#include <errno.h>
#include <limits.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef realloc
#undef free

static int process_bias_detector(detector_plan *detector, size_t index, size_t frame_count,
    char *const *raw_paths, const mef_config *config, const mef_product_paths *paths,
    const char *private_work_directory, const mef_bias_measurement_options *options,
    mef_bias_product_qc *archive, mef_error **error)
{
    mef_image_ref *input_references = NULL, calibration;
    mef_request *request = NULL;
    mef_context *context = NULL;
    mef_resolved_request_spec request_spec;
    mef_bpm_selection selection;
    mef_calibration_role role = MEF_CAL_BPM;
    mef_bias_result *result = NULL;
    mef_status status = MEF_ERR_INPUT;
    mef_bias_measurement_options measurements = *options;
    qfits_header *qc_header = NULL;
    char qc_message[256];
    pixelmap *mask = NULL, *loaded = NULL;
    const mef_bound_detector *first;
    size_t i;
    int succeeded = 0, x, y;
    const image_t *image;
    input_references = calloc(frame_count, sizeof(*input_references));
    if (input_references == NULL) {
        goto done;
    }
    for (i = 0; i < frame_count; ++i) {
        const mef_bound_detector *bound_input =
            mef_layout_find(detector->raw_layouts[i], detector->detector_id);
        input_references[i].asset_record_id = raw_paths[i];
        input_references[i].resolved_path = raw_paths[i];
        input_references[i].detector_id = detector->detector_id;
        input_references[i].hdu_index = bound_input->image.hdu_index;
        if (bound_input->image.has_extname && bound_input->image.has_extver) {
            input_references[i].extname = bound_input->image.extname;
            input_references[i].extver = bound_input->image.extver;
        }
    }
    first = mef_layout_find(detector->raw_layouts[0], detector->detector_id);
    if (detector->mask_map) {
        const mef_bpm_policy *policy = &mef_config_processing(config)->bpm;
        status = policy->supplied ? mef_layout_load_bpm_policy(detector->mask_map,
                                        detector->detector_id, policy, &loaded, error)
                                  : mef_layout_load_bpm(detector->mask_map, detector->detector_id,
                                        detector->bpm_good_value, &loaded, error);
        if (status != MEF_OK) {
            goto done;
        }
        if (detector->bpm_active_only) {
            mask = pixelmap_new((int)first->image.axes[0], (int)first->image.axes[1]);
            if (mask == NULL) {
                goto done;
            }
            for (y = 0; y < loaded->ly; ++y) {
                for (x = 0; x < loaded->lx; ++x) {
                    mask->data[(y + detector->settings.trim[2] - 1) * mask->lx + x +
                               detector->settings.trim[0] - 1] = loaded->data[y * loaded->lx + x];
                }
            }
            pixelmap_updatecount(mask);
        } else {
            mask = loaded;
            loaded = NULL;
        }
        measurements.bpm = mask;
        measurements.bpm_active_only = detector->bpm_active_only;
    }
    memset(&request_spec, 0, sizeof(request_spec));
    memset(&calibration, 0, sizeof(calibration));
    request_spec.request.operation = MEF_OP_CAL_BIAS;
    request_spec.request.operation_version = 1;
    request_spec.request.inputs = input_references;
    request_spec.request.input_count = frame_count;
    request_spec.request.work_dir = private_work_directory;
    request_spec.request.output_dir = paths->directory;
    request_spec.request.log_path = paths->log;
    selection.detector_id = detector->detector_id;
    selection.state = mask ? MEF_BPM_SELECTED : MEF_BPM_OMITTED;
    request_spec.bpm_selections = &selection;
    request_spec.bpm_selection_count = 1;
    if (mask) {
        calibration.asset_record_id = detector->bpm_path;
        calibration.resolved_path = detector->bpm_path;
        calibration.detector_id = detector->detector_id;
        calibration.hdu_index = detector->bpm_hdu;
        request_spec.request.calibrations = &calibration;
        request_spec.request.calibration_count = 1;
        request_spec.calibration_roles = &role;
        request_spec.calibration_role_count = 1;
    }
    status = mef_request_create_resolved(&request_spec, NULL, &request, error);
    if (status == MEF_OK) {
        status = mef_context_create(config, request, NULL, &context, error);
    }
    if (status != MEF_OK) {
        goto done;
    }
    if (snprintf(detector->temporary_path, sizeof(detector->temporary_path),
            "%s/detector-%06lu.fits", private_work_directory,
            (unsigned long)index) >= (int)sizeof(detector->temporary_path)) {
        goto done;
    }

    /* [BIAS-DETECTOR-CALIBRATION]
     * The file adapter owns the loaded raws; the result owns its corrected master.
     */

    status = mef_bias_from_files_measurements(context,
        (const mef_layout_map *const *)detector->raw_layouts, frame_count, detector->detector_id,
        &measurements, &result, error);
    if (status != MEF_OK ||
        !mef_bias_product_qc_add(archive, index, detector->detector_id,
            detector->option_values[AMP], detector->option_values[READOUT],
            detector->configuration_index, detector->bin_x, detector->bin_y, result, &measurements,
            &detector->settings, (int)first->image.axes[1], detector->bpm_path, detector->bpm_hdu,
            detector->bpm_good_value)) {
        goto done;
    }
    if (mef_bias_qc_fits_header(
            mef_bias_product_qc_view(archive), index, &qc_header, qc_message, sizeof(qc_message))) {
        fprintf(stderr, "%s\n", qc_message);
        goto done;
    }
    status = mef_bias_publish_with_header_named(config, result, detector->configuration_index,
        detector->temporary_path, qc_header, detector->detector_id, error);
    if (status != MEF_OK) {
        goto done;
    }
    image = mef_bias_result_signal(result);
    detector->assembly.path = detector->temporary_path;
    detector->assembly.detector_id = detector->detector_id;
    detector->assembly.configuration_detector = detector->configuration_index;
    detector->assembly.output_hdu = index + 1;
    detector->assembly.width = image->lx;
    detector->assembly.height = image->ly;
    detector->assembly.bitpix = BPP_DEFAULT;
    detector->assembly.bscale = 1;
    detector->assembly.bzero = 0;
    succeeded = 1;
done:
    qfits_header_destroy(qc_header);
    mef_bias_result_destroy(result);
    mef_context_destroy(context);
    mef_request_destroy(request);
    pixelmap_del(mask);
    pixelmap_del(loaded);
    free(input_references);
    return succeeded;
}

int mef_bias_process(mef_bias *recipe, size_t i)
{
    fprintf(recipe->run->log, "DETECTOR_START %lu %s CONFIGURATION %lu\n", (unsigned long)i,
        recipe->arguments.detectors[i].detector_id,
        (unsigned long)recipe->arguments.detectors[i].configuration_index);
    if (fflush(recipe->run->log)) {
        return 0;
    }
    printf("BIAS_DETECTOR %lu/%lu %s\n", (unsigned long)i + 1,
        (unsigned long)recipe->arguments.detector_count,
        recipe->arguments.detectors[i].detector_id);
    fflush(stdout);
    if (!process_bias_detector(recipe->arguments.detectors + i, i, recipe->frame_count,
            recipe->raw_paths, recipe->config, &recipe->run->paths,
            recipe->run->private_work_directory, &recipe->options, recipe->archive,
            &recipe->error)) {
        return 0;
    }
    recipe->assembly[i] = recipe->arguments.detectors[i].assembly;
    fprintf(recipe->run->log, "DETECTOR_DONE %s\n", recipe->arguments.detectors[i].detector_id);
    if (fflush(recipe->run->log)) {
        return 0;
    }
    return 1;
}
