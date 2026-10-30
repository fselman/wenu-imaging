/* File/list and ownership probe: no engine or image pixel/header reads. */
#include "mef_input_request.h"
#include "framelist.h"
#include <assert.h>
#include <unistd.h>

typedef struct { size_t calls, owners, fail_at; int persistent; } allocation_state;
static void *allocate(void *user, size_t bytes)
{
    allocation_state *s;
    void *p;
    s = user; ++s->calls;
    if (s->fail_at && (s->calls == s->fail_at ||
        (s->persistent && s->calls >= s->fail_at))) return NULL;
    p = (malloc)(bytes);
    if (p != NULL) ++s->owners;
    return p;
}
static void release(void *user, void *p)
{
    allocation_state *s;
    s = user; assert(p != NULL && s->owners > 0);
    --s->owners; (free)(p);
}
static char *join(const char *root, const char *suffix)
{
    char *p;
    size_t r, s;
    r = strlen(root); s = strlen(suffix);
    p = (malloc)(r + s + 2); assert(p != NULL);
    memcpy(p, root, r); p[r] = '/'; memcpy(p + r + 1, suffix, s + 1);
    return p;
}
static size_t exercise(const mef_input_request_spec *spec, size_t fail_at, int persistent)
{
    allocation_state s;
    mef_allocator a;
    mef_request *request;
    mef_error *error;
    mef_status status;
    size_t calls;
    s.calls = s.owners = 0; s.fail_at = fail_at; s.persistent = persistent;
    a.user = &s; a.allocate = allocate; a.release = release;
    request = NULL; error = NULL;
    status = mef_request_from_input(spec, &a, &request, &error);
    calls = s.calls;
    if (fail_at) {
        assert(status == MEF_ERR_MEMORY && request == NULL);
        if (persistent) assert(error == NULL);
        else if (error != NULL) assert(mef_error_status(error) == MEF_ERR_MEMORY);
    } else assert(status == MEF_OK && request != NULL && error == NULL);
    mef_request_destroy(request); mef_error_destroy(error);
    assert(s.owners == 0);
    return calls;
}
/* A missing selected BPM remains an error even if reporting it runs out of
 * memory. No partial request may escape either the copy or I/O failure. */
static size_t invalid_exercise(const mef_input_request_spec *spec, size_t fail_at, int persistent)
{
    allocation_state s;
    mef_allocator a;
    mef_request *request;
    mef_error *error;
    mef_status status;
    size_t calls;
    s.calls = s.owners = 0; s.fail_at = fail_at; s.persistent = persistent;
    a.user = &s; a.allocate = allocate; a.release = release;
    request = NULL; error = NULL;
    status = mef_request_from_input(spec, &a, &request, &error);
    calls = s.calls;
    assert(request == NULL);
    assert(status == MEF_ERR_IO || (fail_at != 0 && status == MEF_ERR_MEMORY));
    if (error != NULL) assert(mef_error_status(error) == status);
    mef_error_destroy(error); assert(s.owners == 0);
    return calls;
}
int main(int argc, char **argv)
{
    mef_input_request_spec spec;
    mef_image_ref catalogue[3], calibration;
    mef_bpm_selection bpm[2];
    mef_calibration_role role;
    mef_request *request, *alias;
    mef_error *error, *error_alias;
    mef_allocator invalid_allocator;
    const mef_resolved_request_spec *view;
    framelist *legacy;
    mef_status status, expected;
    char *base, *list, *zpath, *apath, *bpath, *temporary;
    char before[4096], after[4096];
    const char *mode;
    size_t i, calls, failure;
    int cycle;
    assert(argc == 3);
    if (strcmp(argv[1], "legacy") == 0) {
        legacy = framelist_load(argv[2]); assert(legacy != NULL);
        for (i = 0; i < (size_t)legacy->n; ++i) printf("LEGACY:%s\n", legacy->name[i]);
        framelist_del(legacy); return 0;
    }
    mode = argv[1]; assert(getcwd(before, sizeof(before)) != NULL);
    base = join(argv[2], "members"); list = join(argv[2], "lists/input.list");
    zpath = join(base, "z.fits"); apath = join(base, "a.fits");
    bpath = join(argv[2], "cal/bpm.fits"); temporary = NULL;
    catalogue[0].asset_record_id = "asset:z"; catalogue[0].detector_id = "DET-B";
    catalogue[0].resolved_path = zpath; catalogue[0].hdu_index = 2;
    catalogue[0].extname = "DET-B"; catalogue[0].extver = 1;
    catalogue[1] = catalogue[0]; catalogue[1].detector_id = "DET-A";
    catalogue[1].hdu_index = 1; catalogue[1].extname = "DET-A";
    catalogue[2] = catalogue[1]; catalogue[2].asset_record_id = "asset:a";
    catalogue[2].resolved_path = apath; catalogue[2].hdu_index = 0;
    catalogue[2].extname = NULL; catalogue[2].extver = 0;
    bpm[0].detector_id = "DET-B"; bpm[0].state = MEF_BPM_OMITTED;
    bpm[1].detector_id = "DET-A"; bpm[1].state = MEF_BPM_OMITTED;
    role = MEF_CAL_BPM;
    calibration = catalogue[1]; calibration.asset_record_id = "cal:bpm";
    calibration.resolved_path = bpath;
    spec.request.request.operation = MEF_OP_CAL_BIAS;
    spec.request.request.operation_version = 1;
    spec.request.request.inputs = NULL; spec.request.request.input_count = 0;
    spec.request.request.calibrations = NULL; spec.request.request.calibration_count = 0;
    spec.request.request.work_dir = "/work"; spec.request.request.output_dir = "/output";
    spec.request.request.log_path = "/logs/run.log";
    spec.request.calibration_roles = NULL; spec.request.calibration_role_count = 0;
    spec.request.bpm_selections = bpm; spec.request.bpm_selection_count = 2;
    spec.kind = MEF_INPUT_LEGACY_LIST; spec.input_path = list; spec.member_base = base;
    spec.catalogue = catalogue; spec.catalogue_count = 3;
    expected = MEF_OK;
    if (strcmp(mode, "selected") == 0 || strcmp(mode, "missing-bpm") == 0 ||
        strcmp(mode, "ownership-selected") == 0) {
        spec.request.request.calibrations = &calibration; spec.request.request.calibration_count = 1;
        spec.request.calibration_roles = &role; spec.request.calibration_role_count = 1;
        bpm[1].state = MEF_BPM_SELECTED;
        if (strcmp(mode, "missing-bpm") == 0) {
            temporary = join(argv[2], "missing-bpm.fits");
            calibration.resolved_path = temporary; expected = MEF_ERR_IO;
        }
    } else if (strcmp(mode, "direct") == 0) {
        temporary = join(base, "with space.fits");
        catalogue[0] = catalogue[2]; catalogue[0].resolved_path = temporary;
        spec.input_path = temporary; spec.kind = MEF_INPUT_FILE; spec.member_base = NULL;
        spec.catalogue_count = 1; spec.request.bpm_selections = bpm + 1;
        spec.request.bpm_selection_count = 1;
    } else if (strcmp(mode, "missing-member") == 0 || strcmp(mode, "empty") == 0 ||
               strcmp(mode, "long-line") == 0 || strcmp(mode, "nul") == 0 ||
               strcmp(mode, "quoted-space") == 0) {
        temporary = join(argv[2], mode); spec.input_path = temporary;
        expected = strcmp(mode, "missing-member") == 0 || strcmp(mode, "quoted-space") == 0 ? MEF_ERR_IO : MEF_ERR_INPUT;
    } else if (strcmp(mode, "directory") == 0) {
        spec.input_path = base; expected = MEF_ERR_IO;
    } else if (strcmp(mode, "unknown-base") == 0) {
        spec.member_base = NULL; expected = MEF_ERR_INPUT;
    } else if (strcmp(mode, "unknown-image") == 0) {
        spec.catalogue_count = 2; expected = MEF_ERR_INPUT;
    } else if (strcmp(mode, "ambiguous") == 0) {
        catalogue[1] = catalogue[0]; expected = MEF_ERR_INPUT;
    } else if (strcmp(mode, "no-guess") == 0) {
        spec.kind = MEF_INPUT_FILE; expected = MEF_ERR_INPUT;
    } else if (strcmp(mode, "inconsistent-bpm") == 0) {
        bpm[1].state = MEF_BPM_SELECTED; expected = MEF_ERR_INPUT;
    } else assert(strcmp(mode, "omitted") == 0 || strcmp(mode, "ownership") == 0);
    request = NULL; error = NULL;
    status = mef_request_from_input(&spec, NULL, &request, &error);
    assert(status == expected);
    if (status != MEF_OK) {
        assert(request == NULL && mef_error_status(error) == expected);
        printf("REJECTED:%s:%d:%s\n", mode, (int)status, mef_error_message(error));
        mef_error_destroy(error);
        if (strcmp(mode, "missing-bpm") == 0) {
            calls = invalid_exercise(&spec, 0, 0);
            for (failure = 1; failure <= calls; ++failure) {
                (void)invalid_exercise(&spec, failure, 0);
                (void)invalid_exercise(&spec, failure, 1);
            }
            printf("OWNERSHIP-INVALID:%lu:transient+persistent\n", (unsigned long)calls);
        }
    } else {
        assert(error == NULL);
        alias = request;
        assert(mef_request_from_input(&spec, NULL, &request, &error) == MEF_ERR_INPUT);
        assert(request == alias && error == NULL);
        assert(mef_error_create(MEF_ERR_INPUT, "existing", NULL, &error) == MEF_OK);
        error_alias = error;
        assert(mef_request_from_input(&spec, NULL, &request, &error) == MEF_ERR_INPUT);
        assert(request == alias && error == error_alias);
        mef_error_destroy(error); error = NULL;
        view = mef_request_resolved_view(request); assert(view != NULL);
        for (i = 0; i < view->request.input_count; ++i) {
            const mef_image_ref *ref;
            ref = view->request.inputs + i;
            printf("IMAGE:%s|%s|%s|%d|%d\n", ref->asset_record_id, ref->detector_id,
                ref->resolved_path, ref->hdu_index, ref->extver);
        }
        for (i = 0; i < view->bpm_selection_count; ++i)
            printf("BPM:%s:%d\n", view->bpm_selections[i].detector_id, (int)view->bpm_selections[i].state);
        if (strcmp(mode, "ownership") == 0 || strcmp(mode, "ownership-selected") == 0) {
            calls = exercise(&spec, 0, 0);
            for (failure = 1; failure <= calls; ++failure) {
                (void)exercise(&spec, failure, 0);
                (void)exercise(&spec, failure, 1);
            }
            for (cycle = 0; cycle < 20; ++cycle) (void)exercise(&spec, 0, 0);
            printf("OWNERSHIP:%lu:transient+persistent:20cycles\n", (unsigned long)calls);
        }
        /* Request strings/selection data do not borrow catalogue storage. */
        zpath[1] = 'X'; catalogue[0].hdu_index = 99; bpm[0].state = MEF_BPM_SELECTED;
        assert(view->request.inputs[0].hdu_index != 99);
        assert(view->request.inputs[0].resolved_path != catalogue[0].resolved_path);
        mef_request_destroy(request); request = NULL;
    }
    invalid_allocator.user = NULL; invalid_allocator.allocate = NULL; invalid_allocator.release = NULL;
    assert(mef_request_from_input(&spec, &invalid_allocator, &request, NULL) == MEF_ERR_CONFIG);
    assert(getcwd(after, sizeof(after)) != NULL && strcmp(before, after) == 0);
    (free)(temporary); (free)(base); (free)(list); (free)(zpath); (free)(apath); (free)(bpath);
    return 0;
}
