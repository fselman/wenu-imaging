#include "mef_bias_files.h"
#include "mefp_lib.h"
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>

static mef_status failed(mef_status status, const char *message, mef_error **error)
{
    if (error != NULL && *error == NULL)
        (void)mef_error_create(status, message, NULL, error);
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
static mef_status bias_validate(void *opaque, mef_error **error)
{
    bias_state *s;
    const mef_resolved_request_spec *request;
    const mef_bound_detector *first, *d;
    const mef_image_ref *ref;
    size_t i, entries;
    s = opaque;
    if (s->context == NULL || s->maps == NULL || s->detector == NULL || !*s->detector ||
        s->count == 0 || s->count > INT_MAX || s->count > (size_t)-1 / sizeof(*s->frames))
        return failed(MEF_ERR_INPUT, "Invalid mapped bias input", error);
    request = mef_request_resolved_view(mef_context_request(s->context));
    if (request == NULL || request->request.input_count != s->count ||
        request->request.operation != MEF_OP_CAL_BIAS ||
        request->bpm_selection_count != 1)
        return failed(MEF_ERR_UNSUPPORTED, "Bias adapter requires resolved BPM selection", error);
    if (s->measurements == NULL || s->measurements->bpm == NULL) {
        if (request->request.calibration_count != 0 || request->bpm_selections[0].state != MEF_BPM_OMITTED)
            return failed(MEF_ERR_UNSUPPORTED, "BPM map and request selection disagree", error);
    } else if (request->request.calibration_count != 1 ||
        request->calibration_roles[0] != MEF_CAL_BPM || request->bpm_selections[0].state != MEF_BPM_SELECTED)
        return failed(MEF_ERR_UNSUPPORTED, "BPM map and request selection disagree", error);
    first = mef_layout_find(s->maps[0], s->detector);
    if (first == NULL) return failed(MEF_ERR_INPUT, "Missing bias detector", error);
    s->configuration_detector = first->configuration_detector;
    for (i = 0; i < s->count; ++i) {
        ref = request->request.inputs + i;
        d = mef_layout_find(s->maps[i], s->detector);
        (void)mef_layout_map_view(s->maps[i], &entries);
        if (entries != 1 || d == NULL || d->selection != MEF_OUTPUT_SELECTED ||
            strcmp(d->unit, "ADU") || strcmp(ref->detector_id, s->detector) ||
            d->configuration_detector != first->configuration_detector ||
            d->image.hdu_index != ref->hdu_index ||
            (ref->extname != NULL && (!d->image.has_extname || !d->image.has_extver ||
             strcmp(ref->extname, d->image.extname) || ref->extver != d->image.extver)) ||
            mef_layout_compatible(s->maps[0], s->maps[i], "ADU", "ADU", NULL, NULL) != MEF_OK ||
            strcmp(mef_layout_map_path(s->maps[i]), ref->resolved_path))
            return failed(MEF_ERR_INPUT, "Bias map/request or readout mismatch", error);
    }
    return MEF_OK;
}
static mef_status bias_load(void *opaque, mef_error **error)
{
    bias_state *s;
    mef_status status;
    size_t i;
    s = opaque;
    s->frames = calloc(s->count, sizeof(*s->frames));
    s->borrowed = calloc(s->count, sizeof(*s->borrowed));
    if (s->frames == NULL || s->borrowed == NULL)
        return failed(MEF_ERR_MEMORY, "Cannot allocate bias plane handles", error);
    for (i = 0; i < s->count; ++i) {
        status = mef_layout_load(s->maps[i], s->detector, s->frames + i, error);
        if (status != MEF_OK) return status;
        s->borrowed[i] = s->frames[i];
    }
    return MEF_OK;
}
static mef_status bias_calculate(void *opaque, mef_error **error)
{
    bias_state *s;
    mef_bias_input input;
    s = opaque;
    input.frames = s->borrowed; input.count = s->count;
    input.configuration_detector = s->configuration_detector;
    return mef_cal_bias_measurements(s->context, &input, s->measurements, &s->pending, error);
}
static mef_status bias_publish_step(void *opaque, mef_error **error)
{
    bias_state *s;
    s = opaque;
    return mef_bias_publish(mef_context_config(s->context), s->pending,
        s->configuration_detector, s->final_path, error);
}
static void bias_cleanup(void *opaque)
{
    bias_state *s;
    size_t i;
    s = opaque;
    if (s->frames != NULL) for (i = 0; i < s->count; ++i) image_del(s->frames[i]);
    free(s->frames); free(s->borrowed);
    s->frames = NULL; s->borrowed = NULL;
}
static mef_status bias_run(mef_context *context,
    const mef_layout_map *const *maps, size_t count, const char *detector,
    const char *final_path, const mef_bias_measurement_options *measurements,
    mef_bias_result **out, mef_error **error)
{
    bias_state state;
    mef_operation_steps steps;
    mef_status status;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    memset(&state, 0, sizeof(state)); state.context = context; state.maps = maps;
    state.measurements = measurements;
    state.count = count; state.detector = detector; state.final_path = final_path;
    steps.validate = bias_validate; steps.load = bias_load;
    steps.calculate = bias_calculate; steps.publish = final_path ? bias_publish_step : NULL;
    steps.cleanup = bias_cleanup;
    status = mef_operation_run(&steps, &state, error);
    if (status == MEF_OK) *out = state.pending;
    else mef_bias_result_destroy(state.pending);
    return status;
}
mef_status mef_bias_from_files(mef_context *context,
    const mef_layout_map *const *maps, size_t count, const char *detector,
    mef_bias_result **out, mef_error **error)
{
    return bias_run(context, maps, count, detector, NULL, NULL, out, error);
}
mef_status mef_bias_files_execute(mef_context *context,
    const mef_layout_map *const *maps, size_t count, const char *detector,
    const char *final_path, mef_bias_result **out, mef_error **error)
{
    if (final_path == NULL) return MEF_ERR_INPUT;
    return bias_run(context, maps, count, detector, final_path, NULL, out, error);
}

mef_status mef_bias_files_execute_measurements(mef_context *context,
    const mef_layout_map *const *maps, size_t count, const char *detector,
    const char *final_path, const mef_bias_measurement_options *measurements,
    mef_bias_result **out, mef_error **error)
{
    if (final_path == NULL || measurements == NULL) return MEF_ERR_INPUT;
    return bias_run(context, maps, count, detector, final_path, measurements, out, error);
}

mef_status mef_bias_from_files_measurements(mef_context *context,
    const mef_layout_map *const *maps, size_t count, const char *detector,
    const mef_bias_measurement_options *measurements,
    mef_bias_result **out, mef_error **error)
{
    if (measurements == NULL) return MEF_ERR_INPUT;
    return bias_run(context, maps, count, detector, NULL, measurements, out, error);
}

/* #211/#212: qfits_header_del leaves n stale. qfits_header_copy traverses
 * forward links and rebuilds n via append. Never index the deleted source or
 * merge it as an update. Build the required structural prefix without deletion.
 * Existing extension-input publication does not enter this conversion. */
static int structural_key(const char *key)
{
    return !strcmp(key, "SIMPLE") || !strcmp(key, "XTENSION") ||
        !strcmp(key, "BITPIX") || !strcmp(key, "NAXIS") ||
        !strcmp(key, "NAXIS1") || !strcmp(key, "NAXIS2") || !strcmp(key, "NAXIS3") ||
        !strcmp(key, "PCOUNT") || !strcmp(key, "GCOUNT") ||
        !strcmp(key, "EXTEND") || !strcmp(key, "BSCALE") ||
        !strcmp(key, "BZERO") || !strcmp(key, "END");
}
static qfits_header *primary_image_header(qfits_header *source,
    const image_t *signal, int is_primary)
{
    qfits_header *copy, *out;
    char value[32], key[FITS_LINESZ + 1], val[FITS_LINESZ + 1];
    char comment[FITS_LINESZ + 1], line[FITS_LINESZ + 1];
    int i;
    copy = qfits_header_copy(source);
    if (copy == NULL) return NULL;
    out = qfits_header_new();
    if (out == NULL) { qfits_header_destroy(copy); return NULL; }
    qfits_header_append(out, is_primary ? "SIMPLE" : "XTENSION",
        is_primary ? "T" : "IMAGE", NULL, NULL);
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
            qfits_header_destroy(copy); qfits_header_destroy(out); return NULL;
        }
        if (!structural_key(key))
            qfits_header_append(out, key, *val ? val : NULL,
                *comment ? comment : NULL, *line ? line : NULL);
    }
    qfits_header_append(out, "END", NULL, NULL, NULL);
    qfits_header_destroy(copy);
    return out;
}

static mef_status publish_header(const mef_config *config,
    const mef_bias_result *result, size_t configuration_detector,
    const char *final_path, const qfits_header *additions, const char *output_detector, mef_error **error)
{
    const mef_request_spec *request;
    const mef_bias_qc *qc;
    const image_t *signal;
    mef_bb *bb;
    qfits_header *primary, *extension;
    framelist names;
    char **members, *temporary, *slash;
    int fd, source_hdu, committed;
    size_t i, n;
    mef_status status;
    if (error != NULL && *error != NULL) return MEF_ERR_INPUT;
    if (result == NULL || final_path == NULL || final_path[0] != '/')
        return failed(MEF_ERR_INPUT, "Require an absolute new bias output", error);
    request = mef_request_view(mef_bias_result_request(result));
    qc = mef_bias_result_qc(result); signal = mef_bias_result_signal(result);
    if (request == NULL || qc == NULL || signal == NULL || request->input_count == 0 ||
        request->input_count > INT_MAX || request->input_count > (size_t)-1 / sizeof(*members))
        return failed(MEF_ERR_INPUT, "Incomplete bias result", error);
    bb = NULL; primary = extension = NULL; members = NULL; temporary = NULL;
    committed = 0;
    status = mef_config_bias_header_context(config, configuration_detector, &bb);
    if (status != MEF_OK) goto done;
    /* Bound the existing legacy 80-byte creation-name formatter. This is not
     * a clock/naming correction or a new filename grammar (#207 stays open). */
    if (strlen(bb->instrument) > 24 || strlen(bb->recipe_key) > 48 ||
        strlen(bb->bias_frame_i_key) > 48) { status = MEF_ERR_CONFIG; goto done; }
    source_hdu = request->inputs[0].hdu_index;
    bb->name_bias = strdup(request->inputs[0].resolved_path);
    if (bb->name_bias == NULL) { status = MEF_ERR_MEMORY; goto done; }
    members = calloc(request->input_count, sizeof(*members));
    if (members == NULL) { status = MEF_ERR_MEMORY; goto done; }
    for (i = 0; i < request->input_count; ++i)
        members[i] = (char *)request->inputs[i].resolved_path;
    memset(&names, 0, sizeof(names)); names.n = (int)request->input_count;
    names.name = members; bb->bias_header_inputs = &names;
    bb->bias_nframes = (int)qc->input_frames;
    /* All helpers now see one statistics/configuration slot. Borrowed views
     * are detached before legacy destruction, including every error path. */
    bb->bias_scan_median = (float *)qc->scan_median;
    bb->bias_scan_stdev = (float *)qc->scan_stdev;
    bb->bias_avg1 = (float *)&qc->frame_mean_average;
    bb->bias_sig1 = (float *)&qc->frame_mean_sigma;
    bb->bias_framethr_lo = (float *)&qc->rejection_low;
    bb->bias_framethr_hi = (float *)&qc->rejection_high;
    bb->bias_median = (float *)&qc->product_median;
    bb->bias_stdev = (float *)&qc->product_stdev;
    /* The legacy Phase3 helper requires both raw time cards (#24 unchanged).
     * Fail before calling atof(NULL); do not invent a time for missing cards. */
    primary = qfits_header_read(bb->name_bias);
    if (primary == NULL || qfits_header_getstr(primary, "EXPTIME") == NULL ||
        qfits_header_getstr(primary, "MJD-OBS") == NULL ||
        qfits_header_getstr(primary, "ORIGFILE") == NULL) {
        status = MEF_ERR_INPUT; goto done;
    }
    qfits_header_destroy(primary); primary = NULL;
    mef_create_orig_filename(bb, "bias");
    if (bb->orig_bias == NULL) { status = MEF_ERR_MEMORY; goto done; }
    primary = mef_get_headers_for_hdu("bias", bb, NULL, source_hdu);
    extension = mef_get_headers_for_hdu("bias", bb, (image_t *)signal, source_hdu);
    if (primary == NULL || extension == NULL) { status = MEF_ERR_INPUT; goto done; }
    /* A raw primary image is written as one extension with an empty primary.
     * Existing MEF inputs preserve the old header policy byte for byte. */
    if (source_hdu == 0) {
        qfits_header *new_primary, *new_extension;
        new_primary = primary_image_header(primary, signal, 1);
        new_extension = primary_image_header(extension, signal, 0);
        if (new_primary == NULL || new_extension == NULL) {
            qfits_header_destroy(new_primary); qfits_header_destroy(new_extension);
            status = MEF_ERR_MEMORY; goto done;
        }
        qfits_header_destroy(primary); qfits_header_destroy(extension);
        primary = new_primary; extension = new_extension;
    }
    if (output_detector != NULL) {
        char value[80];
        char *old = qfits_header_getstr(extension, "EXTNAME");
        if (!*output_detector || strlen(output_detector) > 68 ||
            strchr(output_detector, '\'') || strchr(output_detector, '\n')) {
            status = MEF_ERR_INPUT; goto done;
        }
        if (old == NULL || strcmp(qfits_pretty_string(old), output_detector)) {
            snprintf(value, sizeof(value), "'%s'", output_detector);
            if (old == NULL) qfits_header_add(extension, "EXTNAME", value, "Logical detector", NULL);
            else qfits_header_mod(extension, "EXTNAME", value, NULL);
        }
    }
    if (additions != NULL) {
        char key[81], value[81], comment[81], line[81];
        int k;
        for (k = 0; k < additions->n; ++k) {
            if (qfits_header_getitem((qfits_header *)additions, k, key, value, comment, line) != 0 ||
                strncmp(key, "HIERARCH ESO MPP QC ", 20) ||
                qfits_header_getstr(extension, key) != NULL) {
                status = MEF_ERR_INPUT; goto done;
            }
            qfits_header_add(extension, key, value, NULL, NULL);
            if (qfits_header_getstr(extension, key) == NULL) {
                status = MEF_ERR_MEMORY; goto done;
            }
        }
    }
    n = strlen(final_path);
    if (n > (size_t)-1 - 32) { status = MEF_ERR_INPUT; goto done; }
    temporary = malloc(n + 32);
    if (temporary == NULL) { status = MEF_ERR_MEMORY; goto done; }
    strcpy(temporary, final_path); slash = strrchr(temporary, '/');
    strcpy(slash + 1, ".mefpp-bias-XXXXXX");
    fd = mkstemp(temporary);
    if (fd < 0) { temporary[0] = '\0'; status = MEF_ERR_IO; goto done; }
    if (close(fd) != 0 || mef_hdrpix_dump(NULL, temporary, primary, BPP_DEFAULT) != 0 ||
        mef_hdrpix_dump((image_t *)signal, temporary, extension, BPP_DEFAULT) != 0 ||
        link(temporary, final_path) != 0) { status = MEF_ERR_IO; goto done; }
    committed = 1; status = MEF_OK;
    printf("BIAS_PRODUCT %s\nORIGFILE %s\n", final_path, bb->orig_bias);
done:
    if (temporary != NULL && *temporary && unlink(temporary) != 0 && committed)
        e_warning("published bias is complete; output assembly remains: %s", temporary);
    free(temporary); free(members);
    qfits_header_destroy(primary); qfits_header_destroy(extension);
    if (bb != NULL) {
        bb->bias_header_inputs = NULL;
        bb->bias_scan_median = bb->bias_scan_stdev = NULL;
        bb->bias_avg1 = bb->bias_sig1 = NULL;
        bb->bias_framethr_lo = bb->bias_framethr_hi = NULL;
        bb->bias_median = bb->bias_stdev = NULL;
        mef_bb_del(bb);
    }
    if (status != MEF_OK) return failed(status, "Bias publication failed; no success reported", error);
    return status;
}

mef_status mef_bias_publish(const mef_config *config,
    const mef_bias_result *result, size_t configuration_detector,
    const char *final_path, mef_error **error)
{
    return mef_bias_publish_with_header(config, result, configuration_detector,
        final_path, NULL, error);
}

mef_status mef_bias_publish_with_header(const mef_config *config,
    const mef_bias_result *result, size_t detector, const char *path,
    const qfits_header *header, mef_error **error)
{ return publish_header(config,result,detector,path,header,NULL,error); }
mef_status mef_bias_publish_with_header_named(const mef_config *config,
    const mef_bias_result *result, size_t detector, const char *path,
    const qfits_header *header, const char *id, mef_error **error)
{ return publish_header(config,result,detector,path,header,id,error); }
