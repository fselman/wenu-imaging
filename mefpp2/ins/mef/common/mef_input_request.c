#include "mef_input_request.h"
#include "charmatrix.h"
#include "static_sz.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <string.h>

static void *standard_allocate(void *user, size_t size)
{
    (void)user;
    return (malloc)(size);
}
static void standard_release(void *user, void *p)
{
    (void)user;
    (free)(p);
}
static int select_allocator(const mef_allocator *source, mef_allocator *a)
{
    if (source != NULL) {
        if (source->allocate == NULL || source->release == NULL) return 0;
        *a = *source;
    } else {
        a->user = NULL; a->allocate = standard_allocate; a->release = standard_release;
    }
    return 1;
}
static int present(const char *s) { return s != NULL && *s != '\0'; }
static int absolute(const char *s) { return s != NULL && *s == '/'; }
static void release(const mef_allocator *a, void *p)
{
    if (p != NULL) a->release(a->user, p);
}
static mef_status failure(const mef_allocator *a, mef_status status,
    const char *message, const char *path, mef_error **error)
{
    size_t m, n;
    char *detail;
    if (error == NULL || *error != NULL) return status;
    m = strlen(message); n = path == NULL ? 0 : strlen(path);
    if (n > (size_t)-1 - m - 3) return status;
    detail = a->allocate(a->user, m + n + 3);
    if (detail == NULL) return status;
    memcpy(detail, message, m);
    detail[m] = ':'; detail[m + 1] = ' ';
    if (n != 0) memcpy(detail + m + 2, path, n);
    detail[m + n + 2] = '\0';
    (void)mef_error_create(status, detail, a, error);
    release(a, detail);
    return status;
}
static int readable_regular(const char *path)
{
    struct stat st;
    FILE *stream;
    if (stat(path, &st) != 0 || !S_ISREG(st.st_mode)) return 0;
    stream = fopen(path, "rb");
    if (stream == NULL) return 0;
    return fclose(stream) == 0;
}
/* Do not let the legacy parser silently split a long line or consume NULs.
 * This is a bounded adapter format gate, not a change to the old reader.
 */
static int supported_list(const char *path)
{
    FILE *stream;
    size_t length;
    int ch, supported;
    stream = fopen(path, "rb");
    if (stream == NULL) return 0;
    length = 0; supported = 1;
    while ((ch = fgetc(stream)) != EOF) {
        if (ch == '\0') { supported = 0; break; }
        if (ch == '\n') length = 0;
        else if (++length >= ASCIILINESZ - 1) { supported = 0; break; }
    }
    if (ferror(stream)) supported = 0;
    if (fclose(stream) != 0) supported = 0;
    return supported;
}
static char *member_path(const mef_allocator *a, const char *base, const char *member)
{
    size_t b, m;
    char *path;
    b = absolute(member) ? 0 : strlen(base);
    m = strlen(member);
    if (m > (size_t)-1 - b - 2) return NULL;
    path = a->allocate(a->user, b + m + 2);
    if (path == NULL) return NULL;
    if (b != 0) {
        memcpy(path, base, b);
        if (path[b - 1] != '/') path[b++] = '/';
    }
    memcpy(path + b, member, m + 1);
    return path;
}
static int valid_catalogue(const mef_image_ref *refs, size_t count)
{
    size_t i, j;
    if (count == 0 || refs == NULL || count > (size_t)-1 / sizeof(*refs)) return 0;
    for (i = 0; i < count; ++i) {
        if (!absolute(refs[i].resolved_path) || !present(refs[i].asset_record_id) ||
            !present(refs[i].detector_id) || refs[i].hdu_index < 0 ||
            (refs[i].extname == NULL ? refs[i].extver != 0 :
             !present(refs[i].extname) || refs[i].extver <= 0)) return 0;
        for (j = 0; j < i; ++j) {
            if (strcmp(refs[i].resolved_path, refs[j].resolved_path) == 0 &&
                (strcmp(refs[i].detector_id, refs[j].detector_id) == 0 ||
                 refs[i].hdu_index == refs[j].hdu_index)) return 0;
        }
    }
    return 1;
}
mef_status mef_request_from_input(const mef_input_request_spec *spec,
    const mef_allocator *allocator, mef_request **out, mef_error **error)
{
    mef_allocator a;
    charmatrix *matrix;
    mef_image_ref *inputs;
    mef_resolved_request_spec resolved;
    mef_request *pending;
    char *path;
    const char *token;
    size_t i, j, rows, count, matches, position;
    mef_status status;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (!select_allocator(allocator, &a)) return MEF_ERR_CONFIG;
    if (spec == NULL || !absolute(spec->input_path) ||
        (spec->kind != MEF_INPUT_FILE && spec->kind != MEF_INPUT_LEGACY_LIST) ||
        (spec->kind == MEF_INPUT_LEGACY_LIST && !absolute(spec->member_base)) ||
        spec->request.request.inputs != NULL || spec->request.request.input_count != 0 ||
        !valid_catalogue(spec->catalogue, spec->catalogue_count))
        return failure(&a, MEF_ERR_INPUT, "Invalid input/catalogue descriptor", NULL, error);
    if (!readable_regular(spec->input_path))
        return failure(&a, MEF_ERR_IO, "Cannot read input file/list", spec->input_path, error);
    matrix = NULL; inputs = NULL; path = NULL; pending = NULL;
    status = MEF_OK;
    if (spec->kind == MEF_INPUT_LEGACY_LIST) {
        if (!supported_list(spec->input_path))
            return failure(&a, MEF_ERR_INPUT, "Unsupported or unreadable legacy list", spec->input_path, error);
        matrix = charmatrix_read((char *)spec->input_path);
        if (matrix == NULL) return failure(&a, MEF_ERR_INPUT, "Cannot parse nonempty legacy list", spec->input_path, error);
    }
    rows = matrix == NULL ? 1 : (size_t)matrix->ly;
    count = 0;
    /* First count the exact expansion, validating every selected path. */
    for (i = 0; i < rows; ++i) {
        token = matrix == NULL ? spec->input_path : charmatrix_elem(matrix, 0, (int)i);
        path = member_path(&a, spec->member_base, token);
        if (path == NULL) { status = MEF_ERR_MEMORY; goto cleanup; }
        if (!readable_regular(path)) {
            status = failure(&a, MEF_ERR_IO, "Cannot read selected input", path, error);
            goto cleanup;
        }
        matches = 0;
        for (j = 0; j < spec->catalogue_count; ++j)
            if (strcmp(path, spec->catalogue[j].resolved_path) == 0) ++matches;
        if (matches == 0) {
            status = failure(&a, MEF_ERR_INPUT, "Input absent from selected image catalogue", path, error);
            goto cleanup;
        }
        if (matches > (size_t)-1 / sizeof(*inputs) - count) {
            status = MEF_ERR_MEMORY; goto cleanup;
        }
        count += matches;
        release(&a, path); path = NULL;
    }
    inputs = a.allocate(a.user, count * sizeof(*inputs));
    if (inputs == NULL) { status = MEF_ERR_MEMORY; goto cleanup; }
    position = 0;
    for (i = 0; i < rows; ++i) {
        token = matrix == NULL ? spec->input_path : charmatrix_elem(matrix, 0, (int)i);
        path = member_path(&a, spec->member_base, token);
        if (path == NULL) { status = MEF_ERR_MEMORY; goto cleanup; }
        for (j = 0; j < spec->catalogue_count; ++j)
            if (strcmp(path, spec->catalogue[j].resolved_path) == 0)
                inputs[position++] = spec->catalogue[j];
        release(&a, path); path = NULL;
    }
    resolved = spec->request;
    resolved.request.inputs = inputs; resolved.request.input_count = count;
    /* The existing builder validates roles/BPM choices and owns all copies. */
    status = mef_request_create_resolved(&resolved, &a, &pending, error);
    if (status != MEF_OK) goto cleanup;
    for (j = 0; j < resolved.request.calibration_count; ++j) {
        if (!readable_regular(resolved.request.calibrations[j].resolved_path)) {
            status = failure(&a, MEF_ERR_IO, "Cannot read selected calibration",
                resolved.request.calibrations[j].resolved_path, error);
            goto cleanup;
        }
    }
    *out = pending; pending = NULL;
cleanup:
    mef_request_destroy(pending);
    release(&a, path); release(&a, inputs); charmatrix_del(matrix);
    if (status == MEF_ERR_MEMORY)
        return failure(&a, status, "Cannot allocate input request", spec->input_path, error);
    return status;
}
