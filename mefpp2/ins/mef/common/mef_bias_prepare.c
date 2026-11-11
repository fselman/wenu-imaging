#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias.h"
#include "mef_bias_qc_fits.h"
#include "mef_recipe_inputs.h"
#include "mef_project.h"
#include <errno.h>
#include <limits.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef realloc
#undef free

int mef_bias_parse_nonnegative_int(const char *text, int *parsed_value)
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
        if (!strcmp(key, "--bias") || !strcmp(key, "--input")) {
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
        if (!strcmp(key, "--qc")) {
            if (!set_option_once(&arguments->qc_option, option_value) ||
                (strcmp(option_value, "legacy") && strcmp(option_value, "full"))) {
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
            if (!mef_bias_parse_nonnegative_int(option_value, &frame_count)) {
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
        (arguments->mad_option != NULL && strcmp(arguments->mad_option, "yes") &&
            strcmp(arguments->mad_option, "no")) ||
        !arguments->detector_count ||
        (arguments->ron_first_option == NULL) != (arguments->ron_second_option == NULL)) {
        return 0;
    }
    if (arguments->mad_option == NULL) {
        arguments->mad_option = "no";
    }
    return 1;
}

void mef_bias_initialize(mef_bias *recipe, mef_recipe_run *run)
{
    memset(recipe, 0, sizeof(*recipe));
    recipe->run = run;
}

/* Project roots govern processing observations and immutable calibrations. */
static int prepare_project_inputs(mef_bias *recipe)
{
    if (mef_bias_project(recipe->recipe_document)) {
        char project_name[4096], raw_name[4096], output_name[4096];
        const char *source = mef_bias_path(recipe->recipe_document);
        const char *reference = mef_bias_project(recipe->recipe_document);
        const char *slash = strrchr(source, '/');
        if (snprintf(project_name, sizeof(project_name), "%.*s%s%s",
                reference[0] == '/' ? 0 : (int)(slash - source), source,
                reference[0] == '/' ? "" : "/", reference) >= (int)sizeof(project_name)) {
            return 0;
        }
        toml_result_t project = {0};
        char *origin = NULL;
        if (!mef_project_read(project_name, &project, &origin, NULL, NULL)) {
            return 0;
        }
        *strrchr(origin, '/') = 0;
        toml_datum_t roots = toml_get(toml_get(project.toptab, "project"), "roots");
        toml_datum_t raw = toml_get(roots, "raw"), output = toml_get(roots, "output"),
                     calibration = toml_get(roots, "calibration");
        const char *run = mef_bias_run(recipe->recipe_document);
        int okay = raw.type == TOML_STRING && output.type == TOML_STRING &&
                   calibration.type == TOML_STRING && run && run[0] != '/' && !strstr(run, "..");
        if (okay) {
            snprintf(raw_name, sizeof(raw_name), "%s%s%s", raw.u.s[0] == '/' ? "" : origin,
                raw.u.s[0] == '/' ? "" : "/", raw.u.s);
            snprintf(output_name, sizeof(output_name), "%s%s%s/%s",
                output.u.s[0] == '/' ? "" : origin, output.u.s[0] == '/' ? "" : "/", output.u.s,
                run);
            recipe->project_raw = realpath(raw_name, NULL);
            recipe->project_output = realpath(output_name, NULL);
            char calibration_name[4096], invocation[4096],
                *canonical = realpath(project_name, NULL);
            snprintf(calibration_name, sizeof(calibration_name), "%s%s%s",
                calibration.u.s[0] == '/' ? "" : origin, calibration.u.s[0] == '/' ? "" : "/",
                calibration.u.s);
            recipe->project_calibration = realpath(calibration_name, NULL);
            char reduced_name[4096];
            snprintf(reduced_name, sizeof(reduced_name), "%s%s%s",
                output.u.s[0] == '/' ? "" : origin, output.u.s[0] == '/' ? "" : "/", output.u.s);
            char *reduced = realpath(reduced_name, NULL);
            okay = recipe->project_raw && recipe->project_output && recipe->project_calibration &&
                   reduced && canonical && getcwd(invocation, sizeof(invocation));
            if (okay) {
                *strrchr(canonical, '/') = 0;
                okay = !strcmp(invocation, canonical) &&
                       !strncmp(source, canonical, strlen(canonical)) &&
                       source[strlen(canonical)] == '/' &&
                       !strncmp(recipe->listing_path, canonical, strlen(canonical)) &&
                       recipe->listing_path[strlen(canonical)] == '/';
            }
            if (okay) {
                size_t n = strlen(reduced);
                okay = !strncmp(recipe->project_output, reduced, n) &&
                       recipe->project_output[n] == '/' &&
                       !strncmp(recipe->project_calibration, reduced, n) &&
                       recipe->project_calibration[n] == '/' &&
                       strncmp(recipe->project_raw, reduced, n) != 0;
                if (recipe->arguments.output_directory) {
                    char *explicit_output = realpath(recipe->arguments.output_directory, NULL);
                    okay =
                        okay && explicit_output && !strcmp(explicit_output, recipe->project_output);
                    free(explicit_output);
                }
                if (recipe->arguments.output_path) {
                    okay = 0;
                }
            }
            free(reduced);
            free(canonical);
            if (okay) {
                for (size_t i = 0; i < recipe->arguments.detector_count; ++i) {
                    detector_plan *detector = recipe->arguments.detectors + i;
                    const char *mask = detector->option_values[BPM];
                    if (mask && strcmp(mask, "omitted")) {
                        snprintf(calibration_name, sizeof(calibration_name), "%s%s%s",
                            mask[0] == '/' ? "" : recipe->project_calibration,
                            mask[0] == '/' ? "" : "/", mask);
                        detector->dependency_path = realpath(calibration_name, NULL);
                        if (!detector->dependency_path ||
                            strncmp(detector->dependency_path, recipe->project_calibration,
                                strlen(recipe->project_calibration)) ||
                            detector->dependency_path[strlen(recipe->project_calibration)] != '/') {
                            okay = 0;
                            break;
                        }
                        detector->option_values[BPM] = detector->dependency_path;
                    }
                }
            }
        }
        toml_free(project);
        free(origin);
        if (!okay) {
            return 0;
        }
        if (!recipe->arguments.output_directory && !recipe->arguments.output_path) {
            recipe->arguments.output_directory = recipe->project_output;
        }
    }
    return 1;
}

int mef_bias_prepare(mef_bias *recipe, int argc, char **argv)
{
    int expanded_argc = argc, first, second;
    char **expanded_argv = argv, *end;
    mef_status status;
    if (!mef_bias_expand(argc, argv, &expanded_argc, &expanded_argv, &recipe->recipe_document,
            recipe->run->message, sizeof(recipe->run->message))) {
        return 0;
    }
    if (!parse_recipe_arguments(expanded_argc, expanded_argv, &recipe->arguments)) {
        recipe->show_usage = 1;
        return 0;
    }
    recipe->options.legacy_qc =
        recipe->arguments.qc_option && !strcmp(recipe->arguments.qc_option, "legacy");
    recipe->options.with_mad = !strcmp(recipe->arguments.mad_option, "yes");
    recipe->options.high_sigma = 5;
    if (recipe->arguments.high_sigma_option) {
        errno = 0;
        recipe->options.high_sigma = strtod(recipe->arguments.high_sigma_option, &end);
        if (errno || end == recipe->arguments.high_sigma_option || *end ||
            !isfinite(recipe->options.high_sigma) || recipe->options.high_sigma <= 0) {
            recipe->show_usage = 1;
            return 0;
        }
    }
    if (recipe->arguments.ron_first_option) {
        if (!mef_bias_parse_nonnegative_int(recipe->arguments.ron_first_option, &first) ||
            !mef_bias_parse_nonnegative_int(recipe->arguments.ron_second_option, &second) ||
            first == second) {
            recipe->show_usage = 1;
            return 0;
        }
        recipe->options.ron_pair_set = 1;
        recipe->options.ron_first = (size_t)first;
        recipe->options.ron_second = (size_t)second;
    }
    recipe->config_path = realpath(
        recipe->arguments.paf_path ? recipe->arguments.paf_path : recipe->arguments.toml_path,
        NULL);
    recipe->listing_path = realpath(recipe->arguments.bias_list_path, NULL);
    if (recipe->config_path == NULL || recipe->listing_path == NULL) {
        strcpy(recipe->run->message, "Missing explicit configuration or bias list");
        return 0;
    }
    for (int i = 3; i + 1 < expanded_argc; i += 2) {
        if (!strcmp(expanded_argv[i], "--input")) {
            recipe->classified_input = 1;
        }
    }
    if (!prepare_project_inputs(recipe)) {
        return 0;
    }
    if (!mef_recipe_run_paths(recipe->run, recipe->arguments.output_directory,
            recipe->arguments.output_path, "CMDP")) {
        return 0;
    }
    eclipse_init();
    set_logfile(0);
    if (recipe->arguments.paf_path) {
        recipe->legacy = mef_bb_new_from_paf(recipe->config_path);
        if (recipe->legacy == NULL) {
            return 0;
        }
        status = mef_config_from_legacy(recipe->legacy, NULL, &recipe->config, &recipe->diagnostic);
    } else {
        mef_config_toml_initialize();
        status = mef_config_document_from_toml(recipe->config_path, NULL, &recipe->document,
            recipe->run->message, sizeof(recipe->run->message));
        if (status == MEF_OK) {
            status = mef_config_clone(mef_config_document_settings(recipe->document), NULL,
                &recipe->config, &recipe->diagnostic);
        }
    }
    if (status != MEF_OK) {
        return 0;
    }
    {
        const mef_processing_policy *policy = mef_config_processing(recipe->config);
        const char *requested = mef_bias_median_even_handling(recipe->recipe_document);
        if (requested) {
            mef_processing_policy effective = *policy;
            int mode = !strcmp(requested, "lower") ? MEDIAN_EVEN_LOWER : MEDIAN_EVEN_AVERAGE;
            if (policy->median_even_supplied && policy->median_even_handling != mode) {
                strcpy(recipe->run->message, "Conflicting explicit median_even_handling settings");
                return 0;
            }
            effective.median_even_supplied = 1;
            effective.median_even_handling = mode;
            mef_config_initialize_processing(recipe->config, &effective);
        }

        recipe->options.ron_clip_enabled = policy->ron_clip_enabled;
        recipe->options.ron_clip.sigma_low = policy->ron_clip_low;
        recipe->options.ron_clip.sigma_high = policy->ron_clip_high;
        recipe->options.ron_clip.max_iterations = policy->ron_clip_max_iterations;
        if (!recipe->options.legacy_qc && recipe->options.ron_clip_enabled &&
            !recipe->options.ron_pair_set) {
            strcpy(recipe->run->message, "Clipped RON requires an explicit raw pair");
            return 0;
        }
    }
    if (recipe->options.legacy_qc) {
        recipe->options.with_mad = 0;
        recipe->options.ron_pair_set = 0;
        recipe->options.ron_clip_enabled = 0;
    }
    mef_bb_del(recipe->legacy);
    recipe->legacy = NULL;
    mef_recipe_inputs inputs = {0};
    char current[4096];
    const char *raw = recipe->project_raw ? recipe->project_raw : getcwd(current, sizeof(current));
    if (!raw || !mef_recipe_inputs_read(recipe->listing_path, raw, !recipe->classified_input,
                    &inputs, recipe->run->message, sizeof(recipe->run->message))) {
        return 0;
    }
    recipe->frames = framelist_new((int)inputs.count);
    if (recipe->frames) {
        for (size_t i = 0; i < inputs.count; ++i) {
            if (strcmp(inputs.rows[i].dpr_type, "BIAS")) {
                strcpy(recipe->run->message, "Bias processing list accepts DPR.TYPE BIAS only");
                mef_recipe_inputs_destroy(&inputs);
                return 0;
            }
            if (recipe->project_raw &&
                (strncmp(inputs.rows[i].path, recipe->project_raw, strlen(recipe->project_raw)) ||
                    inputs.rows[i].path[strlen(recipe->project_raw)] != '/')) {
                strcpy(recipe->run->message, "Processing input escapes project raw root");
                mef_recipe_inputs_destroy(&inputs);
                return 0;
            }
            recipe->frames->name[i] = strdup(inputs.rows[i].path);
            recipe->frames->type[i] = strdup(inputs.rows[i].dpr_type);
        }
    }
    mef_recipe_inputs_destroy(&inputs);
    if (recipe->frames == NULL || recipe->frames->n < 3 || recipe->frames->n > 100000) {
        strcpy(recipe->run->message, "Require an explicit list of at least three bias inputs");
        return 0;
    }
    recipe->frame_count = (size_t)recipe->frames->n;
    if (recipe->options.ron_pair_set && (recipe->options.ron_first >= recipe->frame_count ||
                                            recipe->options.ron_second >= recipe->frame_count)) {
        recipe->show_usage = 1;
        return 0;
    }
    return 1;
}

void mef_bias_usage(void)
{
    fprintf(stderr,
        "Short form: cal bias --config RECIPE.toml --bias ABS_LIST (--output-dir DIR|--output "
        "FITS) [--detectors all|ID,ID] [--qc legacy|full]\n");
    fprintf(stderr,
        "Standalone candidate: cal bias [--qc legacy|full] (--pafname PAF|--config TOML) --bias "
        "ABS_LIST "
        "(--output-dir DIR|--output FITS) --reference-detector ID [--mad (yes|no)] [--ron-first "
        "INDEX --ron-second INDEX] [--high-sigma K]\n"
        "Repeat detector blocks: --detector-id EXTNAME --config-detector ZERO_BASED --readout-id "
        "ID --bin-x N --bin-y N --amplifier-id ID --input-bpm (omitted|FITS) --hdu N [--hdu N ... "
        "one per input]\n"
        "Selected BPM additionally requires --bpm-hdu N --bpm-good-value (0|1) --bpm-coordinates "
        "(raw|active) [--bpm-expected-extname NAME]. MAD defaults to no. "
        "Output parent must exist; no overwrite.\n");
}

void mef_bias_destroy(mef_bias *recipe)
{
    size_t i, j;
    mef_bias_product_qc_destroy(recipe->archive);
    mef_error_destroy(recipe->error);
    for (i = 0; i < recipe->arguments.detector_count; ++i) {
        if (recipe->arguments.detectors[i].raw_layouts) {
            for (j = 0; j < recipe->frame_count; ++j) {
                mef_layout_map_destroy(recipe->arguments.detectors[i].raw_layouts[j]);
            }
        }
        mef_layout_map_destroy(recipe->arguments.detectors[i].mask_map);
        free(recipe->arguments.detectors[i].raw_layouts);
        free(recipe->arguments.detectors[i].hdus);
        free(recipe->arguments.detectors[i].bpm_path);
        free(recipe->arguments.detectors[i].dependency_path);
    }
    for (i = 0; i < recipe->frame_count; ++i) {
        if (recipe->layouts) {
            mef_layout_destroy(recipe->layouts[i]);
        }
        if (recipe->raw_paths) {
            free(recipe->raw_paths[i]);
        }
    }
    free(recipe->layouts);
    free(recipe->raw_paths);
    free(recipe->assembly);
    free(recipe->arguments.detectors);
    free(recipe->config_path);
    free(recipe->listing_path);
    framelist_del(recipe->frames);
    mef_config_destroy(recipe->config);
    mef_config_document_destroy(recipe->document);
    mef_bb_del(recipe->legacy);
    mef_bias_config_destroy(recipe->recipe_document);
    free(recipe->project_raw);
    free(recipe->project_output);
    free(recipe->project_calibration);
}
