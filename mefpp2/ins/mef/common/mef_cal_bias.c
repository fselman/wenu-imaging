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
static int finite_value(double value)
{
    return value == value && value >= -DBL_MAX && value <= DBL_MAX;
}
static int interval(const int *pair, int width)
{
    return pair[0] >= 1 && pair[1] >= pair[0] && pair[1] <= width;
}
static mef_status validate(mef_context *context, const mef_bias_input *input,
    mef_bias_settings *settings)
{
    const mef_request_spec *request;
    const mef_resolved_request_spec *resolved;
    size_t i, j, pixels;
    int width, height, scan_width;
    if (context == NULL || input == NULL || input->frames == NULL ||
        input->count == 0 || input->count > INT_MAX ||
        input->count > (size_t)-1 / sizeof(double)) return MEF_ERR_INPUT;
    resolved = mef_request_resolved_view(mef_context_request(context));
    if (resolved == NULL) return MEF_ERR_INPUT;
    request = &resolved->request;
    if (request->operation != MEF_OP_CAL_BIAS || request->operation_version != 1 ||
        request->input_count != input->count) return MEF_ERR_INPUT;
    /* This first concrete service has no calibration application kernel. */
    if (request->calibration_count != 0) return MEF_ERR_UNSUPPORTED;
    if (resolved->bpm_selection_count != 1) return MEF_ERR_UNSUPPORTED;
    if (resolved->bpm_selections[0].state != MEF_BPM_OMITTED)
        return MEF_ERR_UNSUPPORTED;
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
        /* Initial CCD/MEF lane. Primary images remain M4, not guessed here. */
        if (request->inputs[i].hdu_index == 0) return MEF_ERR_UNSUPPORTED;
        if (input->frames[i] == NULL || input->frames[i]->data == NULL ||
            input->frames[i]->lx != width || input->frames[i]->ly != height)
            return MEF_ERR_INPUT;
        for (j = 0; j < pixels; ++j)
            if (!finite_value(input->frames[i]->data[j])) return MEF_ERR_INPUT;
    }
    return MEF_OK;
}

mef_status mef_cal_bias(mef_context *context, const mef_bias_input *input,
    mef_bias_result **out, mef_error **error)
{
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
    cube = NULL;
    names = NULL;
    a = mef_context_allocator(context);
    status = validate(context, input, &settings);
    if (status != MEF_OK) goto cleanup;
    resolved = mef_request_resolved_view(mef_context_request(context));

    /* Construct a safely destructible pending owner, before numerical work. */
    detail = "Cannot allocate pending bias result or QC arrays";
    status = MEF_ERR_MEMORY;
    pending = a->allocate(a->user, sizeof(*pending));
    if (pending == NULL) goto cleanup;
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
        cropped = mef_overscan_correction(cube->plane[i], &work, (int)i, "bias");
        if (cropped == NULL) goto cleanup;
        image_del(cube->plane[i]);
        cube->plane[i] = cropped;
    }
    cube->lx = cube->plane[0]->lx;
    cube->ly = cube->plane[0]->ly;
    detail = "Bias rejection or median stacking failed; no result transferred";
    pending->signal = mef_bias_stack(cube, settings.minimum_frames,
        settings.kappa, &stats, (int *)pending->qc.accepted);
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
    *out = pending;
    pending = NULL;
    status = MEF_OK;
cleanup:
    cube_del(cube);
    if (a != NULL) release(a, names);
    mef_bias_result_destroy(pending);
    if (status != MEF_OK && error != NULL && *error == NULL)
        (void)mef_error_create(status, detail, a, error);
    return status;
}
