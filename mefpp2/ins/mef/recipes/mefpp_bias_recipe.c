/* Coordinate a detector-local master-bias recipe from configuration and raw FITS.
 * Read main first: admit every binding, calibrate detectors, then assemble FITS
 * and write the associated ASDF archive. Failed on-disk work remains evidence.
 */

#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias_product_qc.h"
#include "mef_bias_qc_fits.h"
#include "mef_bias_recipe_config.h"
#include "qfits.h"
#include "mef_config_toml.h"
#include "mef_mef_assemble.h"
#include "mefp_lib.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef realloc
#undef free

enum { CFG, READOUT, BINX, BINY, BPM, BPM_HDU, GOOD, COORDS, BPM_NAME, AMP, RAW_NAME, FIELD_COUNT };

typedef struct {
    const char *detector_id, *option_values[FIELD_COUNT];
    int *hdus;
    size_t hdu_count, configuration_index;
    int bin_x, bin_y, bpm_hdu, bpm_good_value, bpm_active_only;
    char *bpm_path;
    mef_bias_settings settings;
    mef_layout_map **raw_layouts, *mask_map;
    char temporary_path[MEF_PRODUCT_PATH_SIZE];
    mef_assembly_detector assembly;
} detector_plan;

typedef struct {
    const char *paf_path, *toml_path, *bias_list_path, *output_path, *output_directory,
        *reference_detector_id, *mad_option, *ron_first_option, *ron_second_option,
        *high_sigma_option;
    detector_plan *detectors;
    size_t detector_count;
} bias_recipe_arguments;

static int parse_nonnegative_int(const char *text, int *parsed_value)
{
    char *end;
    long parsed_number;
    if (text == NULL || !*text) {
        return 0;
    }
    errno = 0;
    parsed_number = strtol(text, &end, 10);
    if (errno || *end || parsed_number < 0 || parsed_number > INT_MAX) {
        return 0;
    }
    *parsed_value = (int)parsed_number;
    return 1;
}

static int set_option_once(const char **slot, const char *value)
{
    if (*slot != NULL) {
        return 0;
    }
    *slot = value;
    return 1;
}

static int parse_recipe_arguments(int argc, char **argv, bias_recipe_arguments *arguments)
{
    static const char *keys[FIELD_COUNT] = {"--config-detector", "--readout-id", "--bin-x",
        "--bin-y", "--input-bpm", "--bpm-hdu", "--bpm-good-value", "--bpm-coordinates",
        "--bpm-expected-extname", "--amplifier-id", "--raw-expected-extname"};
    int i, j;
    detector_plan *detector = NULL;
    if (argc < 3 || strcmp(argv[1], "cal") || strcmp(argv[2], "bias")) {
        return 0;
    }
    arguments->detectors = calloc((size_t)argc / 2, sizeof(*arguments->detectors));
    if (arguments->detectors == NULL) {
        return 0;
    }
    for (i = 3; i < argc; i += 2) {
        const char *key = argv[i], *option_value;
        if (i + 1 >= argc || !*argv[i + 1]) {
            return 0;
        }
        option_value = argv[i + 1];
        if (!strcmp(key, "--pafname")) {
            if (!set_option_once(&arguments->paf_path, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--config")) {
            if (!set_option_once(&arguments->toml_path, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--bias")) {
            if (!set_option_once(&arguments->bias_list_path, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--output")) {
            if (!set_option_once(&arguments->output_path, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--output-dir")) {
            if (!set_option_once(&arguments->output_directory, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--reference-detector")) {
            if (!set_option_once(&arguments->reference_detector_id, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--mad")) {
            if (!set_option_once(&arguments->mad_option, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--ron-first")) {
            if (!set_option_once(&arguments->ron_first_option, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--ron-second")) {
            if (!set_option_once(&arguments->ron_second_option, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--high-sigma")) {
            if (!set_option_once(&arguments->high_sigma_option, option_value)) {
                return 0;
            }
            continue;
        }
        if (!strcmp(key, "--detector-id")) {
            if (arguments->detector_count == 4096) {
                return 0;
            }
            detector = arguments->detectors + arguments->detector_count++;
            detector->detector_id = option_value;
            continue;
        }
        if (detector == NULL) {
            return 0;
        }
        if (!strcmp(key, "--hdu")) {
            int frame_count, *next;
            if (!parse_nonnegative_int(option_value, &frame_count)) {
                return 0;
            }
            next = realloc(detector->hdus, (detector->hdu_count + 1) * sizeof(*next));
            if (next == NULL) {
                return 0;
            }
            detector->hdus = next;
            detector->hdus[detector->hdu_count++] = frame_count;
            continue;
        }
        for (j = 0; j < FIELD_COUNT; ++j) {
            if (!strcmp(key, keys[j])) {
                break;
            }
        }
        if (j == FIELD_COUNT || !set_option_once(detector->option_values + j, option_value)) {
            return 0;
        }
    }
    if ((arguments->paf_path == NULL) == (arguments->toml_path == NULL) ||
        arguments->bias_list_path == NULL || arguments->reference_detector_id == NULL ||
        arguments->mad_option == NULL ||
        (strcmp(arguments->mad_option, "yes") && strcmp(arguments->mad_option, "no")) ||
        !arguments->detector_count ||
        (arguments->ron_first_option == NULL) != (arguments->ron_second_option == NULL)) {
        return 0;
    }
    return 1;
}

static int bind_detector_inputs(detector_plan *detector, mef_layout *const *layouts,
    size_t frame_count, const mef_config *config, mef_error **error)
{
    mef_detector_binding binding;
    size_t i;
    int configured;
    const mef_bpm_policy *policy = &mef_config_processing(config)->bpm;
    if (!parse_nonnegative_int(detector->option_values[CFG], &configured) ||
        !parse_nonnegative_int(detector->option_values[BINX], &detector->bin_x) ||
        detector->bin_x == 0 ||
        !parse_nonnegative_int(detector->option_values[BINY], &detector->bin_y) ||
        detector->bin_y == 0 || !detector->option_values[READOUT] ||
        !detector->option_values[AMP] || !detector->option_values[BPM] ||
        (detector->hdu_count != 1 && detector->hdu_count != frame_count)) {
        return 0;
    }
    detector->configuration_index = (size_t)configured;
    if (mef_config_bias_settings(config, detector->configuration_index, &detector->settings) !=
        MEF_OK) {
        return 0;
    }
    detector->raw_layouts = calloc(frame_count, sizeof(*detector->raw_layouts));
    if (detector->raw_layouts == NULL) {
        return 0;
    }
    memset(&binding, 0, sizeof(binding));
    binding.detector_id = detector->detector_id;
    binding.unit = "ADU";
    binding.extname = detector->option_values[RAW_NAME]
                          ? (strcmp(detector->option_values[RAW_NAME], "omitted")
                                    ? detector->option_values[RAW_NAME]
                                    : NULL)
                          : detector->detector_id;
    binding.readout_id = detector->option_values[READOUT];
    binding.bin_x = detector->bin_x;
    binding.bin_y = detector->bin_y;
    binding.active_x = detector->settings.trim[0];
    binding.active_y = detector->settings.trim[2];
    binding.active_width = detector->settings.trim[1] - detector->settings.trim[0] + 1;
    binding.active_height = detector->settings.trim[3] - detector->settings.trim[2] + 1;
    binding.configuration_detector = detector->configuration_index;
    binding.health = MEF_HEALTH_UNKNOWN;
    binding.selection = MEF_OUTPUT_SELECTED;
    for (i = 0; i < frame_count; ++i) {
        binding.hdu_index = detector->hdus[detector->hdu_count == 1 ? 0 : i];

        /* Explicit source HDU 0 or extension: logical ID and EXTNAME are independent. */

        if (binding.hdu_index < 0 ||
            mef_layout_bind(layouts[i], &binding, 1, NULL, detector->raw_layouts + i, error) !=
                MEF_OK ||
            mef_layout_compatible(detector->raw_layouts[0], detector->raw_layouts[i], "ADU", "ADU",
                NULL, error) != MEF_OK) {
            return 0;
        }
        {
            const mef_bound_detector *raw =
                mef_layout_find(detector->raw_layouts[i], detector->detector_id);
            if (raw->image.axes[0] == 0 || raw->image.axes[1] == 0 ||
                raw->image.axes[0] > INT_MAX || raw->image.axes[1] > INT_MAX ||
                raw->image.axes[0] > INT_MAX / raw->image.axes[1]) {
                return 0;
            }
        }
    }
    if (!strcmp(detector->option_values[BPM], "omitted")) {
        for (i = BPM_HDU; i <= BPM_NAME; ++i) {
            if (detector->option_values[i]) {
                return 0;
            }
        }
    } else {
        mef_layout_options options;
        mef_layout *layout = NULL;
        mef_status status;
        const mef_bound_detector *raw, *mask;
        if (!parse_nonnegative_int(detector->option_values[BPM_HDU], &detector->bpm_hdu) ||
            !detector->option_values[COORDS] ||
            (strcmp(detector->option_values[COORDS], "raw") &&
                strcmp(detector->option_values[COORDS], "active"))) {
            return 0;
        }
        if (policy->supplied) {
            detector->bpm_good_value = policy->bad_when_nonzero ? 0 : 1;
            if (detector->option_values[GOOD]) {
                int legacy_good;
                if (policy->encoding != MEF_BPM_BINARY ||
                    !parse_nonnegative_int(detector->option_values[GOOD], &legacy_good) ||
                    legacy_good != detector->bpm_good_value) {
                    return 0;
                }
            }
        } else if (!parse_nonnegative_int(
                       detector->option_values[GOOD], &detector->bpm_good_value) ||
                   detector->bpm_good_value > 1) {
            return 0;
        }
        detector->bpm_path = realpath(detector->option_values[BPM], NULL);
        if (detector->bpm_path == NULL) {
            return 0;
        }
        detector->bpm_active_only = !strcmp(detector->option_values[COORDS], "active");
        memset(&options, 0, sizeof(options));
        options.max_hdus = 4096;
        options.max_header_bytes = 16 * 1024 * 1024;
        binding.hdu_index = detector->bpm_hdu;
        binding.unit = "mask";
        binding.extname = detector->option_values[BPM_NAME];
        if (detector->bpm_active_only) {
            binding.active_x = 1;
            binding.active_y = 1;
        }
        status = mef_layout_read(detector->bpm_path, &options, NULL, &layout, error);
        if (status == MEF_OK) {
            status = mef_layout_bind(layout, &binding, 1, NULL, &detector->mask_map, error);
        }
        mef_layout_destroy(layout);
        if (status != MEF_OK || mef_layout_compatible(detector->raw_layouts[0], detector->mask_map,
                                    "ADU", "mask", NULL, error) != MEF_OK) {
            return 0;
        }
        raw = mef_layout_find(detector->raw_layouts[0], detector->detector_id);
        mask = mef_layout_find(detector->mask_map, detector->detector_id);
        if (mask->image.axes[0] != (size_t)(detector->bpm_active_only ? binding.active_width
                                                                      : (int)raw->image.axes[0]) ||
            mask->image.axes[1] != (size_t)(detector->bpm_active_only ? binding.active_height
                                                                      : (int)raw->image.axes[1])) {
            return 0;
        }
    }
    return 1;
}

static int process_bias_detector(detector_plan *detector, size_t index, size_t frame_count,
    char *const *raw_paths, const mef_config *config, const mef_product_paths *paths,
    const char *private_work_directory, const mef_bias_measurement_options *options,
    mef_bias_product_qc *archive, mef_error **error)
{
    mef_image_ref *input_references = NULL, calibration;
    mef_request *request = NULL;
    mef_context *context = NULL;
    mef_resolved_request_spec request_spec;
    mef_bpm_selection selection;
    mef_calibration_role role = MEF_CAL_BPM;
    mef_bias_result *result = NULL;
    mef_status status = MEF_ERR_INPUT;
    mef_bias_measurement_options measurements = *options;
    qfits_header *qc_header = NULL;
    char qc_message[256];
    pixelmap *mask = NULL, *loaded = NULL;
    const mef_bound_detector *first;
    size_t i;
    int succeeded = 0, x, y;
    const image_t *image;
    input_references = calloc(frame_count, sizeof(*input_references));
    if (input_references == NULL) {
        goto done;
    }
    for (i = 0; i < frame_count; ++i) {
        const mef_bound_detector *bound_input =
            mef_layout_find(detector->raw_layouts[i], detector->detector_id);
        input_references[i].asset_record_id = raw_paths[i];
        input_references[i].resolved_path = raw_paths[i];
        input_references[i].detector_id = detector->detector_id;
        input_references[i].hdu_index = bound_input->image.hdu_index;
        if (bound_input->image.has_extname && bound_input->image.has_extver) {
            input_references[i].extname = bound_input->image.extname;
            input_references[i].extver = bound_input->image.extver;
        }
    }
    first = mef_layout_find(detector->raw_layouts[0], detector->detector_id);
    if (detector->mask_map) {
        const mef_bpm_policy *policy = &mef_config_processing(config)->bpm;
        status = policy->supplied ? mef_layout_load_bpm_policy(detector->mask_map,
                                        detector->detector_id, policy, &loaded, error)
                                  : mef_layout_load_bpm(detector->mask_map, detector->detector_id,
                                        detector->bpm_good_value, &loaded, error);
        if (status != MEF_OK) {
            goto done;
        }
        if (detector->bpm_active_only) {
            mask = pixelmap_new((int)first->image.axes[0], (int)first->image.axes[1]);
            if (mask == NULL) {
                goto done;
            }
            for (y = 0; y < loaded->ly; ++y) {
                for (x = 0; x < loaded->lx; ++x) {
                    mask->data[(y + detector->settings.trim[2] - 1) * mask->lx + x +
                               detector->settings.trim[0] - 1] = loaded->data[y * loaded->lx + x];
                }
            }
            pixelmap_updatecount(mask);
        } else {
            mask = loaded;
            loaded = NULL;
        }
        measurements.bpm = mask;
        measurements.bpm_active_only = detector->bpm_active_only;
    }
    memset(&request_spec, 0, sizeof(request_spec));
    memset(&calibration, 0, sizeof(calibration));
    request_spec.request.operation = MEF_OP_CAL_BIAS;
    request_spec.request.operation_version = 1;
    request_spec.request.inputs = input_references;
    request_spec.request.input_count = frame_count;
    request_spec.request.work_dir = private_work_directory;
    request_spec.request.output_dir = paths->directory;
    request_spec.request.log_path = paths->log;
    selection.detector_id = detector->detector_id;
    selection.state = mask ? MEF_BPM_SELECTED : MEF_BPM_OMITTED;
    request_spec.bpm_selections = &selection;
    request_spec.bpm_selection_count = 1;
    if (mask) {
        calibration.asset_record_id = detector->bpm_path;
        calibration.resolved_path = detector->bpm_path;
        calibration.detector_id = detector->detector_id;
        calibration.hdu_index = detector->bpm_hdu;
        request_spec.request.calibrations = &calibration;
        request_spec.request.calibration_count = 1;
        request_spec.calibration_roles = &role;
        request_spec.calibration_role_count = 1;
    }
    status = mef_request_create_resolved(&request_spec, NULL, &request, error);
    if (status == MEF_OK) {
        status = mef_context_create(config, request, NULL, &context, error);
    }
    if (status != MEF_OK) {
        goto done;
    }
    if (snprintf(detector->temporary_path, sizeof(detector->temporary_path),
            "%s/detector-%06lu.fits", private_work_directory,
            (unsigned long)index) >= (int)sizeof(detector->temporary_path)) {
        goto done;
    }

    /* [BIAS-DETECTOR-CALIBRATION]
     * The file adapter owns the loaded raws; the result owns its corrected master.
     */

    status = mef_bias_from_files_measurements(context,
        (const mef_layout_map *const *)detector->raw_layouts, frame_count, detector->detector_id,
        &measurements, &result, error);
    if (status != MEF_OK ||
        !mef_bias_product_qc_add(archive, index, detector->detector_id,
            detector->option_values[AMP], detector->option_values[READOUT],
            detector->configuration_index, detector->bin_x, detector->bin_y, result, &measurements,
            &detector->settings, (int)first->image.axes[1], detector->bpm_path, detector->bpm_hdu,
            detector->bpm_good_value)) {
        goto done;
    }
    if (mef_bias_qc_fits_header(
            mef_bias_product_qc_view(archive), index, &qc_header, qc_message, sizeof(qc_message))) {
        fprintf(stderr, "%s\n", qc_message);
        goto done;
    }
    status = mef_bias_publish_with_header_named(config, result, detector->configuration_index,
        detector->temporary_path, qc_header, detector->detector_id, error);
    if (status != MEF_OK) {
        goto done;
    }
    image = mef_bias_result_signal(result);
    detector->assembly.path = detector->temporary_path;
    detector->assembly.detector_id = detector->detector_id;
    detector->assembly.configuration_detector = detector->configuration_index;
    detector->assembly.output_hdu = index + 1;
    detector->assembly.width = image->lx;
    detector->assembly.height = image->ly;
    detector->assembly.bitpix = BPP_DEFAULT;
    detector->assembly.bscale = 1;
    detector->assembly.bzero = 0;
    succeeded = 1;
done:
    qfits_header_destroy(qc_header);
    mef_bias_result_destroy(result);
    mef_context_destroy(context);
    mef_request_destroy(request);
    pixelmap_del(mask);
    pixelmap_del(loaded);
    free(input_references);
    return succeeded;
}

int main(int argc, char **argv)
{
    bias_recipe_arguments arguments;
    mef_bias_recipe_config *recipe_document = NULL;
    int expanded_argc = argc;
    char **expanded_argv = argv;
    mef_product_paths paths;
    char recipe_start[MEF_RECIPE_TIME_SIZE], message[512] = "";
    char invocation_directory[MEF_PRODUCT_PATH_SIZE],
        private_work_directory[MEF_PRODUCT_PATH_SIZE] = "";
    char *config_path = NULL, *listing_path = NULL, **raw_paths = NULL, *end;
    mef_config *config = NULL;
    mef_config_document *document = NULL;
    mef_bb *legacy = NULL;
    mef_layout **layouts = NULL;
    mef_layout_options layout_options;
    mef_error *error = NULL;
    mef_bias_product_qc *archive = NULL;
    mef_assembly_detector *assembly = NULL;
    framelist *frames = NULL;
    FILE *log = NULL;
    int log_descriptor = -1, succeeded = 0, first, second;
    mef_bias_measurement_options options;
    const char *diagnostic = NULL;
    mef_status status;
    size_t i, j, frame_count = 0;
    int reference_found = 0;
    memset(&arguments, 0, sizeof(arguments));
    memset(&options, 0, sizeof(options));

    /* [BIAS-RECIPE-ADMISSION]
     * Resolve configuration and all detector bindings before creating products.
     * Sample the recipe-start instant once, independently of detector count.
     */

    if (mef_recipe_start_time(recipe_start, sizeof(recipe_start), message, sizeof(message)) ||
        getcwd(invocation_directory, sizeof(invocation_directory)) == NULL) {
        goto done;
    }
    if (!mef_bias_recipe_expand(argc, argv, &expanded_argc, &expanded_argv, &recipe_document,
            message, sizeof(message))) {
        goto done;
    }
    if (!parse_recipe_arguments(expanded_argc, expanded_argv, &arguments)) {
        goto usage;
    }
    if (mef_product_paths_resolve(invocation_directory, arguments.output_directory,
            arguments.output_path, "CMDP", recipe_start, 1, &paths, message, sizeof(message))) {
        goto done;
    }
    {
        const char *name = strrchr(paths.fits, '/') + 1;
        if (strlen(name) > 68 || strchr(name, '\'')) {
            strcpy(message, "Final basename exceeds the existing single-card ORIGFILE contract");
            goto done;
        }
        for (i = 0; name[i]; ++i) {
            if ((unsigned char)name[i] < 32 || (unsigned char)name[i] > 126) {
                strcpy(message, "Final FITS basename must use printable ASCII");
                goto done;
            }
        }
    }
    options.with_mad = !strcmp(arguments.mad_option, "yes");
    options.high_sigma = 5;
    if (arguments.high_sigma_option) {
        errno = 0;
        options.high_sigma = strtod(arguments.high_sigma_option, &end);
        if (errno || end == arguments.high_sigma_option || *end || !isfinite(options.high_sigma) ||
            options.high_sigma <= 0) {
            goto usage;
        }
    }
    if (arguments.ron_first_option) {
        if (!parse_nonnegative_int(arguments.ron_first_option, &first) ||
            !parse_nonnegative_int(arguments.ron_second_option, &second) || first == second) {
            goto usage;
        }
        options.ron_pair_set = 1;
        options.ron_first = (size_t)first;
        options.ron_second = (size_t)second;
    }
    config_path = realpath(arguments.paf_path ? arguments.paf_path : arguments.toml_path, NULL);
    listing_path = realpath(arguments.bias_list_path, NULL);
    if (config_path == NULL || listing_path == NULL) {
        strcpy(message, "Missing explicit configuration or bias list");
        goto done;
    }
    eclipse_init();
    set_logfile(0);
    if (arguments.paf_path) {
        legacy = mef_bb_new_from_paf(config_path);
        if (legacy == NULL) {
            goto done;
        }
        status = mef_config_from_legacy(legacy, NULL, &config, &diagnostic);
    } else {
        mef_config_toml_initialize();
        status =
            mef_config_document_from_toml(config_path, NULL, &document, message, sizeof(message));
        if (status == MEF_OK) {
            status = mef_config_clone(
                mef_config_document_settings(document), NULL, &config, &diagnostic);
        }
    }
    if (status != MEF_OK) {
        goto done;
    }
    {
        const mef_processing_policy *policy = mef_config_processing(config);
        const char *requested = mef_bias_recipe_median_even_handling(recipe_document);
        if (requested) {
            mef_processing_policy effective = *policy;
            int mode = !strcmp(requested, "lower") ? MEDIAN_EVEN_LOWER : MEDIAN_EVEN_AVERAGE;
            if (policy->median_even_supplied && policy->median_even_handling != mode) {
                strcpy(message, "Conflicting explicit median_even_handling settings");
                goto done;
            }
            effective.median_even_supplied = 1;
            effective.median_even_handling = mode;
            mef_config_initialize_processing(config, &effective);
        }

        options.ron_clip_enabled = policy->ron_clip_enabled;
        options.ron_clip.sigma_low = policy->ron_clip_low;
        options.ron_clip.sigma_high = policy->ron_clip_high;
        options.ron_clip.max_iterations = policy->ron_clip_max_iterations;
        if (options.ron_clip_enabled && !options.ron_pair_set) {
            strcpy(message, "Clipped RON requires an explicit raw pair");
            goto done;
        }
    }
    mef_bb_del(legacy);
    legacy = NULL;
    frames = framelist_load(listing_path);
    if (frames == NULL || frames->n < 3 || frames->n > 100000) {
        strcpy(message, "Require an explicit list of at least three bias inputs");
        goto done;
    }
    frame_count = (size_t)frames->n;
    if (options.ron_pair_set &&
        (options.ron_first >= frame_count || options.ron_second >= frame_count)) {
        goto usage;
    }
    layouts = calloc(frame_count, sizeof(*layouts));
    raw_paths = calloc(frame_count, sizeof(*raw_paths));
    assembly = calloc(arguments.detector_count, sizeof(*assembly));
    if (layouts == NULL || raw_paths == NULL || assembly == NULL) {
        goto done;
    }
    memset(&layout_options, 0, sizeof(layout_options));
    layout_options.max_hdus = 4096;
    layout_options.max_header_bytes = 16 * 1024 * 1024;

    /* Header-only admission of every input/detector precedes output creation. */

    for (i = 0; i < frame_count; ++i) {
        if (frames->name[i][0] != '/' || (raw_paths[i] = realpath(frames->name[i], NULL)) == NULL) {
            goto done;
        }
        for (j = 0; j < i; ++j) {
            if (!strcmp(raw_paths[i], raw_paths[j])) {
                strcpy(message, "Duplicate raw input path");
                goto done;
            }
        }
        if (mef_layout_read(raw_paths[i], &layout_options, NULL, layouts + i, &error) != MEF_OK) {
            goto done;
        }
    }
    for (i = 0; i < arguments.detector_count; ++i) {
        detector_plan *detector = arguments.detectors + i;
        if (!bind_detector_inputs(detector, layouts, frame_count, config, &error)) {
            strcpy(message, "Invalid explicit detector/BPM binding or geometry");
            goto done;
        }
        if (!strcmp(detector->detector_id, arguments.reference_detector_id)) {
            reference_found = 1;
        }

        /* Different logical detectors may not reuse one physical input plane. */

        for (j = 0; j < i; ++j) {
            size_t frame;
            for (frame = 0; frame < frame_count; ++frame) {
                const mef_bound_detector *now =
                    mef_layout_find(detector->raw_layouts[frame], detector->detector_id);
                const mef_bound_detector *old = mef_layout_find(
                    arguments.detectors[j].raw_layouts[frame], arguments.detectors[j].detector_id);
                if (now->image.hdu_index == old->image.hdu_index) {
                    strcpy(message, "Selected detector catalogue reuses an input HDU");
                    goto done;
                }
            }
        }
        for (j = 0; j < i; ++j) {
            if (!strcmp(detector->detector_id, arguments.detectors[j].detector_id) ||
                detector->configuration_index == arguments.detectors[j].configuration_index) {
                strcpy(message, "Duplicate detector identity or configuration slot");
                goto done;
            }
        }
    }
    if (!reference_found) {
        strcpy(message, "Reference detector must be in the selected set");
        goto done;
    }
    archive = mef_bias_product_qc_new(config, &paths, recipe_start, MEFPP_CANDIDATE_REVISION,
        (const char *const *)raw_paths, frame_count, arguments.detector_count);
    if (archive == NULL) {
        goto done;
    }
    log_descriptor = open(paths.log, O_WRONLY | O_CREAT | O_EXCL | O_APPEND, 0600);
    if (log_descriptor < 0) {
        goto done;
    }
    log = fdopen(log_descriptor, "a");
    if (log == NULL) {
        goto done;
    }
    log_descriptor = -1;
    fprintf(log,
        "RECIPE cal.bias\nSTART %s\nSOURCE %s\nINVOCATION %s\nCONFIG %s\nINPUT_LIST %s\nFITS "
        "%s\nASDF %s\n",
        recipe_start, MEFPP_CANDIDATE_REVISION, invocation_directory, config_path, listing_path,
        paths.fits, paths.asdf);
    for (i = 0; i < frame_count; ++i) {
        fprintf(log, "INPUT %lu %s\n", (unsigned long)i, raw_paths[i]);
    }
    if (snprintf(private_work_directory, sizeof(private_work_directory), "%s/.mefpp-bias-XXXXXX",
            paths.directory) >= (int)sizeof(private_work_directory) ||
        mkdtemp(private_work_directory) == NULL) {
        private_work_directory[0] = '\0';
        goto done;
    }
    fprintf(log, "PRIVATE_WORK %s\n", private_work_directory);
    if (fflush(log)) {
        goto done;
    }
    set_logfilename(paths.log);
    set_logfile(1);

    /* [BIAS-DETECTOR-LOOP]
     * Each detector has its own corrections, frame membership and private MEF.
     */

    for (i = 0; i < arguments.detector_count; ++i) {
        fprintf(log, "DETECTOR_START %lu %s CONFIGURATION %lu\n", (unsigned long)i,
            arguments.detectors[i].detector_id,
            (unsigned long)arguments.detectors[i].configuration_index);
        if (fflush(log)) {
            goto done;
        }
        printf("BIAS_DETECTOR %lu/%lu %s\n", (unsigned long)i + 1,
            (unsigned long)arguments.detector_count, arguments.detectors[i].detector_id);
        fflush(stdout);
        if (!process_bias_detector(arguments.detectors + i, i, frame_count, raw_paths, config,
                &paths, private_work_directory, &options, archive, &error)) {
            goto done;
        }
        assembly[i] = arguments.detectors[i].assembly;
        fprintf(log, "DETECTOR_DONE %s\n", arguments.detectors[i].detector_id);
        if (fflush(log)) {
            goto done;
        }
    }

    /* [BIAS-PRODUCT-PUBLICATION]
     * All selected detector products must be complete before final assembly.
     * Bias adds no cross-detector normalization or balancing here.
     */

    if (mef_bias_product_qc_check(archive, message, sizeof(message))) {
        goto done;
    }
    fprintf(log, "MEF_ASSEMBLY_START\n");
    if (fflush(log)) {
        goto done;
    }
    printf("BIAS_MEF_ASSEMBLY %s\n", paths.fits);
    fflush(stdout);
    if (mef_mef_assemble(paths.fits, arguments.reference_detector_id, assembly,
            arguments.detector_count, message, sizeof(message))) {
        goto done;
    }
    fprintf(log, "NATIVE_ASDF_START\n");
    if (fflush(log)) {
        goto done;
    }
    printf("BIAS_NATIVE_ASDF %s\n", paths.asdf);
    fflush(stdout);
    if (recipe_document) {
        size_t primary_count, detector_count;
        const char *const *primary_keys =
            mef_bias_recipe_primary_keys(recipe_document, &primary_count);
        const char *const *detector_keys =
            mef_bias_recipe_detector_keys(recipe_document, &detector_count);
        if (mef_bias_product_qc_headers(archive, primary_keys, primary_count, detector_keys,
                detector_count, mef_bias_recipe_path(recipe_document),
                mef_bias_recipe_source(recipe_document), message, sizeof(message))) {
            goto done;
        }
    }
    if (mef_bias_product_qc_write(archive, message, sizeof(message))) {
        goto done;
    }
    set_logfile(0);
    for (i = 0; i < arguments.detector_count; ++i) {
        if (unlink(arguments.detectors[i].temporary_path)) {
            fprintf(log, "RETAINED_TEMPORARY %s\n", arguments.detectors[i].temporary_path);
        }
    }
    if (rmdir(private_work_directory)) {
        fprintf(log, "RETAINED_PRIVATE_WORK %s\n", private_work_directory);
    }
    fprintf(log, "OUTPUTS_WRITTEN; final success requires zero command exit\n");
    if (ferror(log)) {
        goto done;
    }
    if (fclose(log)) {
        log = NULL;
        goto done;
    }
    log = NULL;
    printf("BIAS_RECIPE_COMPLETE\nFITS %s\nASDF %s\nLOG %s\n", paths.fits, paths.asdf, paths.log);
    succeeded = 1;
    goto done;
usage:
    fprintf(stderr,
        "Short form: cal bias --config RECIPE.toml --bias ABS_LIST (--output-dir DIR|--output "
        "FITS) [--detectors all|ID,ID]\n");
    fprintf(stderr,
        "Standalone candidate: cal bias (--pafname PAF|--config TOML) --bias ABS_LIST "
        "(--output-dir DIR|--output FITS) --reference-detector ID --mad (yes|no) [--ron-first "
        "INDEX --ron-second INDEX] [--high-sigma K]\n"
        "Repeat detector blocks: --detector-id EXTNAME --config-detector ZERO_BASED --readout-id "
        "ID --bin-x N --bin-y N --amplifier-id ID --input-bpm (omitted|FITS) --hdu N [--hdu N ... "
        "one per input]\n"
        "Selected BPM additionally requires --bpm-hdu N --bpm-good-value (0|1) --bpm-coordinates "
        "(raw|active) [--bpm-expected-extname NAME]. Output parent must exist; no overwrite.\n");
done:

    /* Release in-memory owners; preserve failed file products and private work. */

    set_logfile(0);
    if (!succeeded) {
        if (*message) {
            fprintf(stderr, "%s\n", message);
        }
        if (error) {
            fprintf(stderr, "%s\n", mef_error_message(error));
        }
        if (diagnostic) {
            fprintf(stderr, "%s\n", diagnostic);
        }
        if (log) {
            fprintf(log, "FAILED; retain existing outputs and private work %s\n",
                private_work_directory);
            fclose(log);
            log = NULL;
        }
        if (*private_work_directory) {
            fprintf(stderr, "Retained private work: %s\n", private_work_directory);
        }
        fprintf(stderr, "Bias recipe incomplete; no overall success reported.\n");
    }
    if (log_descriptor >= 0) {
        close(log_descriptor);
    }
    mef_bias_product_qc_destroy(archive);
    mef_error_destroy(error);
    for (i = 0; i < arguments.detector_count; ++i) {
        if (arguments.detectors[i].raw_layouts) {
            for (j = 0; j < frame_count; ++j) {
                mef_layout_map_destroy(arguments.detectors[i].raw_layouts[j]);
            }
        }
        mef_layout_map_destroy(arguments.detectors[i].mask_map);
        free(arguments.detectors[i].raw_layouts);
        free(arguments.detectors[i].hdus);
        free(arguments.detectors[i].bpm_path);
    }
    for (i = 0; i < frame_count; ++i) {
        if (layouts) {
            mef_layout_destroy(layouts[i]);
        }
        if (raw_paths) {
            free(raw_paths[i]);
        }
    }
    free(layouts);
    free(raw_paths);
    free(assembly);
    free(arguments.detectors);
    free(config_path);
    free(listing_path);
    framelist_del(frames);
    mef_config_destroy(config);
    mef_config_document_destroy(document);
    mef_bb_del(legacy);
    mef_bias_recipe_config_destroy(recipe_document);
    return succeeded ? EXIT_SUCCESS : EXIT_FAILURE;
}
