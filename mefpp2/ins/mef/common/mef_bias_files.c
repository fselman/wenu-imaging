/* Bridge resolved FITS detector bindings to the in-memory bias service.
 * Validation/loading/calculation use the shared operation template. Loaded raw
 * frames belong to the adapter; successful results transfer to the caller.
 * Publication writes one detector MEF without replacing an existing final path.
 */

#include "mef_bias_files.h"
#include "mefp_lib.h"
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>

static mef_status report_file_failure(mef_status status, const char *message, mef_error **error)
{
    if (error != NULL && *error == NULL) {
        (void)mef_error_create(status, message, NULL, error);
    }
    return status;
}

/* The first concrete use of the reusable operation template. Later adapters
 * provide their own typed state/callbacks without copying this orchestration. */

#include "mef_operation_template.h"

typedef struct {
    mef_context *context;
    const mef_layout_map *const *maps;
    size_t count;
    const char *detector, *final_path;
    image_t **frames;
    const image_t **borrowed;
    size_t configuration_detector;
    mef_bias_result *pending;
    const mef_bias_measurement_options *measurements;
} bias_state;

static mef_status validate_mapped_inputs(void *opaque, mef_error **error)
{
    bias_state *state;
    const mef_resolved_request_spec *request;
    const mef_bound_detector *first_detector, *detector_binding;
    const mef_image_ref *input_reference;
    size_t i, entries;
    state = opaque;
    if (state->context == NULL || state->maps == NULL || state->detector == NULL ||
        !*state->detector || state->count == 0 || state->count > INT_MAX ||
        state->count > (size_t)-1 / sizeof(*state->frames)) {
        return report_file_failure(MEF_ERR_INPUT, "Invalid mapped bias input", error);
    }
    request = mef_request_resolved_view(mef_context_request(state->context));
    if (request == NULL || request->request.input_count != state->count ||
        request->request.operation != MEF_OP_CAL_BIAS || request->bpm_selection_count != 1) {
        return report_file_failure(
            MEF_ERR_UNSUPPORTED, "Bias adapter requires resolved BPM selection", error);
    }
    if (state->measurements == NULL || state->measurements->bpm == NULL) {
        if (request->request.calibration_count != 0 ||
            request->bpm_selections[0].state != MEF_BPM_OMITTED) {
            return report_file_failure(
                MEF_ERR_UNSUPPORTED, "BPM map and request selection disagree", error);
        }
    } else if (request->request.calibration_count != 1 ||
               request->calibration_roles[0] != MEF_CAL_BPM ||
               request->bpm_selections[0].state != MEF_BPM_SELECTED) {
        return report_file_failure(
            MEF_ERR_UNSUPPORTED, "BPM map and request selection disagree", error);
    }
    first_detector = mef_layout_find(state->maps[0], state->detector);
    if (first_detector == NULL) {
        return report_file_failure(MEF_ERR_INPUT, "Missing bias detector", error);
    }
    state->configuration_detector = first_detector->configuration_detector;
    for (i = 0; i < state->count; ++i) {
        input_reference = request->request.inputs + i;
        detector_binding = mef_layout_find(state->maps[i], state->detector);
        (void)mef_layout_map_view(state->maps[i], &entries);
        if (entries != 1 || detector_binding == NULL ||
            detector_binding->selection != MEF_OUTPUT_SELECTED ||
            strcmp(detector_binding->unit, "ADU") ||
            strcmp(input_reference->detector_id, state->detector) ||
            detector_binding->configuration_detector != first_detector->configuration_detector ||
            detector_binding->image.hdu_index != input_reference->hdu_index ||
            (input_reference->extname != NULL &&
                (!detector_binding->image.has_extname || !detector_binding->image.has_extver ||
                    strcmp(input_reference->extname, detector_binding->image.extname) ||
                    input_reference->extver != detector_binding->image.extver)) ||
            mef_layout_compatible(state->maps[0], state->maps[i], "ADU", "ADU", NULL, NULL) !=
                MEF_OK ||
            strcmp(mef_layout_map_path(state->maps[i]), input_reference->resolved_path)) {
            return report_file_failure(
                MEF_ERR_INPUT, "Bias map/request or readout mismatch", error);
        }
    }
    return MEF_OK;
}

static mef_status load_bias_frames(void *opaque, mef_error **error)
{
    bias_state *state;
    mef_status status;
    size_t i;
    state = opaque;
    state->frames = calloc(state->count, sizeof(*state->frames));
    state->borrowed = calloc(state->count, sizeof(*state->borrowed));
    if (state->frames == NULL || state->borrowed == NULL) {
        return report_file_failure(MEF_ERR_MEMORY, "Cannot allocate bias plane handles", error);
    }

    /* [BIAS-INPUT-LOADING]
     * Each map selects the logical detector's explicit source HDU, not its ordinal.
     */

    for (i = 0; i < state->count; ++i) {
        status = mef_layout_load(state->maps[i], state->detector, state->frames + i, error);
        if (status != MEF_OK) {
            return status;
        }
        state->borrowed[i] = state->frames[i];
    }
    return MEF_OK;
}

static mef_status calculate_bias_detector(void *opaque, mef_error **error)
{
    bias_state *state;
    mef_bias_input input;
    state = opaque;
    input.frames = state->borrowed;
    input.count = state->count;
    input.configuration_detector = state->configuration_detector;
    return mef_cal_bias_owned_measurements(
        state->context, &input, state->frames, state->measurements, &state->pending, error);
}

static mef_status publish_bias_step(void *opaque, mef_error **error)
{
    bias_state *state;
    state = opaque;
    return mef_bias_publish(mef_context_config(state->context), state->pending,
        state->configuration_detector, state->final_path, error);
}

static void release_bias_frames(void *opaque)
{
    bias_state *state;
    size_t i;
    state = opaque;
    if (state->frames != NULL) {
        for (i = 0; i < state->count; ++i) {
            image_del(state->frames[i]);
        }
    }
    free(state->frames);
    free(state->borrowed);
    state->frames = NULL;
    state->borrowed = NULL;
}

static mef_status run_bias_file_operation(mef_context *context, const mef_layout_map *const *maps,
    size_t count, const char *detector, const char *final_path,
    const mef_bias_measurement_options *measurements, mef_bias_result **out, mef_error **error)
{
    bias_state state;
    mef_operation_steps steps;
    mef_status status;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) {
        return MEF_ERR_INPUT;
    }
    memset(&state, 0, sizeof(state));
    state.context = context;
    state.maps = maps;
    state.measurements = measurements;
    state.count = count;
    state.detector = detector;
    state.final_path = final_path;
    steps.validate = validate_mapped_inputs;
    steps.load = load_bias_frames;
    steps.calculate = calculate_bias_detector;
    steps.publish = final_path ? publish_bias_step : NULL;
    steps.cleanup = release_bias_frames;
    status = mef_operation_run(&steps, &state, error);
    if (status == MEF_OK) {
        *out = state.pending;
    } else {
        mef_bias_result_destroy(state.pending);
    }
    return status;
}

mef_status mef_bias_from_files(mef_context *context, const mef_layout_map *const *maps,
    size_t count, const char *detector, mef_bias_result **out, mef_error **error)
{
    return run_bias_file_operation(context, maps, count, detector, NULL, NULL, out, error);
}

mef_status mef_bias_files_execute(mef_context *context, const mef_layout_map *const *maps,
    size_t count, const char *detector, const char *final_path, mef_bias_result **out,
    mef_error **error)
{
    if (final_path == NULL) {
        return MEF_ERR_INPUT;
    }
    return run_bias_file_operation(context, maps, count, detector, final_path, NULL, out, error);
}

mef_status mef_bias_files_execute_measurements(mef_context *context,
    const mef_layout_map *const *maps, size_t count, const char *detector, const char *final_path,
    const mef_bias_measurement_options *measurements, mef_bias_result **out, mef_error **error)
{
    if (final_path == NULL || measurements == NULL) {
        return MEF_ERR_INPUT;
    }
    return run_bias_file_operation(
        context, maps, count, detector, final_path, measurements, out, error);
}

mef_status mef_bias_from_files_measurements(mef_context *context, const mef_layout_map *const *maps,
    size_t count, const char *detector, const mef_bias_measurement_options *measurements,
    mef_bias_result **out, mef_error **error)
{
    if (measurements == NULL) {
        return MEF_ERR_INPUT;
    }
    return run_bias_file_operation(context, maps, count, detector, NULL, measurements, out, error);
}

/* #211/#212: qfits_header_del leaves n stale. qfits_header_copy traverses
 * forward links and rebuilds n via append. Never index the deleted source or
 * merge it as an update. Build the required structural prefix without deletion.
 * Existing extension-input publication does not enter this conversion. */

static int is_structural_fits_key(const char *key)
{
    return !strcmp(key, "SIMPLE") || !strcmp(key, "XTENSION") || !strcmp(key, "BITPIX") ||
           !strcmp(key, "NAXIS") || !strcmp(key, "NAXIS1") || !strcmp(key, "NAXIS2") ||
           !strcmp(key, "NAXIS3") || !strcmp(key, "PCOUNT") || !strcmp(key, "GCOUNT") ||
           !strcmp(key, "EXTEND") || !strcmp(key, "BSCALE") || !strcmp(key, "BZERO") ||
           !strcmp(key, "END");
}

static qfits_header *copy_primary_image_header(
    qfits_header *source, const image_t *signal, int is_primary)
{
    qfits_header *copy, *out;
    char value[32], key[FITS_LINESZ + 1], val[FITS_LINESZ + 1];
    char comment[FITS_LINESZ + 1], line[FITS_LINESZ + 1];
    int i;
    copy = qfits_header_copy(source);
    if (copy == NULL) {
        return NULL;
    }
    out = qfits_header_new();
    if (out == NULL) {
        qfits_header_destroy(copy);
        return NULL;
    }
    qfits_header_append(
        out, is_primary ? "SIMPLE" : "XTENSION", is_primary ? "T" : "IMAGE", NULL, NULL);
    sprintf(value, "%d", is_primary ? 8 : BPP_DEFAULT);
    qfits_header_append(out, "BITPIX", value, NULL, NULL);
    qfits_header_append(out, "NAXIS", is_primary ? "0" : "2", NULL, NULL);
    if (is_primary) {
        qfits_header_append(out, "EXTEND", "T", NULL, NULL);
    } else {
        sprintf(value, "%d", signal->lx);
        qfits_header_append(out, "NAXIS1", value, NULL, NULL);
        sprintf(value, "%d", signal->ly);
        qfits_header_append(out, "NAXIS2", value, NULL, NULL);
        qfits_header_append(out, "PCOUNT", "0", NULL, NULL);
        qfits_header_append(out, "GCOUNT", "1", NULL, NULL);

        /* Loaded/calculated pixels are physical ADU, not stored raw integers. */

        qfits_header_append(out, "BSCALE", "1.0", "pixel=FITS*BSCALE+BZERO", NULL);
        qfits_header_append(out, "BZERO", "0.0", "pixel=FITS*BSCALE+BZERO", NULL);
    }
    for (i = 0; i < copy->n; ++i) {
        if (qfits_header_getitem(copy, i, key, val, comment, line) != 0) {
            qfits_header_destroy(copy);
            qfits_header_destroy(out);
            return NULL;
        }
        if (!is_structural_fits_key(key)) {
            qfits_header_append(
                out, key, *val ? val : NULL, *comment ? comment : NULL, *line ? line : NULL);
        }
    }
    qfits_header_append(out, "END", NULL, NULL, NULL);
    qfits_header_destroy(copy);
    return out;
}

static mef_status publish_bias_header(const mef_config *config, const mef_bias_result *result,
    size_t configuration_detector, const char *final_path, const qfits_header *additions,
    const char *output_detector, mef_error **error)
{
    const mef_request_spec *request;
    const mef_bias_qc *bias_qc;
    const image_t *signal;
    mef_bb *legacy_header_context;
    qfits_header *primary_header, *detector_header;
    framelist names;
    char **members, *temporary_path, *basename_start;
    int temporary_descriptor, source_hdu, published;
    size_t i, path_length;
    mef_status status;
    if (error != NULL && *error != NULL) {
        return MEF_ERR_INPUT;
    }
    if (result == NULL || final_path == NULL || final_path[0] != '/') {
        return report_file_failure(MEF_ERR_INPUT, "Require an absolute new bias output", error);
    }
    request = mef_request_view(mef_bias_result_request(result));
    bias_qc = mef_bias_result_qc(result);
    signal = mef_bias_result_signal(result);
    if (request == NULL || bias_qc == NULL || signal == NULL || request->input_count == 0 ||
        request->input_count > INT_MAX || request->input_count > (size_t)-1 / sizeof(*members)) {
        return report_file_failure(MEF_ERR_INPUT, "Incomplete bias result", error);
    }
    legacy_header_context = NULL;
    primary_header = detector_header = NULL;
    members = NULL;
    temporary_path = NULL;
    published = 0;
    status = mef_config_bias_header_context(config, configuration_detector, &legacy_header_context);
    if (status != MEF_OK) {
        goto done;
    }

    /* Bound the existing legacy 80-byte creation-name formatter. This is not
     * a clock/naming correction or a new filename grammar (#207 stays open). */

    if (strlen(legacy_header_context->instrument) > 24 ||
        strlen(legacy_header_context->recipe_key) > 48 ||
        strlen(legacy_header_context->bias_frame_i_key) > 48) {
        status = MEF_ERR_CONFIG;
        goto done;
    }
    source_hdu = request->inputs[0].hdu_index;
    legacy_header_context->name_bias = strdup(request->inputs[0].resolved_path);
    if (legacy_header_context->name_bias == NULL) {
        status = MEF_ERR_MEMORY;
        goto done;
    }
    members = calloc(request->input_count, sizeof(*members));
    if (members == NULL) {
        status = MEF_ERR_MEMORY;
        goto done;
    }
    for (i = 0; i < request->input_count; ++i) {
        members[i] = (char *)request->inputs[i].resolved_path;
    }
    memset(&names, 0, sizeof(names));
    names.n = (int)request->input_count;
    names.name = members;
    legacy_header_context->bias_header_inputs = &names;
    legacy_header_context->bias_nframes = (int)bias_qc->input_frames;

    /* All helpers now see one statistics/configuration slot. Borrowed views
     * are detached before legacy destruction, including every error path. */

    legacy_header_context->bias_scan_median = (float *)bias_qc->scan_median;
    legacy_header_context->bias_scan_stdev = (float *)bias_qc->scan_stdev;
    legacy_header_context->bias_median_even_handling =
        (median_even_handling)bias_qc->median_even_handling;
    legacy_header_context->bias_avg1 = (float *)&bias_qc->frame_mean_average;
    legacy_header_context->bias_sig1 = (float *)&bias_qc->frame_mean_sigma;
    legacy_header_context->bias_framethr_lo = (float *)&bias_qc->rejection_low;
    legacy_header_context->bias_framethr_hi = (float *)&bias_qc->rejection_high;
    legacy_header_context->bias_median = (float *)&bias_qc->product_median;
    legacy_header_context->bias_stdev = (float *)&bias_qc->product_stdev;

    /* The legacy Phase3 helper requires both raw time cards (#24 unchanged).
     * Fail before calling atof(NULL); do not invent a time for missing cards. */

    primary_header = qfits_header_read(legacy_header_context->name_bias);
    if (primary_header == NULL || qfits_header_getstr(primary_header, "EXPTIME") == NULL ||
        qfits_header_getstr(primary_header, "MJD-OBS") == NULL ||
        qfits_header_getstr(primary_header, "ORIGFILE") == NULL) {
        status = MEF_ERR_INPUT;
        goto done;
    }
    qfits_header_destroy(primary_header);
    primary_header = NULL;
    mef_create_orig_filename(legacy_header_context, "bias");
    if (legacy_header_context->orig_bias == NULL) {
        status = MEF_ERR_MEMORY;
        goto done;
    }
    primary_header = mef_get_headers_for_hdu("bias", legacy_header_context, NULL, source_hdu);
    detector_header =
        mef_get_headers_for_hdu("bias", legacy_header_context, (image_t *)signal, source_hdu);
    if (primary_header == NULL || detector_header == NULL) {
        status = MEF_ERR_INPUT;
        goto done;
    }

    /* A raw primary image is written as one extension with an empty primary.
     * Existing MEF inputs preserve the old header policy byte for byte. */

    if (source_hdu == 0) {
        qfits_header *new_primary, *new_extension;
        new_primary = copy_primary_image_header(primary_header, signal, 1);
        new_extension = copy_primary_image_header(detector_header, signal, 0);
        if (new_primary == NULL || new_extension == NULL) {
            qfits_header_destroy(new_primary);
            qfits_header_destroy(new_extension);
            status = MEF_ERR_MEMORY;
            goto done;
        }
        qfits_header_destroy(primary_header);
        qfits_header_destroy(detector_header);
        primary_header = new_primary;
        detector_header = new_extension;
    }
    if (output_detector != NULL) {
        char value[80];
        char *old = qfits_header_getstr(detector_header, "EXTNAME");
        if (!*output_detector || strlen(output_detector) > 68 || strchr(output_detector, '\'') ||
            strchr(output_detector, '\n')) {
            status = MEF_ERR_INPUT;
            goto done;
        }
        if (old == NULL || strcmp(qfits_pretty_string(old), output_detector)) {
            snprintf(value, sizeof(value), "'%s'", output_detector);
            if (old == NULL) {
                qfits_header_add(detector_header, "EXTNAME", value, "Logical detector", NULL);
            } else {
                qfits_header_mod(detector_header, "EXTNAME", value, NULL);
            }
        }
    }
    if (additions != NULL) {
        char key[81], value[81], comment[81], line[81];
        int k;
        for (k = 0; k < additions->n; ++k) {
            if (qfits_header_getitem((qfits_header *)additions, k, key, value, comment, line) !=
                    0 ||
                strncmp(key, "HIERARCH ESO MPP QC ", 20)) {
                status = MEF_ERR_INPUT;
                goto done;
            }
            {
                const char *existing = qfits_header_getstr(detector_header, key);
                if (existing) {

                    /* This one card is emitted by both the legacy bias helper
                     * and typed QC. Keep it only if both explicitly agree. */

                    if (!strcmp(key, "HIERARCH ESO MPP QC MED EVEN") && !strcmp(existing, value)) {
                        continue;
                    }
                    status = MEF_ERR_INPUT;
                    goto done;
                }
            }
            qfits_header_add(detector_header, key, value, NULL, NULL);
            if (qfits_header_getstr(detector_header, key) == NULL) {
                status = MEF_ERR_MEMORY;
                goto done;
            }
        }
    }

    /* [BIAS-DETECTOR-WRITE]
     * Stage physical-ADU pixels and headers, then publish by an exclusive link.
     */

    path_length = strlen(final_path);
    if (path_length > (size_t)-1 - 32) {
        status = MEF_ERR_INPUT;
        goto done;
    }
    temporary_path = malloc(path_length + 32);
    if (temporary_path == NULL) {
        status = MEF_ERR_MEMORY;
        goto done;
    }
    strcpy(temporary_path, final_path);
    basename_start = strrchr(temporary_path, '/');
    strcpy(basename_start + 1, ".mefpp-bias-XXXXXX");
    temporary_descriptor = mkstemp(temporary_path);
    if (temporary_descriptor < 0) {
        temporary_path[0] = '\0';
        status = MEF_ERR_IO;
        goto done;
    }
    if (close(temporary_descriptor) != 0 ||
        mef_hdrpix_dump(NULL, temporary_path, primary_header, BPP_DEFAULT) != 0 ||
        mef_hdrpix_dump((image_t *)signal, temporary_path, detector_header, BPP_DEFAULT) != 0 ||
        link(temporary_path, final_path) != 0) {
        status = MEF_ERR_IO;
        goto done;
    }
    published = 1;
    status = MEF_OK;
    printf("BIAS_PRODUCT %s\nORIGFILE %s\n", final_path, legacy_header_context->orig_bias);
done:
    if (temporary_path != NULL && *temporary_path && unlink(temporary_path) != 0 && published) {
        e_warning("published bias is complete; output assembly remains: %s", temporary_path);
    }
    free(temporary_path);
    free(members);
    qfits_header_destroy(primary_header);
    qfits_header_destroy(detector_header);
    if (legacy_header_context != NULL) {
        legacy_header_context->bias_header_inputs = NULL;
        legacy_header_context->bias_scan_median = legacy_header_context->bias_scan_stdev = NULL;
        legacy_header_context->bias_avg1 = legacy_header_context->bias_sig1 = NULL;
        legacy_header_context->bias_framethr_lo = legacy_header_context->bias_framethr_hi = NULL;
        legacy_header_context->bias_median = legacy_header_context->bias_stdev = NULL;
        mef_bb_del(legacy_header_context);
    }
    if (status != MEF_OK) {
        return report_file_failure(status, "Bias publication failed; no success reported", error);
    }
    return status;
}

mef_status mef_bias_publish(const mef_config *config, const mef_bias_result *result,
    size_t configuration_detector, const char *final_path, mef_error **error)
{
    return mef_bias_publish_with_header(
        config, result, configuration_detector, final_path, NULL, error);
}

mef_status mef_bias_publish_with_header(const mef_config *config, const mef_bias_result *result,
    size_t detector, const char *path, const qfits_header *header, mef_error **error)
{
    return publish_bias_header(config, result, detector, path, header, NULL, error);
}

mef_status mef_bias_publish_with_header_named(const mef_config *config,
    const mef_bias_result *result, size_t detector, const char *path, const qfits_header *header,
    const char *id, mef_error **error)
{
    return publish_bias_header(config, result, detector, path, header, id, error);
}
