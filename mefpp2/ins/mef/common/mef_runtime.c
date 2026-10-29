#include "mef_runtime.h"
#include <stdlib.h>
#include <string.h>

struct mef_error {
    mef_allocator allocator;
    mef_status status;
    char *message;
};
struct mef_request {
    mef_allocator allocator;
    mef_request_spec spec;
};
struct mef_context {
    mef_allocator allocator;
    mef_config *config;
    mef_request *request;
};
struct mef_result {
    mef_allocator allocator;
    mef_operation operation;
    mef_image_ref *products;
    size_t count;
};

static void *standard_allocate(void *user, size_t size)
{
    (void)user;
    return malloc(size);
}
static void standard_release(void *user, void *pointer)
{
    (void)user;
    free(pointer);
}
static int select_allocator(const mef_allocator *source, mef_allocator *out)
{
    if (source != NULL) {
        if (source->allocate == NULL || source->release == NULL) return 0;
        *out = *source;
    } else {
        out->user = NULL;
        out->allocate = standard_allocate;
        out->release = standard_release;
    }
    return 1;
}
static void release(const mef_allocator *a, const void *p)
{
    if (p != NULL) a->release(a->user, (void *)p);
}
static char *copy_string(const mef_allocator *a, const char *source)
{
    size_t size;
    char *copy;
    if (source == NULL) return NULL;
    size = strlen(source);
    if (size == (size_t)-1) return NULL;
    copy = a->allocate(a->user, size + 1);
    if (copy != NULL) memcpy(copy, source, size + 1);
    return copy;
}
static int valid_operation(mef_operation operation)
{
    return operation >= MEF_OP_CAL_BIAS && operation <= MEF_OP_SCI_PP;
}
static int text_present(const char *s) { return s != NULL && *s != '\0'; }
static int absolute_path(const char *s) { return s != NULL && *s == '/'; }

mef_status mef_error_create(mef_status status, const char *message,
    const mef_allocator *allocator, mef_error **out)
{
    mef_allocator a;
    mef_error *error;
    if (out == NULL || *out != NULL || status <= MEF_OK ||
        status > MEF_ERR_CANCELLED || !text_present(message)) return MEF_ERR_INPUT;
    if (!select_allocator(allocator, &a)) return MEF_ERR_CONFIG;
    error = a.allocate(a.user, sizeof(*error));
    if (error == NULL) return MEF_ERR_MEMORY;
    error->allocator = a;
    error->status = status;
    error->message = copy_string(&a, message);
    if (error->message == NULL) {
        release(&a, error);
        return MEF_ERR_MEMORY;
    }
    *out = error;
    return MEF_OK;
}
void mef_error_destroy(mef_error *error)
{
    mef_allocator a;
    if (error == NULL) return;
    a = error->allocator;
    release(&a, error->message);
    release(&a, error);
}
mef_status mef_error_status(const mef_error *error)
{
    return error == NULL ? MEF_OK : error->status;
}
const char *mef_error_message(const mef_error *error)
{
    return error == NULL ? NULL : error->message;
}
static mef_status fail(const mef_allocator *a, mef_status status,
    const char *message, mef_error **error)
{
    if (error != NULL && *error == NULL)
        (void)mef_error_create(status, message, a, error);
    return status;
}
static int valid_refs(const mef_image_ref *refs, size_t count)
{
    size_t i;
    if (count > (size_t)-1 / sizeof(*refs) || (count && refs == NULL)) return 0;
    for (i = 0; i < count; ++i) {
        if (!text_present(refs[i].asset_record_id) || !text_present(refs[i].detector_id) ||
            !absolute_path(refs[i].resolved_path) || refs[i].hdu_index < 0 ||
            (refs[i].extname == NULL ? refs[i].extver != 0 :
             !text_present(refs[i].extname) || refs[i].extver <= 0)) return 0;
    }
    return 1;
}
static void free_refs(const mef_allocator *a, const mef_image_ref *refs, size_t count)
{
    size_t i;
    if (refs == NULL) return;
    for (i = 0; i < count; ++i) {
        release(a, refs[i].asset_record_id);
        release(a, refs[i].detector_id);
        release(a, refs[i].resolved_path);
        release(a, refs[i].extname);
    }
    release(a, refs);
}
/* Source descriptors are validated before this helper. Empty arrays own NULL. */
static mef_image_ref *copy_refs(const mef_allocator *a,
    const mef_image_ref *source, size_t count)
{
    mef_image_ref *refs;
    size_t i;
    if (count == 0) return NULL;
    refs = a->allocate(a->user, count * sizeof(*refs));
    if (refs == NULL) return NULL;
    for (i = 0; i < count; ++i) {
        refs[i].asset_record_id = NULL;
        refs[i].detector_id = NULL;
        refs[i].resolved_path = NULL;
        refs[i].extname = NULL;
        refs[i].hdu_index = source[i].hdu_index;
        refs[i].extver = source[i].extver;
    }
    for (i = 0; i < count; ++i) {
        refs[i].asset_record_id = copy_string(a, source[i].asset_record_id);
        if (refs[i].asset_record_id == NULL) goto failure;
        refs[i].detector_id = copy_string(a, source[i].detector_id);
        if (refs[i].detector_id == NULL) goto failure;
        refs[i].resolved_path = copy_string(a, source[i].resolved_path);
        if (refs[i].resolved_path == NULL) goto failure;
        if (source[i].extname != NULL) refs[i].extname = copy_string(a, source[i].extname);
        if (refs[i].asset_record_id == NULL || refs[i].detector_id == NULL ||
            refs[i].resolved_path == NULL ||
            (source[i].extname != NULL && refs[i].extname == NULL)) {
            goto failure;
        }
    }
    return refs;
failure:
    free_refs(a, refs, count);
    return NULL;
}
void mef_request_destroy(mef_request *request)
{
    mef_allocator a;
    if (request == NULL) return;
    a = request->allocator;
    free_refs(&a, request->spec.inputs, request->spec.input_count);
    free_refs(&a, request->spec.calibrations, request->spec.calibration_count);
    release(&a, request->spec.work_dir);
    release(&a, request->spec.output_dir);
    release(&a, request->spec.log_path);
    release(&a, request);
}
mef_status mef_request_create(const mef_request_spec *spec,
    const mef_allocator *allocator, mef_request **out, mef_error **error)
{
    mef_allocator a;
    mef_request *request;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (!select_allocator(allocator, &a)) return MEF_ERR_CONFIG;
    if (spec == NULL || !valid_operation(spec->operation) || spec->input_count == 0 ||
        !valid_refs(spec->inputs, spec->input_count) ||
        !valid_refs(spec->calibrations, spec->calibration_count) ||
        !absolute_path(spec->work_dir) || !absolute_path(spec->output_dir) ||
        !absolute_path(spec->log_path))
        return fail(&a, MEF_ERR_INPUT, "Invalid resolved request descriptor", error);
    if (spec->operation_version != 1)
        return fail(&a, MEF_ERR_UNSUPPORTED, "Unsupported operation version", error);
    request = a.allocate(a.user, sizeof(*request));
    if (request == NULL) return fail(&a, MEF_ERR_MEMORY, "Cannot allocate request", error);
    request->allocator = a;
    request->spec = *spec;
    request->spec.inputs = NULL;
    request->spec.calibrations = NULL;
    request->spec.work_dir = NULL;
    request->spec.output_dir = NULL;
    request->spec.log_path = NULL;
    request->spec.inputs = copy_refs(&a, spec->inputs, spec->input_count);
    if (request->spec.inputs == NULL) goto memory_failure;
    request->spec.calibrations = copy_refs(&a, spec->calibrations, spec->calibration_count);
    if (spec->calibration_count && request->spec.calibrations == NULL) goto memory_failure;
    request->spec.work_dir = copy_string(&a, spec->work_dir);
    if (request->spec.work_dir == NULL) goto memory_failure;
    request->spec.output_dir = copy_string(&a, spec->output_dir);
    if (request->spec.output_dir == NULL) goto memory_failure;
    request->spec.log_path = copy_string(&a, spec->log_path);
    if (request->spec.log_path == NULL) goto memory_failure;
    *out = request;
    return MEF_OK;
memory_failure:
    mef_request_destroy(request);
    return fail(&a, MEF_ERR_MEMORY, "Cannot copy request", error);
}
const mef_request_spec *mef_request_view(const mef_request *request)
{
    return request == NULL ? NULL : &request->spec;
}
void mef_context_destroy(mef_context *context)
{
    mef_allocator a;
    if (context == NULL) return;
    a = context->allocator;
    mef_config_destroy(context->config);
    mef_request_destroy(context->request);
    release(&a, context);
}
mef_status mef_context_create(const mef_config *config, const mef_request *request,
    const mef_allocator *allocator, mef_context **out, mef_error **error)
{
    mef_allocator a;
    mef_context *context;
    mef_status status;
    const char *detail;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (!select_allocator(allocator, &a)) return MEF_ERR_CONFIG;
    if (config == NULL || request == NULL)
        return fail(&a, MEF_ERR_INPUT, "Missing configuration or request", error);
    context = a.allocate(a.user, sizeof(*context));
    if (context == NULL) return fail(&a, MEF_ERR_MEMORY, "Cannot allocate context", error);
    context->allocator = a;
    context->config = NULL;
    context->request = NULL;
    status = mef_config_clone(config, &a, &context->config, &detail);
    if (status == MEF_OK)
        status = mef_request_create(&request->spec, &a, &context->request, error);
    if (status != MEF_OK) {
        mef_context_destroy(context);
        return fail(&a, status, "Cannot copy context inputs", error);
    }
    *out = context;
    return MEF_OK;
}
const mef_config *mef_context_config(const mef_context *context)
{
    return context == NULL ? NULL : context->config;
}
const mef_request *mef_context_request(const mef_context *context)
{
    return context == NULL ? NULL : context->request;
}
void mef_result_destroy(mef_result *result)
{
    mef_allocator a;
    if (result == NULL) return;
    a = result->allocator;
    free_refs(&a, result->products, result->count);
    release(&a, result);
}
mef_status mef_result_create(mef_operation operation, const mef_image_ref *products,
    size_t count, const mef_allocator *allocator, mef_result **out, mef_error **error)
{
    mef_allocator a;
    mef_result *result;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (!select_allocator(allocator, &a)) return MEF_ERR_CONFIG;
    if (!valid_operation(operation) || !valid_refs(products, count))
        return fail(&a, MEF_ERR_INPUT, "Invalid result descriptor", error);
    result = a.allocate(a.user, sizeof(*result));
    if (result == NULL) return fail(&a, MEF_ERR_MEMORY, "Cannot allocate result", error);
    result->allocator = a;
    result->operation = operation;
    result->count = count;
    result->products = copy_refs(&a, products, count);
    if (count && result->products == NULL) {
        mef_result_destroy(result);
        return fail(&a, MEF_ERR_MEMORY, "Cannot copy result", error);
    }
    *out = result;
    return MEF_OK;
}
mef_operation mef_result_operation(const mef_result *result)
{
    return result == NULL ? (mef_operation)0 : result->operation;
}
const mef_image_ref *mef_result_products(const mef_result *result, size_t *count)
{
    if (count != NULL) *count = result == NULL ? 0 : result->count;
    return result == NULL ? NULL : result->products;
}
mef_status mef_execute(mef_context *context, mef_result **out, mef_error **error)
{
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (context == NULL) return fail(NULL, MEF_ERR_INPUT, "Missing context", error);
    return fail(&context->allocator, MEF_ERR_UNSUPPORTED,
        "Numerical service is not connected", error);
}
