#include "mef_cli_request.h"
#include "mefp_lib.h"
#include <stdlib.h>
#include <string.h>

struct mef_cli_request {
    mef_allocator allocator;
    mef_config *config;
    char **arguments;
    mef_cli_view view;
};
static void *standard_allocate(void *user, size_t size)
{
    (void)user;
    return (malloc)(size); /* Bypass Eclipse's function-like allocation macros. */
}
static void standard_release(void *user, void *pointer)
{
    (void)user;
    (free)(pointer);
}
static void release(const mef_allocator *a, const void *p)
{
    if (p != NULL) a->release(a->user, (void *)p);
}
static char *copy_string(const mef_allocator *a, const char *source)
{
    size_t size;
    char *copy;
    size = strlen(source);
    if (size == (size_t)-1) return NULL;
    copy = a->allocate(a->user, size + 1);
    if (copy != NULL) memcpy(copy, source, size + 1);
    return copy;
}
static mef_status failure(const mef_allocator *a, mef_status status,
    const char *message, mef_error **error)
{
    if (error != NULL) (void)mef_error_create(status, message, a, error);
    return status;
}
void mef_cli_request_destroy(mef_cli_request *request)
{
    mef_allocator a;
    int i;
    if (request == NULL) return;
    a = request->allocator;
    mef_config_destroy(request->config);
    if (request->arguments != NULL) {
        for (i = 0; i < request->view.argc; ++i) release(&a, request->arguments[i]);
        release(&a, request->arguments);
    }
    release(&a, request->view.base_dir);
#define MEF_CLI_STRING(member, legacy) release(&a, request->view.member);
#define MEF_CLI_INT(member, legacy)
#include "mef_cli_fields.def"
#undef MEF_CLI_STRING
#undef MEF_CLI_INT
    release(&a, request);
}
mef_status mef_cli_request_from_legacy(const struct _mef_bb_ *source,
    const char *base_dir, int argc, const char *const *argv,
    const mef_allocator *allocator, mef_cli_request **out, mef_error **error)
{
    mef_allocator a;
    mef_cli_request *request;
    mef_status status;
    const char *detail;
    int i;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    a.user = NULL; a.allocate = standard_allocate; a.release = standard_release;
    if (allocator != NULL) {
        if (allocator->allocate == NULL || allocator->release == NULL) return MEF_ERR_CONFIG;
        a = *allocator;
    }
    if (source == NULL || source->name_paf == NULL || base_dir == NULL ||
        *base_dir != '/' || argc < 1 || argv == NULL ||
        (size_t)argc > (size_t)-1 / sizeof(char *))
        return failure(&a, MEF_ERR_INPUT, "Invalid loaded CLI capture arguments", error);
    for (i = 0; i < argc; ++i)
        if (argv[i] == NULL) return failure(&a, MEF_ERR_INPUT, "Missing CLI argument", error);
    request = a.allocate(a.user, sizeof(*request));
    if (request == NULL) return failure(&a, MEF_ERR_MEMORY, "Cannot allocate CLI capture", error);
    request->allocator = a;
    request->config = NULL;
    request->arguments = NULL;
    request->view.base_dir = NULL;
    request->view.argc = argc;
    request->view.argv = NULL;
#define MEF_CLI_STRING(member, legacy) request->view.member = NULL;
#define MEF_CLI_INT(member, legacy) request->view.member = source->legacy;
#include "mef_cli_fields.def"
#undef MEF_CLI_STRING
#undef MEF_CLI_INT
    status = MEF_ERR_MEMORY;
    detail = "Cannot copy CLI arguments";
    request->arguments = a.allocate(a.user, (size_t)argc * sizeof(*request->arguments));
    if (request->arguments == NULL) goto cleanup;
    for (i = 0; i < argc; ++i) request->arguments[i] = NULL;
    for (i = 0; i < argc; ++i) {
        request->arguments[i] = copy_string(&a, argv[i]);
        if (request->arguments[i] == NULL) goto cleanup;
    }
    request->view.argv = (const char *const *)request->arguments;
    request->view.base_dir = copy_string(&a, base_dir);
    if (request->view.base_dir == NULL) goto cleanup;
#define MEF_CLI_STRING(member, legacy) \
    if (source->legacy != NULL) { \
        request->view.member = copy_string(&a, source->legacy); \
        if (request->view.member == NULL) { detail = #member; goto cleanup; } \
    }
#define MEF_CLI_INT(member, legacy)
#include "mef_cli_fields.def"
#undef MEF_CLI_STRING
#undef MEF_CLI_INT
    status = mef_config_from_legacy(source, &a, &request->config, &detail);
    if (status != MEF_OK) goto cleanup;
    *out = request;
    return MEF_OK;
cleanup:
    mef_cli_request_destroy(request);
    return failure(&a, status, detail == NULL ? "Cannot copy effective CLI settings" : detail, error);
}
const mef_cli_view *mef_cli_request_view(const mef_cli_request *request)
{
    return request == NULL ? NULL : &request->view;
}
const mef_config *mef_cli_request_config(const mef_cli_request *request)
{
    return request == NULL ? NULL : request->config;
}
static void json_string(FILE *stream, const char *value)
{
    const unsigned char *p;
    if (value == NULL) { fputs("null", stream); return; }
    fputc('"', stream);
    for (p = (const unsigned char *)value; *p; ++p) {
        if (*p == '"' || *p == '\\') { fputc('\\', stream); fputc(*p, stream); }
        else if (*p < 32) fprintf(stream, "\\u%04x", (unsigned int)*p);
        else fputc(*p, stream);
    }
    fputc('"', stream);
}
mef_status mef_cli_request_dump(const mef_cli_request *request, FILE *stream)
{
    int i;
    if (request == NULL || stream == NULL) return MEF_ERR_INPUT;
    fputs("{\"base_dir\":", stream); json_string(stream, request->view.base_dir);
    fprintf(stream, ",\"argc\":%d,\"argv\":[", request->view.argc);
    for (i = 0; i < request->view.argc; ++i) {
        if (i) fputc(',', stream);
        json_string(stream, request->view.argv[i]);
    }
    fputs("]", stream);
#define MEF_CLI_STRING(member, legacy) \
    fputs(",\"" #member "\":", stream); json_string(stream, request->view.member);
#define MEF_CLI_INT(member, legacy) fprintf(stream, ",\"" #member "\":%d", request->view.member);
#include "mef_cli_fields.def"
#undef MEF_CLI_STRING
#undef MEF_CLI_INT
    fputs("}\n", stream);
    return ferror(stream) ? MEF_ERR_IO : MEF_OK;
}
