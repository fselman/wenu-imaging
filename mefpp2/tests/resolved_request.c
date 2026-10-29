/* Metadata/ownership controls only; deliberately nonexistent absolute paths. */
#include "mef_runtime.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

typedef struct { size_t calls, owners, fail_at; int persistent; } memory_state;
static void *test_allocate(void *user, size_t size)
{
    memory_state *s;
    void *p;
    s = user;
    ++s->calls;
    if (s->fail_at && (s->calls == s->fail_at ||
        (s->persistent && s->calls >= s->fail_at))) return NULL;
    p = malloc(size);
    if (p != NULL) ++s->owners;
    return p;
}
static void test_release(void *user, void *p)
{
    memory_state *s;
    s = user;
    assert(p != NULL && s->owners != 0);
    --s->owners;
    free(p);
}
static size_t attempt(const mef_config *config, const mef_resolved_request_spec *spec,
    const mef_request *original, int context_mode, size_t failure, int persistent)
{
    memory_state s;
    mef_allocator a;
    mef_request *request;
    mef_context *context;
    mef_error *error;
    mef_status status;
    size_t calls;
    s.calls = s.owners = 0; s.fail_at = failure; s.persistent = persistent;
    a.user = &s; a.allocate = test_allocate; a.release = test_release;
    request = NULL; context = NULL; error = NULL;
    if (context_mode) status = mef_context_create(config, original, &a, &context, &error);
    else status = mef_request_create_resolved(spec, &a, &request, &error);
    calls = s.calls;
    if (failure) {
        assert(status == MEF_ERR_MEMORY && request == NULL && context == NULL);
        if (persistent) assert(error == NULL);
        else assert(mef_error_status(error) == MEF_ERR_MEMORY);
    } else {
        const mef_resolved_request_spec *view;
        assert(status == MEF_OK && error == NULL);
        view = mef_request_resolved_view(context_mode ? mef_context_request(context) : request);
        assert(view != NULL && view->calibration_roles[1] == MEF_CAL_BPM);
        assert(view->bpm_selections[0].state == MEF_BPM_SELECTED);
        assert(view->bpm_selections[1].state == MEF_BPM_OMITTED);
    }
    mef_request_destroy(request); mef_context_destroy(context); mef_error_destroy(error);
    assert(s.owners == 0);
    return calls;
}

void test_resolved_request(const mef_config *config)
{
    mef_image_ref inputs[3], calibrations[2], invalid;
    mef_calibration_role roles[2], role;
    mef_bpm_selection selections[2], bad_selections[2];
    mef_resolved_request_spec spec, bad;
    mef_request *request, *alias, *legacy;
    mef_context *context;
    mef_result *result;
    mef_error *error, *error_alias;
    mef_allocator bad_allocator;
    const mef_resolved_request_spec *view;
    size_t calls, failure, total;
    int mode, cycle, operation;
    char detector[16];
    strcpy(detector, "CCD-A");
    inputs[0].asset_record_id = "input:one"; inputs[0].detector_id = detector;
    inputs[0].resolved_path = "/not-opened/input one.fits";
    inputs[0].hdu_index = 0; inputs[0].extname = NULL; inputs[0].extver = 0;
    inputs[1] = inputs[0]; inputs[1].asset_record_id = "input:two";
    inputs[1].detector_id = "CCD-B"; inputs[1].hdu_index = 5;
    inputs[1].extname = "CHIP-B"; inputs[1].extver = 2;
    inputs[2] = inputs[0]; inputs[2].asset_record_id = "input:three";
    calibrations[0] = inputs[0]; calibrations[0].asset_record_id = "cal:bias";
    calibrations[1] = inputs[0]; calibrations[1].asset_record_id = "cal:bpm";
    calibrations[1].resolved_path = "/not-opened/selected bpm.fits";
    roles[0] = MEF_CAL_BIAS; roles[1] = MEF_CAL_BPM;
    selections[0].detector_id = detector; selections[0].state = MEF_BPM_SELECTED;
    selections[1].detector_id = "CCD-B"; selections[1].state = MEF_BPM_OMITTED;
    spec.request.operation = MEF_OP_SCI_PP; spec.request.operation_version = 1;
    spec.request.inputs = inputs; spec.request.input_count = 3;
    spec.request.calibrations = calibrations; spec.request.calibration_count = 2;
    spec.request.work_dir = "/work"; spec.request.output_dir = "/products";
    spec.request.log_path = "/logs/run.log";
    spec.calibration_roles = roles; spec.calibration_role_count = 2;
    spec.bpm_selections = selections; spec.bpm_selection_count = 2;
    request = NULL; legacy = NULL; context = NULL; error = NULL; result = NULL;
    assert(mef_request_create_resolved(&spec, NULL, &request, &error) == MEF_OK);
    alias = request;
    assert(mef_request_create_resolved(&spec, NULL, &request, &error) == MEF_ERR_INPUT);
    assert(request == alias && error == NULL);
    assert(mef_context_create(config, request, NULL, &context, &error) == MEF_OK);
    total = 0;
    /* Every added allocation and context-clone failure must clean up. */
    for (mode = 0; mode < 2; ++mode) {
        calls = attempt(config, &spec, request, mode, 0, 0);
        total += calls;
        for (failure = 1; failure <= calls; ++failure) {
            (void)attempt(config, &spec, request, mode, failure, 0);
            (void)attempt(config, &spec, request, mode, failure, 1);
        }
        for (cycle = 0; cycle < 20; ++cycle)
            (void)attempt(config, &spec, request, mode, 0, 0);
    }
    mef_request_destroy(request); request = NULL;
    /* A context must not lose bindings or borrow mutable caller strings. */
    strcpy(detector, "mutated"); roles[1] = MEF_CAL_DARK;
    selections[0].state = MEF_BPM_OMITTED;
    view = mef_request_resolved_view(mef_context_request(context));
    assert(view != NULL && strcmp(view->bpm_selections[0].detector_id, "CCD-A") == 0);
    assert(strcmp(view->request.inputs[0].detector_id, "CCD-A") == 0);
    assert(view->request.inputs[1].hdu_index == 5);
    assert(view->request.inputs[1].extver == 2);
    assert(view->calibration_roles[1] == MEF_CAL_BPM);
    assert(view->bpm_selections[0].state == MEF_BPM_SELECTED);
    assert(mef_execute(context, &result, &error) == MEF_ERR_UNSUPPORTED);
    assert(result == NULL);
    mef_context_destroy(context); context = NULL;
    assert(mef_error_status(error) == MEF_ERR_UNSUPPORTED);
    mef_error_destroy(error); error = NULL;
    strcpy(detector, "CCD-A"); roles[1] = MEF_CAL_BPM;
    selections[0].state = MEF_BPM_SELECTED;
    /* Existing untyped requests stay untyped, including through context copy. */
    assert(mef_request_create(&spec.request, NULL, &legacy, &error) == MEF_OK);
    assert(mef_request_resolved_view(legacy) == NULL);
    assert(mef_context_create(config, legacy, NULL, &context, &error) == MEF_OK);
    assert(mef_request_resolved_view(mef_context_request(context)) == NULL);
    mef_request_destroy(legacy); mef_context_destroy(context); context = NULL;
    assert(mef_request_resolved_view(NULL) == NULL);
    /* Omitted BPM works at the metadata boundary for all nine operations.
     * This is not operation-specific numerical applicability/acceptance. */
    bad = spec; bad.request.calibrations = NULL; bad.request.calibration_count = 0;
    bad.calibration_roles = NULL; bad.calibration_role_count = 0;
    selections[0].state = MEF_BPM_OMITTED;
    for (operation = MEF_OP_CAL_BIAS; operation <= MEF_OP_SCI_PP; ++operation) {
        bad.request.operation = (mef_operation)operation;
        assert(mef_request_create_resolved(&bad, NULL, &request, &error) == MEF_OK);
        assert(mef_request_resolved_view(request)->calibration_role_count == 0);
        mef_request_destroy(request); request = NULL;
    }
    /* All eight roles survive construction without filename inference. */
    bad = spec; bad.request.calibration_count = 1; bad.calibration_role_count = 1;
    for (role = MEF_CAL_BIAS; role <= MEF_CAL_MFF; role = (mef_calibration_role)(role + 1)) {
        roles[0] = role;
        selections[0].state = role == MEF_CAL_BPM ? MEF_BPM_SELECTED : MEF_BPM_OMITTED;
        assert(mef_request_create_resolved(&bad, NULL, &request, &error) == MEF_OK);
        assert(mef_request_resolved_view(request)->calibration_roles[0] == role);
        mef_request_destroy(request); request = NULL;
    }
    roles[0] = MEF_CAL_BIAS; selections[0].state = MEF_BPM_SELECTED;
    /* Reject contradictory/incomplete choices; never downgrade selection. */
    for (mode = 0; mode < 17; ++mode) {
        bad = spec; bad_selections[0] = selections[0]; bad_selections[1] = selections[1];
        bad.bpm_selections = bad_selections;
        if (mode == 0) bad.calibration_role_count = 1;
        if (mode == 1) bad.calibration_roles = NULL;
        if (mode == 2) bad.bpm_selection_count = 0;
        if (mode == 3) bad.bpm_selections = NULL;
        if (mode == 4) bad_selections[0].state = (mef_bpm_selection_state)0;
        if (mode == 5) bad_selections[1].detector_id = "CCD-A";
        if (mode == 6) bad_selections[1].detector_id = "unselected detector";
        if (mode == 7) bad_selections[0].detector_id = NULL;
        if (mode == 8) bad_selections[0].state = MEF_BPM_OMITTED;
        if (mode == 9) bad_selections[1].state = MEF_BPM_SELECTED;
        if (mode == 10) { bad.request.calibration_count = 1; bad.calibration_role_count = 1; }
        if (mode == 11) roles[0] = MEF_CAL_BPM;
        if (mode == 12) roles[0] = (mef_calibration_role)0;
        if (mode == 13) bad.bpm_selection_count = (size_t)-1;
        if (mode == 14) bad.calibration_role_count = (size_t)-1;
        if (mode == 15) {
            invalid = calibrations[0]; invalid.detector_id = "unselected detector";
            bad.request.calibrations = &invalid; bad.request.calibration_count = 1;
            bad.calibration_role_count = 1;
        }
        if (mode == 16) {
            invalid = calibrations[1]; invalid.resolved_path = "relative-bpm.fits";
            bad.request.calibrations = &invalid; bad.request.calibration_count = 1;
            roles[0] = MEF_CAL_BPM; bad.calibration_role_count = 1;
        }
        assert(mef_request_create_resolved(&bad, NULL, &request, &error) == MEF_ERR_INPUT);
        assert(request == NULL && mef_error_status(error) == MEF_ERR_INPUT);
        mef_error_destroy(error); error = NULL; roles[0] = MEF_CAL_BIAS;
    }
    assert(mef_request_create_resolved(NULL, NULL, &request, NULL) == MEF_ERR_INPUT);
    assert(mef_request_create_resolved(&spec, NULL, NULL, NULL) == MEF_ERR_INPUT);
    bad_allocator.user = NULL; bad_allocator.allocate = NULL; bad_allocator.release = NULL;
    assert(mef_request_create_resolved(&spec, &bad_allocator, &request, &error) == MEF_ERR_CONFIG);
    assert(request == NULL && error == NULL);
    assert(mef_error_create(MEF_ERR_INPUT, "existing", NULL, &error) == MEF_OK);
    error_alias = error;
    assert(mef_request_create_resolved(&spec, NULL, &request, &error) == MEF_ERR_INPUT);
    assert(error == error_alias && request == NULL);
    mef_error_destroy(error);
    printf("PASS: resolved roles/BPM metadata; 9 operations, 8 roles, 17 rejected bindings; %lu transient+persistent allocation positions; 20 cycles\n", (unsigned long)total);
}
