/* Synthetic service memory/lifetime comparison; never reads astronomical pixels.
 * Compile the kernel separately with cube_del=mef_memory_cube_del and
 * image_getmedian_checked=mef_memory_master_stats. No production hooks needed.
 * Binary snapshots compare runs of this same compiler/ABI, not portable files.
 */
#include "mef_cal_bias.h"
#include "mefp_lib.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
#ifdef __APPLE__
#include <mach/mach.h>
#endif

static int active_width, active_height, expected_release, released;
static long resident_kib(void)
{
#ifdef __APPLE__
    mach_task_basic_info_data_t info;
    mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;
    if (task_info(mach_task_self(), MACH_TASK_BASIC_INFO,
            (task_info_t)&info, &count) != KERN_SUCCESS) return -1;
    return (long)(info.resident_size / 1024);
#else
    FILE *stream = fopen("/proc/self/status", "r");
    char line[256];
    long value = -1;
    if (!stream) return -1;
    while (fgets(line, sizeof(line), stream)) {
        if (sscanf(line, "VmRSS: %ld kB", &value) == 1) break;
    }
    fclose(stream);
    return value;
#endif
}
static void phase(const char *name)
{
    printf("PHASE %s rss_kib=%ld corrected_cube_released=%d\n",
        name, resident_kib(), released);
    fflush(stdout);
}
void mef_memory_cube_del(cube_t *cube)
{
    int working = cube && cube->lx == active_width && cube->ly == active_height;
    if (working) phase("corrected-cube-release-start");
    cube_del(cube);
    if (working) {
        released = 1;
        phase("corrected-cube-release-end");
    }
}
int mef_memory_master_stats(image_t *image, pixelvalue *value)
{
    if (image->lx == active_width && image->ly == active_height) {
        phase("kernel-master-statistics-start");
        assert(released == expected_release);
    }
    return image_getmedian_checked(image, value);
}
static pixelvalue raw_pixel(int frame, int x, int y, const int trim[4])
{
    int value = 1000 + y % 17 + frame;
    if (x >= trim[0]-1 && x < trim[1] && y >= trim[2]-1 && y < trim[3])
        value += 50 + 3 * frame + (x + 7 * y) % 23;
    return (pixelvalue)value;
}
static void snapshot(const char *path, const mef_bias_result *result)
{
    const image_t *image = mef_bias_result_signal(result);
    const mef_bias_measurements *measurements = mef_bias_result_measurements(result);
    mef_bias_measurements detached = *measurements;
    mef_bias_qc qc = *mef_bias_result_qc(result);
    FILE *stream = fopen(path, "wb");
    assert(stream);
    detached.frames = NULL;
    detached.high_offset_flags = NULL;
    qc.scan_median = qc.scan_stdev = NULL;
    qc.accepted = NULL;
    assert(fwrite(&qc, sizeof(qc), 1, stream) == 1);
    assert(fwrite(&detached, sizeof(detached), 1, stream) == 1);
    assert(fwrite(measurements->frames, sizeof(*measurements->frames),
        measurements->count, stream) == measurements->count);
    assert(fwrite(mef_bias_result_qc(result)->scan_median, sizeof(float), 10, stream) == 10);
    assert(fwrite(mef_bias_result_qc(result)->scan_stdev, sizeof(float), 10, stream) == 10);
    assert(fwrite(mef_bias_result_qc(result)->accepted, sizeof(int), 10, stream) == 10);
    assert(fwrite(image->data, sizeof(pixelvalue), (size_t)image->lx * image->ly, stream) ==
        (size_t)image->lx * image->ly);
    if (measurements->high_offset_flags) {
        const pixelmap *flags = measurements->high_offset_flags;
        assert(fwrite(flags->data, 1, (size_t)flags->lx * flags->ly, stream) ==
            (size_t)flags->lx * flags->ly);
    }
    assert(fclose(stream) == 0);
}
int main(int argc, char **argv)
{
    mef_bb *legacy;
    mef_config *config = NULL;
    mef_request *request = NULL;
    mef_context *context = NULL;
    mef_bias_result *result = NULL;
    mef_resolved_request_spec spec = {0};
    mef_image_ref refs[10] = {{0}}, calibration = {0};
    mef_calibration_role role = MEF_CAL_BPM;
    mef_bpm_selection selection = {"WIN1.CHIP1.OUT1", MEF_BPM_SELECTED};
    mef_bias_measurement_options options = {0};
    mef_bias_input input;
    image_t *frames[10];
    const image_t *borrowed[10];
    pixelmap *mask;
    char paths[10][80];
    int width, height, trim[4], wfi;
    const char *diagnostic = NULL;
    struct rusage usage;
    assert(argc == 6); /* PAF, legacy|full, small|wfi, snapshot, expected release 0|1 */
    assert(!strcmp(argv[2], "legacy") || !strcmp(argv[2], "full"));
    assert(!strcmp(argv[3], "small") || !strcmp(argv[3], "wfi"));
    assert(!strcmp(argv[5], "0") || !strcmp(argv[5], "1"));
    expected_release = !strcmp(argv[5], "1");
    wfi = !strcmp(argv[3], "wfi");
    width = wfi ? 2142 : 96; height = wfi ? 4128 : 80;
    trim[0] = wfi ? 51 : 5; trim[1] = wfi ? 2094 : 84;
    trim[2] = wfi ? 31 : 3; trim[3] = wfi ? 4127 : 78;
    active_width = trim[1] - trim[0] + 1;
    active_height = trim[3] - trim[2] + 1;
    eclipse_init(); set_logfile(0);
    legacy = mef_bb_new_from_paf(argv[1]);
    assert(legacy);
    legacy->use_prescan = 0; legacy->use_overscan = 1;
    legacy->bias_minframe = 3; legacy->bias_kappa1 = 10;
    legacy->bias_median_even_handling = MEDIAN_EVEN_LOWER;
    legacy->scanrej[0] = legacy->scanrej[1] = wfi ? 10 : 0;
    legacy->ccd[0].overscan_x[0] = wfi ? 2100 : 90;
    legacy->ccd[0].overscan_x[1] = width;
    memcpy(legacy->ccd[0].trimreg, trim, sizeof(trim));
    assert(mef_config_from_legacy(legacy, NULL, &config, &diagnostic) == MEF_OK);
    mask = pixelmap_new(width, height);
    assert(mask);
    for (int i = 0; i < 10; ++i) {
        frames[i] = image_new(width, height); assert(frames[i]); borrowed[i] = frames[i];
        for (int y = 0; y < height; ++y)
            for (int x = 0; x < width; ++x)
                frames[i]->data[(size_t)y * width + x] = raw_pixel(i, x, y, trim);
        snprintf(paths[i], sizeof(paths[i]), "/synthetic/wfi-memory-%02d.fits", i);
        refs[i].asset_record_id = refs[i].resolved_path = paths[i];
        refs[i].detector_id = selection.detector_id; refs[i].hdu_index = 1;
    }
    for (int y = trim[2]-1; y < trim[3]; ++y)
        for (int x = trim[0]-1; x < trim[1]; ++x)
            if ((x + 3*y) % 101 == 0) mask->data[(size_t)y * width + x] = 0;
    pixelmap_updatecount(mask);
    calibration = refs[0]; calibration.asset_record_id = "memory-bpm";
    calibration.resolved_path = "/synthetic/memory-bpm.fits";
    spec.request.operation = MEF_OP_CAL_BIAS; spec.request.operation_version = 1;
    spec.request.inputs = refs; spec.request.input_count = 10;
    spec.request.work_dir = "/synthetic/work"; spec.request.output_dir = "/synthetic/products";
    spec.request.log_path = "/synthetic/products/memory.log";
    spec.request.calibrations = &calibration; spec.request.calibration_count = 1;
    spec.calibration_roles = &role; spec.calibration_role_count = 1;
    spec.bpm_selections = &selection; spec.bpm_selection_count = 1;
    assert(mef_request_create_resolved(&spec, NULL, &request, NULL) == MEF_OK);
    assert(mef_context_create(config, request, NULL, &context, NULL) == MEF_OK);
    options.legacy_qc = !strcmp(argv[2], "legacy");
    options.bpm = mask; options.bpm_active_only = 1; options.high_sigma = 5;
    options.with_mad = options.ron_pair_set = options.ron_clip_enabled = !options.legacy_qc;
    options.ron_second = 1;
    options.ron_clip.sigma_low = options.ron_clip.sigma_high = 5;
    options.ron_clip.max_iterations = 10;
    input.frames = borrowed; input.count = 10; input.configuration_detector = 0;
    phase("service-start");
    assert(mef_cal_bias_measurements(context, &input, &options, &result, NULL) == MEF_OK);
    phase("service-complete");
    assert(released && mef_bias_result_qc(result)->accepted_frames == 10);
    for (int i = 0; i < 10; ++i)
        for (int y = 0; y < height; ++y)
            for (int x = 0; x < width; ++x)
                assert(frames[i]->data[(size_t)y * width + x] == raw_pixel(i, x, y, trim));
    if (strcmp(argv[4], "-")) snapshot(argv[4], result);
    getrusage(RUSAGE_SELF, &usage);
#ifdef __APPLE__
    printf("PEAK_RSS_KIB %ld\n", usage.ru_maxrss / 1024);
#else
    printf("PEAK_RSS_KIB %ld\n", usage.ru_maxrss);
#endif
    mef_bias_result_destroy(result); mef_context_destroy(context);
    mef_request_destroy(request); mef_config_destroy(config); mef_bb_del(legacy);
    for (int i = 0; i < 10; ++i) image_del(frames[i]);
    pixelmap_del(mask);
    puts("PASS: release order, ten accepted frames and every borrowed raw pixel unchanged");
    return 0;
}
