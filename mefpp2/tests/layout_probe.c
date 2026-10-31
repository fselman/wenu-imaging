/* Actual M4 C boundary controls (#182); synthetic files from layout_contract.py. */
#include "mef_layout.h"
#include "mef_cal_bias.h"
#include "mefp_lib.h"
#include <assert.h>

static const char *directory;
typedef struct { size_t calls, fail_at, owners; int persistent; } allocation_state;
static void *allocate(void *user, size_t size)
{
    allocation_state *s;
    void *p;
    s = user; ++s->calls;
    if (s->fail_at && (s->calls == s->fail_at || (s->persistent && s->calls >= s->fail_at))) return NULL;
    p = (malloc)(size); if (p != NULL) ++s->owners; return p;
}
static void deallocate(void *user, void *p)
{
    allocation_state *s;
    s = user; assert(p != NULL && s->owners); --s->owners; (free)(p);
}
static void filename(char *out, const char *leaf)
{
    size_t n, m;
    n = strlen(directory); m = strlen(leaf);
    assert(n + m + 2 < 4096);
    memcpy(out, directory, n); out[n] = '/';
    memcpy(out + n + 1, leaf, m + 1);
}
static mef_layout_options options(void)
{
    mef_layout_options o;
    memset(&o, 0, sizeof(o)); o.max_hdus = 16; o.max_header_bytes = 64 * 2880;
    o.identity_key = "DETID"; o.amplifier_key = "AMPID"; return o;
}
static mef_layout *read_layout(const char *leaf)
{
    char path[4096];
    mef_layout_options o;
    mef_layout *l;
    filename(path, leaf); o = options(); l = NULL;
    assert(mef_layout_read(path, &o, NULL, &l, NULL) == MEF_OK); return l;
}
static mef_detector_binding binding(const char *id)
{
    mef_detector_binding b;
    memset(&b, 0, sizeof(b)); b.detector_id = id; b.expected_header_id = id; b.hdu_index = -1;
    b.unit = "ADU"; b.readout_id = "configured-readout:tiny"; b.bin_x = b.bin_y = 1;
    b.active_x = b.active_y = 1; b.active_width = 10; b.active_height = 6;
    b.configuration_detector = 7; b.health = MEF_HEALTH_UNKNOWN; b.selection = MEF_OUTPUT_SELECTED;
    return b;
}
static mef_layout_map *map_one(const mef_layout *layout, const char *id)
{
    mef_layout_map *map;
    mef_detector_binding b;
    map = NULL; b = binding(id);
    assert(mef_layout_bind(layout, &b, 1, NULL, &map, NULL) == MEF_OK); return map;
}
static void failed_bind(mef_layout *layout, mef_detector_binding *b, size_t count)
{
    mef_layout_map *map;
    mef_error *error;
    map = NULL; error = NULL;
    assert(mef_layout_bind(layout, b, count, NULL, &map, &error) == MEF_ERR_INPUT);
    assert(map == NULL && mef_error_status(error) == MEF_ERR_INPUT); mef_error_destroy(error);
}
static void layouts(void)
{
    const char *names[3];
    mef_layout *layout;
    mef_layout_map *map;
    mef_detector_binding b;
    const mef_hdu_layout *hdus;
    const mef_bound_detector *view;
    image_t *image;
    size_t count;
    int i, j;
    char path[4096];
    mef_layout_options o;
    const float expected[5] = {0, 1, 32767, 32768, 65535};
    names[0] = "unsigned-primary.fits"; names[1] = "unsigned-extension.fits"; names[2] = "unsigned-mosaic.fits";
    for (i = 0; i < 3; ++i) {
        layout = read_layout(names[i]); hdus = mef_layout_hdus(layout, &count);
        assert(count == (size_t)(i + 1)); assert(hdus[i].hdu_index == i);
        assert(hdus[i].has_bzero && hdus[i].bzero == 32768.0);
        assert(hdus[i].has_extname == (i != 0) && !hdus[i].has_extver);
        b = binding("A"); b.hdu_index = i;
        if (i != 0) b.extname = "SCI";
        map = NULL; assert(mef_layout_bind(layout, &b, 1, NULL, &map, NULL) == MEF_OK);
        view = mef_layout_map_view(map, &count);
        assert(count == 1 && view[0].configuration_detector == 7);
        assert(view[0].identity_header_matched && view[0].physical_id[0] == '\0');
        mef_layout_destroy(layout); /* Bound map owns all required metadata/path. */
        image = NULL; assert(mef_layout_load(map, "A", &image, NULL) == MEF_OK);
        assert(image->lx == 10 && image->ly == 6);
        for (j = 0; j < 5; ++j) assert(image->data[j] == expected[j]);
        image_del(image); mef_layout_map_destroy(map);
    }
    layout = read_layout("telemetry.fits"); mef_layout_destroy(layout);
    filename(path, "hierarchical-id.fits"); o = options();
    o.identity_key = "HIERARCH ESO DET CHIP ID"; layout = NULL;
    assert(mef_layout_read(path, &o, NULL, &layout, NULL) == MEF_OK);
    b = binding("A"); b.expected_header_id = "configured-chip-A";
    map = NULL; assert(mef_layout_bind(layout, &b, 1, NULL, &map, NULL) == MEF_OK);
    mef_layout_map_destroy(map); mef_layout_destroy(layout);
    layout = read_layout("configured-primary.fits");
    b = binding("configured-logical-detector"); b.hdu_index = 0; b.expected_header_id = NULL;
    map = NULL; assert(mef_layout_bind(layout, &b, 1, NULL, &map, NULL) == MEF_OK);
    view = mef_layout_find(map, "configured-logical-detector");
    assert(view != NULL && !view->unit_from_header && !view->identity_header_matched);
    assert(view->physical_id[0] == '\0' && !strcmp(view->unit, "ADU"));
    image = NULL; assert(mef_layout_load(map, "configured-logical-detector", &image, NULL) == MEF_OK);
    assert(image->data[0] == 0 && image->data[4] == 65535);
    image_del(image); mef_layout_map_destroy(map); mef_layout_destroy(layout);
    puts("PASS: primary/one-extension/MEF selectors, independent EXTVER presence, exact unsigned scaling");
}
static void shuffled(void)
{
    mef_layout *science, *calibration, *only_b;
    mef_layout_map *s, *c, *subset;
    mef_detector_binding bindings[2];
    const mef_bound_detector *view;
    image_t *plane;
    size_t count;
    science = read_layout("science.fits"); calibration = read_layout("calibration.fits"); only_b = read_layout("only-b.fits");
    bindings[0] = binding("B"); bindings[1] = binding("A");
    bindings[1].health = MEF_HEALTH_BAD; bindings[1].selection = MEF_OUTPUT_EXCLUDED;
    s = c = NULL;
    assert(mef_layout_bind(science, bindings, 2, NULL, &s, NULL) == MEF_OK);
    assert(mef_layout_bind(calibration, bindings, 2, NULL, &c, NULL) == MEF_OK);
    view = mef_layout_map_view(s, &count); assert(count == 2);
    assert(!strcmp(view[0].detector_id, "A") && !strcmp(view[1].detector_id, "B"));
    assert(view[0].health == MEF_HEALTH_BAD && view[0].selection == MEF_OUTPUT_EXCLUDED);
    view = mef_layout_map_view(c, &count); assert(!strcmp(view[0].detector_id, "B"));
    assert(mef_layout_compatible(s, c, "ADU", "ADU", "A", NULL) == MEF_OK);
    subset = map_one(only_b, "B");
    assert(mef_layout_compatible(s, subset, "ADU", "ADU", NULL, NULL) == MEF_OK);
    assert(mef_layout_compatible(s, subset, "ADU", "ADU", "A", NULL) == MEF_ERR_INPUT);
    assert(mef_layout_compatible(s, c, "ADU", "ADU", "unknown", NULL) == MEF_ERR_INPUT);
    assert(mef_layout_compatible(s, c, "electron", "ADU", NULL, NULL) == MEF_ERR_INPUT);
    plane = NULL; assert(mef_layout_load(s, "B", &plane, NULL) == MEF_OK); assert(plane->data[0] == 201); image_del(plane);
    plane = NULL; assert(mef_layout_load(c, "B", &plane, NULL) == MEF_OK); assert(plane->data[0] == 21); image_del(plane);
    plane = NULL; assert(mef_layout_load(c, "A", &plane, NULL) == MEF_OK); assert(plane->data[0] == 11); image_del(plane);
    mef_layout_map_destroy(subset); mef_layout_map_destroy(s); mef_layout_map_destroy(c);
    mef_layout_destroy(science); mef_layout_destroy(calibration); mef_layout_destroy(only_b);
    puts("PASS: independent shuffled maps, science order, excluded health/selection and required reference");
}
static void selectors(void)
{
    mef_layout *l, *dup;
    mef_detector_binding b[2];
    mef_layout_map *map;
    mef_layout_map *active_science, *active_calibration;
    mef_layout *trimmed;
    l = read_layout("science.fits"); dup = read_layout("duplicate-id.fits");
    b[0] = binding("unknown"); failed_bind(l, b, 1);
    b[0] = binding("A"); b[0].hdu_index = 2; failed_bind(l, b, 1);
    b[0] = binding("A"); b[0].extname = "wrong"; failed_bind(l, b, 1);
    b[0] = binding("A"); b[0].has_extver = 1; b[0].extver = 1; failed_bind(l, b, 1);
    b[0] = binding("A"); failed_bind(dup, b, 1);
    b[0] = binding("A"); b[1] = b[0]; failed_bind(l, b, 2);
    b[0] = binding("A"); b[0].unit = "electron"; failed_bind(l, b, 1);
    b[0] = binding("A"); b[0].bin_x = 2; failed_bind(l, b, 1);
    b[0] = binding("A"); b[0].active_width = 11; failed_bind(l, b, 1);
    b[0] = binding("A"); b[0].hdu_index = 0; b[0].expected_header_id = NULL; failed_bind(l, b, 1);
    map = map_one(l, "A"); b[0] = binding("A");
    assert(mef_layout_bind(l, b, 1, NULL, &map, NULL) == MEF_ERR_INPUT);
    mef_layout_map_destroy(map);
    b[0] = binding("A"); b[0].active_x = 3; b[0].active_y = 2;
    b[0].active_width = 6; b[0].active_height = 4; active_science = NULL;
    assert(mef_layout_bind(l, b, 1, NULL, &active_science, NULL) == MEF_OK);
    trimmed = read_layout("trimmed.fits"); b[0].active_x = b[0].active_y = 1; active_calibration = NULL;
    assert(mef_layout_bind(trimmed, b, 1, NULL, &active_calibration, NULL) == MEF_OK);
    assert(mef_layout_compatible(active_science, active_calibration, "ADU", "ADU", NULL, NULL) == MEF_OK);
    mef_layout_map_destroy(active_science); mef_layout_map_destroy(active_calibration); mef_layout_destroy(trimmed);
    mef_layout_destroy(l); mef_layout_destroy(dup);
    l = read_layout("table.fits"); b[0] = binding("A"); b[0].hdu_index = 1; failed_bind(l, b, 1); mef_layout_destroy(l);
    puts("PASS: conflicting/absent selectors, duplicate/missing IDs, units/binning/active-region and non-image refusal");
}
static void bounds_and_ownership(void)
{
    char path[4096];
    mef_layout_options o;
    mef_layout *layout;
    mef_layout_map *map;
    mef_detector_binding b;
    mef_allocator a;
    mef_error *error;
    allocation_state state;
    size_t calls, i;
    int persistent;
    const char *bad[6];
    bad[0] = "duplicate-card.fits"; bad[1] = "bad-scale.fits"; bad[2] = "truncated.fits";
    bad[3] = "missing-end.fits"; bad[4] = "bad-identity.fits";
    bad[5] = "nonregular.fifo";
    for (i = 0; i < 6; ++i) {
        filename(path, bad[i]); o = options(); layout = NULL; error = NULL;
        assert(mef_layout_read(path, &o, NULL, &layout, &error) != MEF_OK && layout == NULL);
        assert(error != NULL); mef_error_destroy(error);
    }
    filename(path, "science.fits"); o = options(); o.max_hdus = 1; layout = NULL;
    assert(mef_layout_read(path, &o, NULL, &layout, NULL) == MEF_ERR_INPUT && layout == NULL);
    o = options(); o.max_header_bytes = 2880;
    assert(mef_layout_read(path, &o, NULL, &layout, NULL) == MEF_ERR_INPUT && layout == NULL);
    memset(&state, 0, sizeof(state)); a.user = &state; a.allocate = allocate; a.release = deallocate;
    o = options(); assert(mef_layout_read(path, &o, &a, &layout, NULL) == MEF_OK);
    calls = state.calls; mef_layout_destroy(layout); assert(state.owners == 0);
    for (persistent = 0; persistent < 2; ++persistent) for (i = 1; i <= calls; ++i) {
        state.calls = 0; state.fail_at = i; state.persistent = persistent; layout = NULL; error = NULL;
        assert(mef_layout_read(path, &o, &a, &layout, &error) == MEF_ERR_MEMORY && layout == NULL);
        if (error != NULL) assert(mef_error_status(error) == MEF_ERR_MEMORY);
        mef_error_destroy(error); assert(state.owners == 0);
    }
    state.calls = state.fail_at = 0; layout = read_layout("science.fits"); b = binding("A"); map = NULL;
    assert(mef_layout_bind(layout, &b, 1, &a, &map, NULL) == MEF_OK);
    calls = state.calls; mef_layout_map_destroy(map); assert(state.owners == 0);
    for (persistent = 0; persistent < 2; ++persistent) for (i = 1; i <= calls; ++i) {
        state.calls = 0; state.fail_at = i; state.persistent = persistent; map = NULL; error = NULL;
        assert(mef_layout_bind(layout, &b, 1, &a, &map, &error) == MEF_ERR_MEMORY && map == NULL);
        mef_error_destroy(error); assert(state.owners == 0);
    }
    mef_layout_destroy(layout);
    puts("PASS: header/HDU budgets, malformed/truncated inputs and all metadata-owner failure positions");
}
static void changed_source(void)
{
    char path[4096];
    mef_layout *layout;
    mef_layout_map *map;
    image_t *plane;
    FILE *stream;
    layout = read_layout("mutable.fits"); map = map_one(layout, "A"); mef_layout_destroy(layout);
    filename(path, "mutable.fits"); stream = fopen(path, "ab"); assert(stream != NULL);
    assert(fputc('x', stream) != EOF && fclose(stream) == 0);
    plane = NULL; assert(mef_layout_load(map, "A", &plane, NULL) == MEF_ERR_IO && plane == NULL);
    mef_layout_map_destroy(map);
    puts("PASS: changed source rejected before pixel loading (mutable synthetic fixture only)");
}
static void primary_bias(const char *paf)
{
    mef_bb *legacy;
    mef_config *config;
    mef_request *request;
    mef_context *context;
    mef_resolved_request_spec spec;
    mef_image_ref refs[3];
    mef_bpm_selection bpm;
    mef_bias_input input;
    mef_bias_result *result;
    mef_layout *layout;
    mef_layout_map *map;
    mef_detector_binding b;
    const mef_bound_detector *bound;
    image_t *planes[3];
    const image_t *borrowed[3], *signal;
    pixelvalue reference[24];
    const char *diagnostic, *kinds[3];
    char leaf[80], paths[3][4096];
    int k, i, detector, j;
    legacy = mef_bb_new_from_paf((char *)paf); assert(legacy != NULL); detector = legacy->nchips - 1;
    legacy->bias_minframe = 3; legacy->bias_kappa1 = 10.0;
    legacy->use_prescan = 0; legacy->use_overscan = 1; legacy->scanrej[0] = legacy->scanrej[1] = 0;
    legacy->ccd[detector].prescan_x[0] = 1; legacy->ccd[detector].prescan_x[1] = 2;
    legacy->ccd[detector].overscan_x[0] = 9; legacy->ccd[detector].overscan_x[1] = 10;
    legacy->ccd[detector].trimreg[0] = 3; legacy->ccd[detector].trimreg[1] = 8;
    legacy->ccd[detector].trimreg[2] = 2; legacy->ccd[detector].trimreg[3] = 5;
    kinds[0] = "primary"; kinds[1] = "extension"; kinds[2] = "mosaic";
    config = NULL; assert(mef_config_from_legacy(legacy, NULL, &config, &diagnostic) == MEF_OK);
    for (k = 0; k < 3; ++k) {
        memset(&spec, 0, sizeof(spec));
        for (i = 0; i < 3; ++i) {
            sprintf(leaf, "bias-%s-%d.fits", kinds[k], i); filename(paths[i], leaf);
            layout = read_layout(leaf); b = binding("A"); b.active_x = 3; b.active_y = 2;
            b.active_width = 6; b.active_height = 4; b.configuration_detector = (size_t)detector;
            map = NULL; assert(mef_layout_bind(layout, &b, 1, NULL, &map, NULL) == MEF_OK);
            bound = mef_layout_find(map, "A"); planes[i] = NULL;
            assert(mef_layout_load(map, "A", planes + i, NULL) == MEF_OK); borrowed[i] = planes[i];
            refs[i].asset_record_id = paths[i]; refs[i].resolved_path = paths[i]; refs[i].detector_id = "A";
            refs[i].hdu_index = bound->image.hdu_index;
            /* Validated index bridges the old coupled EXTNAME/EXTVER descriptor. */
            refs[i].extname = NULL; refs[i].extver = 0;
            assert(bound->configuration_detector == (size_t)detector);
            mef_layout_map_destroy(map); mef_layout_destroy(layout);
        }
        spec.request.operation = MEF_OP_CAL_BIAS; spec.request.operation_version = 1;
        spec.request.inputs = refs; spec.request.input_count = 3;
        spec.request.work_dir = directory; spec.request.output_dir = directory; spec.request.log_path = paths[0];
        bpm.detector_id = "A"; bpm.state = MEF_BPM_OMITTED; spec.bpm_selections = &bpm; spec.bpm_selection_count = 1;
        request = NULL; context = NULL; result = NULL;
        assert(mef_request_create_resolved(&spec, NULL, &request, NULL) == MEF_OK);
        assert(mef_context_create(config, request, NULL, &context, NULL) == MEF_OK); mef_request_destroy(request);
        input.frames = borrowed; input.count = 3; input.configuration_detector = (size_t)detector;
        assert(mef_cal_bias(context, &input, &result, NULL) == MEF_OK);
        signal = mef_bias_result_signal(result); assert(signal->lx == 6 && signal->ly == 4);
        if (k == 0) memcpy(reference, signal->data, sizeof(reference));
        else assert(!memcmp(reference, signal->data, sizeof(reference)));
        for (j = 0; j < 24; ++j) assert(signal->data[j] == (pixelvalue)(11 + j % 6 + 2 + 2 * (j / 6 + 1)));
        mef_bias_result_destroy(result); mef_context_destroy(context);
        for (i = 0; i < 3; ++i) image_del(planes[i]);
    }
    mef_config_destroy(config); mef_bb_del(legacy);
    puts("PASS: actual C bias entry exact primary/extension/mosaic pixels, configured detector independent of HDU");
}
int main(int argc, char **argv)
{
    assert(argc == 3); directory = argv[1];
    layouts(); shuffled(); selectors(); bounds_and_ownership(); primary_bias(argv[2]); changed_source();
    mef_layout_destroy(NULL); mef_layout_map_destroy(NULL);
    puts("PASS: M4 native layout contract (six groups); no normalization/CMOS/performance acceptance");
    return 0;
}
