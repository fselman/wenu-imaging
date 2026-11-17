#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_flat_stack.h"
#include "mef_bpm_linearity.h"
#include "mef_detector_catalogue.h"
#include "mef_layout.h"
#include <limits.h>
#include <math.h>
#include <strings.h>
#undef calloc
#undef free

static const char *string(toml_datum_t table, const char *key)
{
    toml_datum_t value = toml_get(table, key);
    return value.type == TOML_STRING && value.u.str.len > 0 &&
        strlen(value.u.s) == (size_t)value.u.str.len ? value.u.s : NULL;
}

static int integer(toml_datum_t value, int low, int high, int *result)
{
    if (value.type != TOML_INT64 || value.u.int64 < low || value.u.int64 > high)
        return 0;
    *result = (int)value.u.int64;
    return 1;
}

static int number(toml_datum_t value, double *result)
{
    if (value.type == TOML_INT64)
        *result = (double)value.u.int64;
    else if (value.type == TOML_FP64)
        *result = value.u.fp64;
    else
        return 0;
    return isfinite(*result);
}

static int only_keys(toml_datum_t table, const char *const *keys, size_t count)
{
    if (table.type != TOML_TABLE || (size_t)table.u.tab.size != count)
        return 0;
    for (size_t i = 0; i < count; ++i)
        if (toml_get(table, keys[i]).type == TOML_UNKNOWN)
            return 0;
    return 1;
}

static int rectangle(toml_datum_t value, int width, int height, int out[4])
{
    if (value.type != TOML_ARRAY || value.u.arr.size != 4)
        return 0;
    for (int i = 0; i < 4; ++i)
        if (!integer(value.u.arr.elem[i], 1, i < 2 ? width : height, out + i))
            return 0;
    return out[0] <= out[1] && out[2] <= out[3];
}

static int detector_settings(mef_flat_stack *flat)
{
    toml_datum_t root = flat->detector.parsed.toptab;
    toml_datum_t binning = toml_get(root, "binning");
    mef_detector_definition entry;
    if (!mef_detector_catalogue_valid(root) ||
        !mef_detector_catalogue_find(root, flat->id, &entry) || !entry.enabled ||
        binning.type != TOML_ARRAY || binning.u.arr.size != 2 ||
        !integer(binning.u.arr.elem[0], 1, INT_MAX, &flat->bin_x) ||
        !integer(binning.u.arr.elem[1], 1, INT_MAX, &flat->bin_y))
        return 0;
    flat->slot = entry.slot;
    flat->instrument = string(root, "instrument");
    flat->readout = string(root, "readout_id");
    flat->amplifier = string(entry.definition, "amplifier");

    toml_datum_t size = toml_get(entry.definition, "raw_size");
    if (!flat->instrument || !flat->readout || !flat->amplifier ||
        size.type != TOML_ARRAY || size.u.arr.size != 2 ||
        !integer(size.u.arr.elem[0], 2, INT_MAX, &flat->raw_width) ||
        !integer(size.u.arr.elem[1], 2, INT_MAX, &flat->raw_height) ||
        flat->raw_width > INT_MAX / flat->raw_height)
        return 0;

    char chip[32];
    snprintf(chip, sizeof(chip), "CHIP%d", entry.slot + 1);
    toml_datum_t instrument = toml_get(toml_get(root, "native"), "instrument");
    toml_datum_t detector = toml_get(toml_get(instrument, "detectors"), chip);
    const char *const regions[] = {"prescan_x_min", "prescan_x_max", "overscan_x_min",
        "overscan_x_max", "trimreg_x_min", "trimreg_x_max", "trimreg_y_min", "trimreg_y_max"};
    int *const coordinates[] = {flat->ccd.prescan_x, flat->ccd.prescan_x + 1,
        flat->ccd.overscan_x, flat->ccd.overscan_x + 1, flat->ccd.trimreg,
        flat->ccd.trimreg + 1, flat->ccd.trimreg + 2, flat->ccd.trimreg + 3};
    for (int i = 0; i < 8; ++i)
        if (!integer(toml_get(toml_get(detector, regions[i]), "value"), 1,
                i < 6 ? flat->raw_width : flat->raw_height, coordinates[i]))
            return 0;
    double gain, ron;
    if (!number(toml_get(toml_get(detector, "gain"), "value"), &gain) ||
        !number(toml_get(toml_get(detector, "ron"), "value"), &ron) ||
        gain <= 0 || ron < 0 || !isfinite((float)gain) || (float)gain == 0 ||
        !isfinite((float)ron))
        return 0;
    flat->ccd.gain = (float)gain;
    flat->ccd.ron = (float)ron;
    return flat->ccd.prescan_x[0] <= flat->ccd.prescan_x[1] &&
        flat->ccd.overscan_x[0] <= flat->ccd.overscan_x[1] &&
        flat->ccd.trimreg[0] < flat->ccd.trimreg[1] &&
        flat->ccd.trimreg[2] < flat->ccd.trimreg[3];
}

static int stack_settings(mef_flat_stack *flat, toml_datum_t settings)
{
    mef_bb *stack = &flat->stack;
    int width = flat->ccd.trimreg[1] - flat->ccd.trimreg[0] + 1;
    int height = flat->ccd.trimreg[3] - flat->ccd.trimreg[2] + 1;
    toml_datum_t pre = toml_get(settings, "use_prescan");
    toml_datum_t over = toml_get(settings, "use_overscan");
    double low, high, clip_low, clip_high;
    if (pre.type != TOML_BOOLEAN || over.type != TOML_BOOLEAN ||
        !integer(toml_get(settings, "reject_scan_low"), 0, flat->raw_width, stack->scanrej) ||
        !integer(toml_get(settings, "reject_scan_high"), 0, flat->raw_width, stack->scanrej + 1) ||
        !integer(toml_get(settings, "minimum_frames"), 3, INT_MAX, &stack->dome_minframe) ||
        !number(toml_get(settings, "frame_mean_low_adu"), &low) ||
        !number(toml_get(settings, "frame_mean_high_adu"), &high) ||
        !number(toml_get(settings, "clip_low_sigma"), &clip_low) ||
        !number(toml_get(settings, "clip_high_sigma"), &clip_high) ||
        low < 0 || !(low < high) || clip_low <= 0 || clip_high <= 0 ||
        !isfinite((float)high) || !isfinite((float)clip_low) || !isfinite((float)clip_high) ||
        (float)low >= (float)high || (float)clip_low <= 0 || (float)clip_high <= 0 ||
        !rectangle(toml_get(settings, "normalization_region"), width, height, stack->median_reg))
        return 0;
    stack->use_prescan = pre.u.boolean;
    stack->use_overscan = over.u.boolean;
    long long scan_width = stack->use_prescan * (flat->ccd.prescan_x[1] - flat->ccd.prescan_x[0] + 1) +
        stack->use_overscan * (flat->ccd.overscan_x[1] - flat->ccd.overscan_x[0] + 1);
    if ((long long)stack->scanrej[0] + stack->scanrej[1] >= scan_width || scan_width > INT_MAX)
        return 0;

    stack->median_surf = (stack->median_reg[1] - stack->median_reg[0] + 1) *
        (stack->median_reg[3] - stack->median_reg[2] + 1);
    for (int i = 0; i < 4; ++i)
        --stack->median_reg[i];
    stack->dome_framethr_lo = low;
    stack->dome_framethr_hi = high;
    stack->pixrej_lo = clip_low;
    stack->pixrej_hi = clip_high;
    return 1;
}

static int primary_matches(char *path, const char *keyword, const char *expected, int fold)
{
    char *card = qfits_query_ext(path, keyword, 0);
    if (!card)
        return 0;
    const char *value = qfits_pretty_string(card);
    return fold ? !strcasecmp(value, expected) : !strcmp(value, expected);
}

static int bind_inputs(mef_flat_stack *flat, const char *filter_key)
{
    const char *type = !strcasecmp(flat->instrument, "wfi") ? "FLAT,SCREEN" : "FLAT,DOME";
    mef_layout_options options = {.max_hdus = 4096,
        .max_header_bytes = MEF_LAYOUT_DEFAULT_HEADER_BYTES,
        .bin_x_key = "HIERARCH ESO DET WIN1 BINX", .bin_y_key = "HIERARCH ESO DET WIN1 BINY"};
    for (size_t i = 0; i < flat->inputs.count; ++i) {
        mef_recipe_input *input = flat->inputs.rows + i;
        mef_flat_exposure *exposure = flat->exposures + i;
        snprintf(flat->run->message, sizeof(flat->run->message),
            "Invalid dome input or detector geometry: %.390s", input->path);
        mef_layout *layout = NULL;
        if (strcmp(input->dpr_type, type) ||
            !primary_matches(input->path, "INSTRUME", flat->instrument, 1) ||
            !primary_matches(input->path, filter_key, flat->filter, 0) ||
            !mef_bpm_linearity_hash(input->path, exposure->sha256) ||
            mef_layout_read(input->path, &options, NULL, &layout, &flat->error) != MEF_OK) {
            mef_layout_destroy(layout);
            return 0;
        }
        size_t count;
        const mef_hdu_layout *planes = mef_layout_hdus(layout, &count);
        int matches = 0;
        for (size_t hdu = 1; hdu < count; ++hdu) {
            const mef_hdu_layout *plane = planes + hdu;
            if (!plane->has_extname || strcmp(plane->extname, flat->id))
                continue;
            ++matches;
            if (plane->kind == MEF_HDU_IMAGE && plane->naxis == 2 &&
                plane->axes[0] == (size_t)flat->raw_width &&
                plane->axes[1] == (size_t)flat->raw_height &&
                (!plane->has_bin_x || plane->bin_x == flat->bin_x) &&
                (!plane->has_bin_y || plane->bin_y == flat->bin_y))
                exposure->hdu = plane->hdu_index;
        }
        mef_layout_destroy(layout);
        if (matches != 1 || exposure->hdu <= 0)
            return 0;
        snprintf(exposure->id, sizeof(exposure->id), "exposure-%zu", i + 1);
    }
    return 1;
}

int mef_flat_stack_admit(mef_flat_stack *flat, const char *path)
{
    static const char *const root_keys[] = {"domeff_recipe_schema_version", "project",
        "detector_toml", "run", "inputs", "flat"};
    static const char *const input_keys[] = {"list"};
    static const char *const flat_keys[] = {"filter", "filter_keyword", "detector",
        "use_prescan", "use_overscan", "reject_scan_low", "reject_scan_high", "minimum_frames",
        "frame_mean_low_adu", "frame_mean_high_adu", "clip_low_sigma", "clip_high_sigma",
        "normalization_region"};
    char *project = NULL, *profile = NULL, *raw = NULL, *calibration = NULL;
    int okay = 0, version;
    snprintf(flat->run->message, sizeof(flat->run->message),
        "Invalid dome recipe, project roots or detector/stack settings.");
    char *absolute = realpath(path, NULL);
    flat->recipe = mef_toml_file_read(absolute, 1024 * 1024);
    free(absolute);
    if (!flat->recipe.parsed.ok)
        goto done;
    toml_datum_t root = flat->recipe.parsed.toptab;
    toml_datum_t settings = toml_get(root, "flat"), inputs = toml_get(root, "inputs");
    if (!only_keys(root, root_keys, sizeof(root_keys) / sizeof(*root_keys)) ||
        !only_keys(inputs, input_keys, sizeof(input_keys) / sizeof(*input_keys)) ||
        !only_keys(settings, flat_keys, sizeof(flat_keys) / sizeof(*flat_keys)) ||
        !integer(toml_get(root, root_keys[0]), 1, 1, &version))
        goto done;
    flat->id = string(settings, "detector");
    flat->filter = string(settings, "filter");
    const char *filter_key = string(settings, "filter_keyword");
    const char *list = string(inputs, "list"), *run = string(root, "run");
    if (!flat->id || strlen(flat->id) > 68 || strchr(flat->id, '\'') ||
        !flat->filter || !filter_key || !list || list[0] != '/' || !run)
        goto done;
    project = mef_flat_relative_to_file(flat->recipe.path, string(root, "project"));
    profile = mef_flat_relative_to_file(flat->recipe.path, string(root, "detector_toml"));
    if (!project || !profile ||
        !mef_flat_project_paths(flat->run, &flat->recipe, project, run, &flat->project,
            &flat->output, &calibration, &raw))
        goto done;
    flat->detector = mef_toml_file_read(profile, 1024 * 1024);
    if (!flat->detector.parsed.ok || !detector_settings(flat) || !stack_settings(flat, settings) ||
        !mef_bpm_linearity_hash(list, flat->list_sha256) ||
        !mef_recipe_inputs_read(list, raw, 0, &flat->inputs, flat->run->message,
            sizeof(flat->run->message)) ||
        flat->inputs.count < (size_t)flat->stack.dome_minframe)
        goto done;
    flat->list_path = list;
    flat->exposures = calloc(flat->inputs.count, sizeof(*flat->exposures));
    if (!flat->exposures || !bind_inputs(flat, filter_key))
        goto done;
    flat->run->message[0] = '\0';
    okay = 1;
done:
    free(project);
    free(profile);
    free(calibration);
    free(raw);
    return okay;
}

void mef_flat_stack_destroy(mef_flat_stack *flat)
{
    if (flat->image)
        image_del(flat->image);
    mef_error_destroy(flat->error);
    mef_recipe_inputs_destroy(&flat->inputs);
    mef_toml_file_destroy(&flat->recipe);
    mef_toml_file_destroy(&flat->project);
    mef_toml_file_destroy(&flat->detector);
    free(flat->exposures);
    free(flat->output);
}
