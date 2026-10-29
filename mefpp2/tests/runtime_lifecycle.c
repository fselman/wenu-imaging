/* Lifecycle-only controls. No native recipe, image processing or FITS I/O. */
#include "mef_runtime.h"
#include "mefp_lib.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

typedef struct { size_t calls, fail_at, owners; int persistent; } allocation_state;
static void *allocate(void *user, size_t bytes)
{
    allocation_state *s;
    void *p;
    s = user;
    ++s->calls;
    if (s->fail_at && (s->calls == s->fail_at ||
                      (s->persistent && s->calls >= s->fail_at))) return NULL;
    p = (malloc)(bytes);
    if (p != NULL) ++s->owners;
    return p;
}
static void release(void *user, void *pointer)
{
    allocation_state *s;
    s = user;
    assert(pointer != NULL && s->owners > 0);
    --s->owners;
    (free)(pointer);
}
static void fixture_release(mef_bb *source)
{
#define MEF_STRING(member, key) (free)(source->member);
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    (free)(source->ccd);
}
#include "config_snapshot_fixture.h"

void test_resolved_request(const mef_config *config);

static size_t exercise(int mode, const mef_config *config,
    const mef_request *original, const mef_request_spec *spec,
    const mef_allocator *allocator, size_t fail_at, int persistent)
{
    allocation_state *state;
    mef_request *request;
    mef_context *context;
    mef_result *result;
    mef_error *error;
    mef_config *copy;
    const char *diagnostic;
    mef_status status;
    size_t calls;
    state = allocator->user;
    state->calls = state->owners = 0;
    state->fail_at = fail_at; state->persistent = persistent;
    request = NULL; context = NULL; result = NULL; error = NULL; copy = NULL;
    if (mode == 0) status = mef_request_create(spec, allocator, &request, &error);
    else if (mode == 1) status = mef_context_create(config, original, allocator, &context, &error);
    else if (mode == 2) status = mef_result_create(spec->operation, spec->inputs,
                               spec->input_count, allocator, &result, &error);
    else if (mode == 3) status = mef_error_create(MEF_ERR_INPUT, "owned error", allocator, &error);
    else status = mef_config_clone(config, allocator, &copy, &diagnostic);
    calls = state->calls;
    if (fail_at) {
        assert(status == MEF_ERR_MEMORY);
        assert(request == NULL && context == NULL && result == NULL && copy == NULL);
        if (persistent || mode == 3 || mode == 4) assert(error == NULL);
        else assert(mef_error_status(error) == MEF_ERR_MEMORY);
    } else assert(status == MEF_OK);
    mef_request_destroy(request); mef_context_destroy(context);
    mef_result_destroy(result); mef_error_destroy(error); mef_config_destroy(copy);
    assert(state->owners == 0);
    return calls;
}

int main(int argc, char **argv)
{
    mef_bb legacy;
    mef_config *config;
    mef_request *request, *request_alias, *second_request;
    mef_context *context, *context_alias, *second_context;
    mef_result *result, *result_alias;
    mef_error *error, *error_alias;
    mef_image_ref refs[2], calibrations[1], invalid;
    mef_request_spec spec, bad_spec;
    const mef_request_spec *view;
    const mef_image_ref *products;
    mef_allocator allocator, bad_allocator;
    allocation_state state;
    const char *diagnostic;
    size_t count, calls, failure, total;
    int mode, cycle;
    FILE *stream;
    char asset[32], path[64], message[32];
    assert(argc == 3);
    fixture_init(&legacy, argv[1]);
    if (strcmp(argv[1], "override") == 0) {
        legacy.bias_kappa1 = 0.123456789012345;
        legacy.pixrej_lo = 0.234567890123456;
        legacy.scanrej[0] = 7;
    }
    config = NULL; request = NULL; context = NULL;
    result = NULL; error = NULL;
    assert(mef_config_from_legacy(&legacy, NULL, &config, &diagnostic) == MEF_OK);
    fixture_release(&legacy);
    test_resolved_request(config);
    strcpy(asset, "asset:primary"); strcpy(path, "/input with spaces/primary.fits");
    refs[0].asset_record_id = asset; refs[0].detector_id = "detector-primary";
    refs[0].resolved_path = path; refs[0].hdu_index = 0;
    refs[0].extname = NULL; refs[0].extver = 0;
    refs[1] = refs[0]; refs[1].asset_record_id = "asset:mef";
    refs[1].resolved_path = "/inputs/mef.fits";
    refs[1].detector_id = "WIN1.CHIP8.OUT1";
    refs[1].hdu_index = 5; refs[1].extname = "WIN1.CHIP8.OUT1"; refs[1].extver = 1;
    calibrations[0] = refs[1]; calibrations[0].asset_record_id = "calibration:bias";
    spec.operation = MEF_OP_SCI_PP; spec.operation_version = 1;
    spec.inputs = refs; spec.input_count = 2;
    spec.calibrations = calibrations; spec.calibration_count = 1;
    spec.work_dir = "/work space"; spec.output_dir = "/output"; spec.log_path = "/logs/run.log";
    assert(mef_request_create(&spec, NULL, &request, &error) == MEF_OK);
    assert(error == NULL);
    request_alias = request;
    assert(mef_request_create(&spec, NULL, &request, &error) == MEF_ERR_INPUT);
    assert(request == request_alias && error == NULL);
    assert(mef_context_create(config, request, NULL, &context, &error) == MEF_OK);
    context_alias = context;
    assert(mef_context_create(config, request, NULL, &context, &error) == MEF_ERR_INPUT);
    assert(context == context_alias && error == NULL);
    second_request = NULL; second_context = NULL;
    bad_spec = spec; bad_spec.operation = MEF_OP_CAL_BIAS;
    bad_spec.work_dir = "/independent work";
    assert(mef_request_create(&bad_spec, NULL, &second_request, &error) == MEF_OK);
    assert(mef_context_create(config, second_request, NULL, &second_context, &error) == MEF_OK);
    mef_request_destroy(second_request);
    assert(mef_request_view(mef_context_request(second_context))->operation == MEF_OP_CAL_BIAS);
    assert(mef_request_view(mef_context_request(context))->operation == MEF_OP_SCI_PP);
    assert(strcmp(mef_request_view(mef_context_request(context))->work_dir, "/work space") == 0);
    mef_context_destroy(second_context);
    allocator.user = &state; allocator.allocate = allocate; allocator.release = release;
    total = 0;
    for (mode = 0; mode < 5; ++mode) {
        calls = exercise(mode, config, request, &spec, &allocator, 0, 0);
        for (failure = 1; failure <= calls; ++failure) {
            (void)exercise(mode, config, request, &spec, &allocator, failure, 0);
            (void)exercise(mode, config, request, &spec, &allocator, failure, 1);
        }
        total += calls;
        for (cycle = 0; cycle < 20; ++cycle)
            (void)exercise(mode, config, request, &spec, &allocator, 0, 0);
    }
    /* Invalid descriptors and occupied error handles do not overwrite owners. */
    assert(mef_error_create(MEF_ERR_INPUT, "existing", NULL, &error) == MEF_OK);
    error_alias = error;
    assert(mef_request_create(&spec, NULL, &request, &error) == MEF_ERR_INPUT);
    assert(error == error_alias && request == request_alias);
    assert(mef_execute(context, &result, &error) == MEF_ERR_INPUT);
    assert(error == error_alias && result == NULL);
    mef_error_destroy(error); error = NULL;
    bad_spec = spec; bad_spec.operation_version = 99;
    mef_request_destroy(request); request = NULL;
    assert(mef_request_create(&bad_spec, NULL, &request, &error) == MEF_ERR_UNSUPPORTED);
    assert(request == NULL && mef_error_status(error) == MEF_ERR_UNSUPPORTED);
    mef_error_destroy(error); error = NULL;
    state.calls = state.owners = 0; state.fail_at = 1; state.persistent = 1;
    assert(mef_request_create(&bad_spec, &allocator, &request, &error) == MEF_ERR_UNSUPPORTED);
    assert(request == NULL && error == NULL && state.owners == 0);
    for (mode = 0; mode < 8; ++mode) {
        invalid = refs[0]; bad_spec = spec;
        if (mode == 0) invalid.hdu_index = -1;
        if (mode == 1) invalid.resolved_path = "relative.fits";
        if (mode == 2) invalid.detector_id = "";
        if (mode == 3) invalid.extver = 1;
        if (mode == 4) { invalid.extname = "SCI"; invalid.extver = 0; }
        bad_spec.inputs = &invalid; bad_spec.input_count = 1;
        if (mode == 5) bad_spec.input_count = (size_t)-1;
        if (mode == 6) bad_spec.work_dir = "relative";
        if (mode == 7) bad_spec.inputs = NULL;
        assert(mef_request_create(&bad_spec, NULL, &request, &error) == MEF_ERR_INPUT);
        assert(request == NULL && mef_error_status(error) == MEF_ERR_INPUT);
        mef_error_destroy(error); error = NULL;
    }
    bad_allocator = allocator; bad_allocator.release = NULL;
    assert(mef_request_create(&spec, &bad_allocator, &request, &error) == MEF_ERR_CONFIG);
    assert(request == NULL && error == NULL);
    assert(mef_request_create(&spec, NULL, NULL, &error) == MEF_ERR_INPUT);
    assert(mef_error_create(MEF_OK, "invalid", NULL, &error) == MEF_ERR_INPUT);
    assert(mef_context_create(NULL, NULL, NULL, &context, &error) == MEF_ERR_INPUT);
    assert(context == context_alias && error == NULL);
    /* Original objects/strings may disappear; the context has its own copies. */
    mef_config_destroy(config); config = NULL;
    strcpy(asset, "mutated"); strcpy(path, "/mutated");
    refs[1].hdu_index = 99; calibrations[0].asset_record_id = "mutated calibration";
    view = mef_request_view(mef_context_request(context));
    assert(strcmp(view->inputs[0].asset_record_id, "asset:primary") == 0);
    assert(strcmp(view->inputs[0].resolved_path, "/input with spaces/primary.fits") == 0);
    assert(view->inputs[0].hdu_index == 0 && view->inputs[1].hdu_index == 5);
    assert(strcmp(view->inputs[1].detector_id, "WIN1.CHIP8.OUT1") == 0);
    assert(view->calibration_count == 1 &&
           strcmp(view->calibrations[0].asset_record_id, "calibration:bias") == 0);
    assert(mef_result_create(view->operation, view->inputs, view->input_count,
                             NULL, &result, &error) == MEF_OK);
    result_alias = result;
    assert(mef_result_create(view->operation, NULL, 0, NULL, &result, &error) == MEF_ERR_INPUT);
    assert(result == result_alias && error == NULL);
    assert(mef_execute(context, &result, &error) == MEF_ERR_INPUT);
    assert(result == result_alias && error == NULL);
    result = NULL;
    assert(mef_execute(context, &result, &error) == MEF_ERR_UNSUPPORTED);
    assert(result == NULL && mef_error_status(error) == MEF_ERR_UNSUPPORTED);
    stream = fopen(argv[2], "w"); assert(stream != NULL);
    assert(mef_config_dump(mef_context_config(context), stream) == MEF_OK);
    assert(fclose(stream) == 0);
    mef_context_destroy(context); context = NULL;
    assert(strcmp(mef_error_message(error), "Numerical service is not connected") == 0);
    products = mef_result_products(result_alias, &count);
    assert(count == 2 && strcmp(products[0].asset_record_id, "asset:primary") == 0);
    assert(mef_result_operation(result_alias) == MEF_OP_SCI_PP);
    mef_error_destroy(error); error = NULL;
    mef_result_destroy(result_alias);
    assert(mef_result_create(MEF_OP_CAL_BIAS, NULL, 0, NULL, &result, &error) == MEF_OK);
    assert(mef_result_products(result, &count) == NULL && count == 0);
    mef_result_destroy(result); result = NULL;
    strcpy(message, "copied error");
    assert(mef_error_create(MEF_ERR_IO, message, NULL, &error) == MEF_OK);
    strcpy(message, "mutated");
    assert(strcmp(mef_error_message(error), "copied error") == 0);
    mef_error_destroy(error);
    assert(mef_execute(NULL, &result, NULL) == MEF_ERR_INPUT);
    assert(mef_request_view(NULL) == NULL && mef_context_request(NULL) == NULL);
    assert(mef_context_config(NULL) == NULL && mef_error_message(NULL) == NULL);
    mef_request_destroy(NULL); mef_context_destroy(NULL);
    mef_result_destroy(NULL); mef_error_destroy(NULL); mef_config_destroy(NULL);
    printf("PASS: %lu allocation positions, transient+persistent OOM; 20 cycles per owner; independent result/error lifetimes\n", (unsigned long)total);
    return 0;
}
