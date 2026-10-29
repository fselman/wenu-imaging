/* Test-only access to the unchanged loader. Never call the renamed main/engine. */
#define main mef_cli_unexecuted_main
#include "../ins/mef/recipes/mefpp.c"
#undef main
#include "mef_cli_request.h"
#include <assert.h>

typedef struct { size_t calls, fail_at, owners; int persistent; } allocation_state;
static void *test_allocate(void *user, size_t size)
{
    allocation_state *s;
    void *p;
    s = user; ++s->calls;
    if (s->fail_at && (s->calls == s->fail_at ||
                      (s->persistent && s->calls >= s->fail_at))) return NULL;
    p = (malloc)(size);
    if (p != NULL) ++s->owners;
    return p;
}
static void test_release(void *user, void *pointer)
{
    allocation_state *s;
    s = user;
    assert(pointer != NULL && s->owners > 0);
    --s->owners; (free)(pointer);
}
static int same_text(const char *a, const char *b)
{
    return a == NULL || b == NULL ? a == b : strcmp(a, b) == 0;
}
/* Independent assertions, deliberately not generated from the adapter catalog. */
static void compare_bindings(const mef_cli_view *v, const mef_bb *bb)
{
    assert(same_text(v->paf_path, bb->name_paf));
    assert(same_text(v->bias_path, bb->name_bias));
    assert(same_text(v->bpm_path, bb->name_bpm));
    assert(same_text(v->dome_path, bb->name_dome));
    assert(same_text(v->sky_path, bb->name_sky));
    assert(same_text(v->mff_path, bb->name_mf));
    assert(same_text(v->mff_output, bb->name_mf_o));
    assert(same_text(v->science_path, bb->science_name_i));
    assert(same_text(v->split_path, bb->name_split));
    assert(v->noverify == bb->noverify && v->xtnum == bb->xtnum);
    assert(v->bias_subtract == bb->bias_subtract && v->bias_save == bb->bias_save);
    assert(v->dome_save == bb->dome_save && v->sky_save == bb->sky_save);
    assert(v->sat_check == bb->sat_check && v->median_surface == bb->median_surf);
}
static void capture_controls(const mef_bb *bb, const char *base, int argc,
    const char *const *argv)
{
    allocation_state state;
    mef_allocator allocator, invalid;
    mef_cli_request *request, *alias;
    mef_error *error, *error_alias;
    mef_status status;
    size_t calls, failure;
    int persistent, cycle;
    allocator.user = &state; allocator.allocate = test_allocate; allocator.release = test_release;
    state.calls = state.fail_at = state.owners = 0; state.persistent = 0;
    request = NULL; error = NULL;
    assert(mef_cli_request_from_legacy(bb, base, argc, argv, &allocator, &request, &error) == MEF_OK);
    calls = state.calls;
    compare_bindings(mef_cli_request_view(request), bb);
    alias = request;
    assert(mef_cli_request_from_legacy(bb, base, argc, argv, &allocator, &request, &error) == MEF_ERR_INPUT);
    assert(request == alias && error == NULL && calls == state.calls);
    mef_cli_request_destroy(request); request = NULL;
    assert(state.owners == 0);
    for (persistent = 0; persistent <= 1; ++persistent) {
        for (failure = 1; failure <= calls; ++failure) {
            state.calls = 0; state.fail_at = failure; state.persistent = persistent;
            status = mef_cli_request_from_legacy(bb, base, argc, argv, &allocator, &request, &error);
            assert(status == MEF_ERR_MEMORY && request == NULL);
            if (persistent) assert(error == NULL);
            else assert(mef_error_status(error) == MEF_ERR_MEMORY);
            mef_error_destroy(error); error = NULL;
            assert(state.owners == 0);
        }
    }
    state.fail_at = 0; state.persistent = 0;
    for (cycle = 0; cycle < 20; ++cycle) {
        assert(mef_cli_request_from_legacy(bb, base, argc, argv, &allocator, &request, &error) == MEF_OK);
        mef_cli_request_destroy(request); request = NULL;
        assert(state.owners == 0);
    }
    assert(mef_error_create(MEF_ERR_INPUT, "occupied", NULL, &error) == MEF_OK);
    error_alias = error;
    assert(mef_cli_request_from_legacy(bb, base, argc, argv, NULL, &request, &error) == MEF_ERR_INPUT);
    assert(request == NULL && error == error_alias);
    mef_error_destroy(error); error = NULL;
    assert(mef_cli_request_from_legacy(bb, "relative", argc, argv, NULL, &request, &error) == MEF_ERR_INPUT);
    assert(request == NULL && mef_error_status(error) == MEF_ERR_INPUT);
    mef_error_destroy(error); error = NULL;
    state.calls = 0; state.fail_at = 1; state.persistent = 1;
    assert(mef_cli_request_from_legacy(bb, "relative", argc, argv, &allocator, &request, &error) == MEF_ERR_INPUT);
    assert(request == NULL && error == NULL && state.owners == 0);
    assert(mef_cli_request_from_legacy(NULL, base, argc, argv, NULL, &request, NULL) == MEF_ERR_INPUT);
    assert(mef_cli_request_from_legacy(bb, base, -1, argv, NULL, &request, NULL) == MEF_ERR_INPUT);
    assert(mef_cli_request_from_legacy(bb, base, argc, NULL, NULL, &request, NULL) == MEF_ERR_INPUT);
    assert(mef_cli_request_from_legacy(bb, base, argc, argv, NULL, NULL, NULL) == MEF_ERR_INPUT);
    invalid = allocator; invalid.release = NULL;
    assert(mef_cli_request_from_legacy(bb, base, argc, argv, &invalid, &request, NULL) == MEF_ERR_CONFIG);
    assert(mef_cli_request_dump(NULL, NULL) == MEF_ERR_INPUT);
    assert(mef_cli_request_view(NULL) == NULL && mef_cli_request_config(NULL) == NULL);
    mef_cli_request_destroy(NULL);
    printf("PASS: %lu CLI capture allocation positions, transient+persistent OOM; 20 ownership cycles\n", (unsigned long)calls);
}

int main(int argc, char **argv)
{
    mef_bb *bb;
    mef_cli_request *request;
    mef_config *reference;
    mef_error *error;
    const mef_cli_view *view;
    const char *detail;
    char **original;
    char reference_name[8192];
    int i, load_status, count;
    FILE *stream;
    if (argc < 5) return 2;
    count = argc - 4;
    original = (malloc)((size_t)count * sizeof(*original));
    assert(original != NULL);
    for (i = 0; i < count; ++i) original[i] = argv[i + 4];
    /* Only the existing CLI loader runs. No eclipse_init/main/mef_engine call. */
    bb = mef_bb_load(count, argv + 4, &load_status);
    if (bb == NULL) { (free)(original); return load_status; }
    request = NULL; error = NULL; reference = NULL;
    capture_controls(bb, argv[3], count, (const char *const *)original);
    assert(mef_cli_request_from_legacy(bb, argv[3], count, (const char *const *)original,
                                      NULL, &request, &error) == MEF_OK);
    assert(error == NULL);
    view = mef_cli_request_view(request);
    compare_bindings(view, bb);
    assert(view->argc == count && strcmp(view->base_dir, argv[3]) == 0);
    for (i = 0; i < count; ++i) assert(strcmp(view->argv[i], original[i]) == 0);
    assert(mef_config_from_legacy(bb, NULL, &reference, &detail) == MEF_OK);
    assert(strlen(argv[2]) + 11 < sizeof(reference_name));
    sprintf(reference_name, "%s.reference", argv[2]);
    stream = fopen(reference_name, "w"); assert(stream != NULL);
    assert(mef_config_dump(reference, stream) == MEF_OK && fclose(stream) == 0);
    mef_config_destroy(reference);
    mef_bb_del(bb);
    for (i = 0; i < count; ++i) memset(original[i], '#', strlen(original[i]));
    (free)(original);
    stream = fopen(argv[1], "w"); assert(stream != NULL);
    assert(mef_cli_request_dump(request, stream) == MEF_OK && fclose(stream) == 0);
    stream = fopen(argv[2], "w"); assert(stream != NULL);
    assert(mef_config_dump(mef_cli_request_config(request), stream) == MEF_OK && fclose(stream) == 0);
    stream = fopen(argv[1], "r"); assert(stream != NULL);
    assert(mef_cli_request_dump(request, stream) == MEF_ERR_IO);
    assert(fclose(stream) == 0);
    mef_cli_request_destroy(request);
    puts("PASS: actual legacy CLI captured; source/argv destroyed; no reduction executed");
    return 0;
}
