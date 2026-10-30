/* Actual qfits accounting plus test-only NULL-return seams in the selected
 * Eclipse/bias dependency units. No production allocator override. #144/#171. */
#include "../qfits5/src/xmemory.c"
#define main accepted_bias_contract_main
#include "bias_service_probe.c"
#undef main

static int dependency_active, dependency_persistent;
static size_t dependency_calls, dependency_fail_at, dependency_fired;
static const char *site_file[4096];
static int site_line[4096];
static int fail_dependency(const char *file, int line)
{
    if (!dependency_active) return 0;
    assert(dependency_calls < 4096);
    site_file[dependency_calls] = file;
    site_line[dependency_calls] = line;
    ++dependency_calls;
    if (dependency_fail_at && (dependency_calls == dependency_fail_at ||
        (dependency_persistent && dependency_calls >= dependency_fail_at))) {
        ++dependency_fired;
        return 1;
    }
    return 0;
}
void *mef_test_dependency_malloc(size_t size, const char *file, int line)
{
    if (fail_dependency(file, line)) return NULL;
    return xmemory_malloc(size, file, line);
}
void *mef_test_dependency_calloc(size_t n, size_t size, const char *file, int line)
{
    if (fail_dependency(file, line)) return NULL;
    return xmemory_calloc(n, size, file, line);
}
typedef struct {
    size_t bytes, ram, swap;
    int cells, swapfiles, files, mappings;
    unsigned long identities;
} resources;
static resources observe(void)
{
    resources value;
    int i;
    memset(&value, 0, sizeof(value));
    value.bytes = xmemory_table.alloc_total; value.ram = xmemory_table.alloc_ram;
    value.swap = xmemory_table.alloc_swap; value.cells = xmemory_table.ncells;
    value.swapfiles = xmemory_table.nswapfiles; value.files = xmemory_table.n_mm_files;
    value.mappings = xmemory_table.n_mm_mappings;
    for (i = 0; i < XMEMORY_MAXPTRS; ++i) if (xmemory_p_val[i] != NULL)
        value.identities ^= (unsigned long)xmemory_p_val[i] ^ xmemory_p_size[i];
    return value;
}
static void unchanged(resources before)
{
    resources after;
    after = observe();
    assert(before.bytes == after.bytes && before.ram == after.ram &&
        before.swap == after.swap && before.cells == after.cells &&
        before.swapfiles == after.swapfiles && before.files == after.files &&
        before.mappings == after.mappings && before.identities == after.identities);
}
static void arm(size_t position, int persistent)
{
    dependency_active = 1; dependency_calls = 0;
    dependency_fail_at = position; dependency_persistent = persistent;
    dependency_fired = 0;
}
static void disarm(void) { dependency_active = 0; }
static cube_t *tiny_cube(void)
{
    cube_t *cube;
    int i, j;
    cube = cube_new(3, 2, 3); assert(cube != NULL);
    for (i = 0; i < 3; ++i) {
        cube->plane[i] = image_new(3, 2); assert(cube->plane[i] != NULL);
        for (j = 0; j < 6; ++j) cube->plane[i]->data[j] = (pixelvalue)(i + j);
    }
    return cube;
}
static void unit(const char *name)
{
    resources before;
    image_t *image;
    cube_t *cube, *original;
    int valid[3] = {1, 1, 0};
    size_t failure;
    mef_bb work;
    mef_ccd detector;
    image = NULL; cube = NULL;
    if (!strcmp(name, "image-structure") || !strcmp(name, "image-pixels")) {
        before = observe();
        arm(!strcmp(name, "image-structure") ? 1 : 2, 0);
        image = image_new(3, 2); disarm();
        assert(image == NULL && dependency_fired == 1); unchanged(before);
    } else if (!strncmp(name, "median-", 7)) {
        cube = tiny_cube(); before = observe();
        failure = !strcmp(name, "median-structure") ? 1 : !strcmp(name, "median-pixels") ? 2 : 3;
        arm(failure, 0); image = cube_avg_median(cube); disarm();
        assert(image == NULL && dependency_fired == 1); unchanged(before);
        assert(cube->plane[2]->data[5] == 7); cube_del(cube);
    } else if (!strncmp(name, "reject-", 7)) {
        cube = tiny_cube(); original = cube; before = observe();
        arm(!strcmp(name, "reject-structure") ? 1 : 2, 0);
        assert(cube_reject_planes(&cube, valid) == -1); disarm();
        assert(dependency_fired == 1 && cube == original && cube->np == 3);
        unchanged(before); assert(cube->plane[2]->data[5] == 7); cube_del(cube);
    } else {
        assert(!strcmp(name, "overscan-owner"));
        cube = tiny_cube(); original = cube;
        memset(&work, 0, sizeof(work)); memset(&detector, 0, sizeof(detector));
        work.ccd = &detector; work.xtnum = work.nxts = 1;
        work.use_overscan = 1; detector.overscan_x[0] = 1; detector.overscan_x[1] = 2;
        detector.trimreg[0] = detector.trimreg[1] = 1;
        before = observe();
        assert(mef_cube_overscan_correction(cube, &work, "bias") == -1);
        unchanged(before); assert(cube == original && cube->np == 3); cube_del(cube);
    }
    printf("PASS: direct %s failure preserves owners/input\n", name);
}
static void sweep(mef_bb *legacy, int rejection)
{
    mef_context *context;
    mef_bias_input input;
    mef_bias_result *result;
    mef_error *error;
    mef_status status;
    image_t *frames[6];
    const image_t *borrowed[6];
    pixelvalue saved[6][60], expected[24];
    mef_ccd geometry;
    mef_allocator allocator;
    allocation_state own;
    resources before;
    size_t baseline_owners, calls, failure;
    int i, j, persistent, count, detector_index;
    count = 5;
    detector_index = legacy->nchips - 1;
    legacy->bias_minframe = 3; legacy->bias_kappa1 = rejection ? 1.0 : 10.0;
    /* Match the qualified fixture's valid 10x6 raw, 6x4 cropped geometry. */
    legacy->use_prescan = legacy->use_overscan = 1;
    legacy->scanrej[0] = legacy->scanrej[1] = 0;
    legacy->ccd[detector_index].prescan_x[0] = 1;
    legacy->ccd[detector_index].prescan_x[1] = 2;
    legacy->ccd[detector_index].overscan_x[0] = 9;
    legacy->ccd[detector_index].overscan_x[1] = 10;
    legacy->ccd[detector_index].trimreg[0] = 3;
    legacy->ccd[detector_index].trimreg[1] = 8;
    legacy->ccd[detector_index].trimreg[2] = 2;
    legacy->ccd[detector_index].trimreg[3] = 5;
    memcpy(&geometry, &legacy->ccd[detector_index], sizeof(geometry));
    for (i = 0; i < count; ++i) {
        frames[i] = image_new(10, 6); assert(frames[i] != NULL); borrowed[i] = frames[i];
        for (j = 0; j < 60; ++j) frames[i]->data[j] = (pixelvalue)(100 + j / 10 + 3 * i +
            ((j % 10 >= 2 && j % 10 <= 7) ? 10 + i + j % 10 + 2 * (j / 10) +
                (rejection && i == count - 1 ? 100 : 0) : 0));
        memcpy(saved[i], frames[i]->data, sizeof(saved[i]));
    }
    memset(&own, 0, sizeof(own));
    allocator.user = &own; allocator.allocate = allocate; allocator.release = release;
    context = context_for(legacy, count, 0, &allocator);
    baseline_owners = own.owners; before = observe();
    input.frames = borrowed; input.count = (size_t)count;
    input.configuration_detector = (size_t)detector_index;
    result = NULL; arm(0, 0);
    assert(mef_cal_bias(context, &input, &result, NULL) == MEF_OK); disarm();
    calls = dependency_calls; assert(calls > 10);
    memcpy(expected, mef_bias_result_signal(result)->data, sizeof(expected));
    for (i = 0; i < 24; ++i) {
        int x, y; x = i % 6; y = i / 6;
        assert(expected[i] == (pixelvalue)((rejection ? 11 : 12) + x + 2 + 2 * (y + 1)));
    }
    mef_bias_result_destroy(result); unchanged(before); assert(own.owners == baseline_owners);
    printf("SITES: rejection=%d positions=%lu\n", rejection, (unsigned long)calls);
    for (i = 0; i < (int)calls; ++i) printf("SITE %d %s:%d\n", i + 1, site_file[i], site_line[i]);
    for (persistent = 0; persistent <= 1; ++persistent) for (failure = 1; failure <= calls; ++failure) {
        result = NULL; error = NULL; arm(failure, persistent);
        status = mef_cal_bias(context, &input, &result, &error); disarm();
        assert(dependency_fired > 0 && status != MEF_OK && result == NULL);
        assert(error == NULL || mef_error_status(error) == status); mef_error_destroy(error);
        unchanged(before); assert(own.owners == baseline_owners);
        assert(memcmp(&geometry, &legacy->ccd[detector_index], sizeof(geometry)) == 0);
        for (i = 0; i < count; ++i) assert(memcmp(saved[i], frames[i]->data, sizeof(saved[i])) == 0);
    }
    /* Recovery in the same context proves no damaged reusable state. */
    for (i = 0; i < 5; ++i) {
        result = NULL; arm(0, 0); assert(mef_cal_bias(context, &input, &result, NULL) == MEF_OK); disarm();
        assert(memcmp(expected, mef_bias_result_signal(result)->data, sizeof(expected)) == 0);
        mef_bias_result_destroy(result); unchanged(before); assert(own.owners == baseline_owners);
    }
    mef_context_destroy(context); assert(own.owners == 0);
    for (i = 0; i < count; ++i) image_del(frames[i]);
    printf("PASS: rejection=%d all %lu dependency positions x2, recovery and preserved sources\n",
        rejection, (unsigned long)calls);
}
int main(int argc, char **argv)
{
    const char *names[] = {"image-structure", "image-pixels", "median-structure", "median-pixels",
        "median-timeline", "reject-structure", "reject-planes", "overscan-owner"};
    mef_bb *legacy;
    int i;
    if (argc == 2 && !strncmp(argv[1], "--site=", 7)) { unit(argv[1] + 7); return 0; }
    assert(argc == 3);
    /* Reuse all eight accepted exact legacy/FITS/QC profiles and owner controls. */
    assert(accepted_bias_contract_main(argc, argv) == 0);
    for (i = 0; i < 8; ++i) unit(names[i]);
    legacy = mef_bb_new_from_paf(argv[1]); assert(legacy != NULL);
    sweep(legacy, 0); sweep(legacy, 1); mef_bb_del(legacy);
    puts("PASS: Eclipse dependency failure contract");
    return 0;
}
