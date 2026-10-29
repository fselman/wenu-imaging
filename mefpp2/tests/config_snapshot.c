/* Synthetic mapped-state tests; no PAF/FITS reads and no native recipe calls. */
#include "mef_config.h"
#include "mefp_lib.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

typedef struct { size_t calls, fail, outstanding; } allocation_state;

static void *test_allocate(void *user, size_t size)
{
    allocation_state *state;
    void *pointer;
    state = user;
    ++state->calls;
    if (state->fail == state->calls) return NULL;
    pointer = (malloc)(size);
    if (pointer != NULL) ++state->outstanding;
    return pointer;
}

static void test_release(void *user, void *pointer)
{
    allocation_state *state;
    state = user;
    assert(pointer != NULL && state->outstanding > 0);
    --state->outstanding;
    (free)(pointer);
}

static void source_release(mef_bb *source)
{
#define MEF_STRING(member, key) (free)(source->member); source->member = NULL;
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    (free)(source->ccd); source->ccd = NULL;
}

/* Generated privately from the reviewed OCAM/WFI value map by the runner. */
#include "config_snapshot_fixture.h"

int main(int argc, char **argv)
{
    mef_bb source;
    mef_config *config, *occupied;
    mef_allocator allocator, bad_allocator;
    allocation_state state;
    const char *diagnostic;
    FILE *stream;
    size_t allocation_count, failure;
    int cycle, saved_count;
    char *saved_string;
    mef_ccd *saved_ccd;
    assert(argc == 3);
    fixture_init(&source, argv[1]);
    allocator.user = &state;
    allocator.allocate = test_allocate;
    allocator.release = test_release;
    state.calls = state.fail = state.outstanding = 0;
    config = NULL;
    assert(mef_config_from_legacy(&source, &allocator, &config, &diagnostic) == MEF_OK);
    assert(diagnostic == NULL && config != NULL);
    allocation_count = state.calls;
    assert(allocation_count == 111);
    occupied = config;
    assert(mef_config_from_legacy(&source, &allocator, &config, NULL) == MEF_ERR_CONFIG);
    assert(config == occupied && state.calls == allocation_count);
    assert(mef_config_dump(NULL, NULL) == MEF_ERR_CONFIG);
    mef_config_destroy(config); config = NULL;
    assert(state.outstanding == 0);
    for (failure = 1; failure <= allocation_count; ++failure) {
        state.calls = 0; state.fail = failure;
        diagnostic = NULL;
        assert(mef_config_from_legacy(&source, &allocator, &config, &diagnostic) == MEF_ERR_MEMORY);
        assert(config == NULL && diagnostic != NULL);
        assert(state.calls == failure && state.outstanding == 0);
    }
    state.calls = state.fail = 0;
    saved_count = source.nchips; source.nchips = 0;
    assert(mef_config_from_legacy(&source, &allocator, &config, NULL) == MEF_ERR_CONFIG);
    source.nchips = saved_count;
    saved_ccd = source.ccd; source.ccd = NULL;
    assert(mef_config_from_legacy(&source, &allocator, &config, NULL) == MEF_ERR_CONFIG);
    source.ccd = saved_ccd;
    saved_string = source.origin; source.origin = NULL;
    assert(mef_config_from_legacy(&source, &allocator, &config, &diagnostic) == MEF_ERR_CONFIG);
    assert(config == NULL && state.outstanding == 0 && diagnostic != NULL);
    source.origin = saved_string;
    bad_allocator = allocator; bad_allocator.release = NULL;
    assert(mef_config_from_legacy(&source, &bad_allocator, &config, NULL) == MEF_ERR_CONFIG);
    assert(mef_config_from_legacy(NULL, NULL, &config, NULL) == MEF_ERR_CONFIG);
    assert(mef_config_from_legacy(&source, NULL, NULL, NULL) == MEF_ERR_CONFIG);
    for (cycle = 0; cycle < 20; ++cycle) {
        assert(mef_config_from_legacy(&source, &allocator, &config, NULL) == MEF_OK);
        mef_config_destroy(config); config = NULL;
        assert(state.outstanding == 0);
    }
    assert(mef_config_from_legacy(&source, NULL, &config, NULL) == MEF_OK);
    /* Destroy the complete source before inspection: no borrowed strings/CCDs. */
    source_release(&source);
    stream = fopen(argv[2], "w"); assert(stream != NULL);
    assert(mef_config_dump(config, stream) == MEF_OK);
    assert(fclose(stream) == 0);
    stream = fopen(argv[2], "r"); assert(stream != NULL);
    assert(mef_config_dump(config, stream) == MEF_ERR_IO);
    assert(fclose(stream) == 0);
    mef_config_destroy(config);
    mef_config_destroy(NULL);
    puts("PASS: 111 allocation failures; 20 ownership cycles; source-independent dump; invalid outputs and I/O failure");
    return 0;
}
