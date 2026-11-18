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

static int detector_settings(toml_datum_t root, const mef_detector_definition *entry,
    mef_flat_detector *channel)
{
    channel->id = entry->id;
    channel->slot = entry->slot;
    channel->amplifier = string(entry->definition, "amplifier");
    if (!channel->amplifier || strlen(channel->id) > 68 || strchr(channel->id, '\''))
        return 0;

    toml_datum_t size = toml_get(entry->definition, "raw_size");
    if (size.type != TOML_ARRAY || size.u.arr.size != 2 ||
        !integer(size.u.arr.elem[0], 2, INT_MAX, &channel->raw_width) ||
        !integer(size.u.arr.elem[1], 2, INT_MAX, &channel->raw_height) ||
        channel->raw_width > INT_MAX / channel->raw_height)
        return 0;

    char chip[32];
    snprintf(chip, sizeof(chip), "CHIP%d", entry->slot + 1);
    toml_datum_t instrument = toml_get(toml_get(root, "native"), "instrument");
    toml_datum_t detector = toml_get(toml_get(instrument, "detectors"), chip);
    const char *const regions[] = {"prescan_x_min", "prescan_x_max", "overscan_x_min",
        "overscan_x_max", "trimreg_x_min", "trimreg_x_max", "trimreg_y_min", "trimreg_y_max"};
    int *const coordinates[] = {channel->ccd.prescan_x, channel->ccd.prescan_x + 1,
        channel->ccd.overscan_x, channel->ccd.overscan_x + 1, channel->ccd.trimreg,
        channel->ccd.trimreg + 1, channel->ccd.trimreg + 2, channel->ccd.trimreg + 3};
    for (int i = 0; i < 8; ++i)
        if (!integer(toml_get(toml_get(detector, regions[i]), "value"), 1,
                i < 6 ? channel->raw_width : channel->raw_height, coordinates[i]))
            return 0;
    double gain, ron;
    if (!number(toml_get(toml_get(detector, "gain"), "value"), &gain) ||
        !number(toml_get(toml_get(detector, "ron"), "value"), &ron) ||
        gain <= 0 || ron < 0 || !isfinite((float)gain) || (float)gain == 0 ||
        !isfinite((float)ron))
        return 0;
    channel->ccd.gain = (float)gain;
    channel->ccd.ron = (float)ron;
    return channel->ccd.prescan_x[0] <= channel->ccd.prescan_x[1] &&
        channel->ccd.overscan_x[0] <= channel->ccd.overscan_x[1] &&
        channel->ccd.trimreg[0] < channel->ccd.trimreg[1] &&
        channel->ccd.trimreg[2] < channel->ccd.trimreg[3];
}

static int stack_settings(mef_flat_detector *channel, toml_datum_t settings, int sky)
{
    mef_bb *stack = &channel->stack;
    int width = channel->ccd.trimreg[1] - channel->ccd.trimreg[0] + 1;
    int height = channel->ccd.trimreg[3] - channel->ccd.trimreg[2] + 1;
    toml_datum_t pre = toml_get(settings, "use_prescan");
    toml_datum_t over = toml_get(settings, "use_overscan");
    int minimum_frames;
    double low, high, clip_low, clip_high;
    if (pre.type != TOML_BOOLEAN || over.type != TOML_BOOLEAN ||
        !integer(toml_get(settings, "reject_scan_low"), 0, channel->raw_width, stack->scanrej) ||
        !integer(toml_get(settings, "reject_scan_high"), 0, channel->raw_width, stack->scanrej + 1) ||
        !integer(toml_get(settings, "minimum_frames"), 3, INT_MAX, &minimum_frames) ||
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
    long long scan_width = stack->use_prescan * (channel->ccd.prescan_x[1] - channel->ccd.prescan_x[0] + 1) +
        stack->use_overscan * (channel->ccd.overscan_x[1] - channel->ccd.overscan_x[0] + 1);
    if ((long long)stack->scanrej[0] + stack->scanrej[1] >= scan_width || scan_width > INT_MAX)
        return 0;

    stack->median_surf = (stack->median_reg[1] - stack->median_reg[0] + 1) *
        (stack->median_reg[3] - stack->median_reg[2] + 1);
    for (int i = 0; i < 4; ++i)
        --stack->median_reg[i];
    if (sky) {
        stack->sky_minframe = minimum_frames;
        stack->sky_framethr_lo = low;
        stack->sky_framethr_hi = high;
    } else {
        stack->dome_minframe = minimum_frames;
        stack->dome_framethr_lo = low;
        stack->dome_framethr_hi = high;
    }
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

static int select_detectors(mef_flat_stack *flat, toml_datum_t settings, const char *selection)
{
    toml_datum_t root = flat->detector.parsed.toptab;
    toml_datum_t binning = toml_get(root, "binning");
    toml_datum_t entries = toml_get(root, "detector");
    int mosaic = !strcmp(selection, "all");
    int reference_found = 0;
    if (!mef_detector_catalogue_valid(root) ||
        binning.type != TOML_ARRAY || binning.u.arr.size != 2 ||
        !integer(binning.u.arr.elem[0], 1, INT_MAX, &flat->bin_x) ||
        !integer(binning.u.arr.elem[1], 1, INT_MAX, &flat->bin_y))
        return 0;
    flat->instrument = string(root, "instrument");
    flat->readout = string(root, "readout_id");
    if (!flat->instrument || !flat->readout)
        return 0;

    flat->detectors = calloc(mosaic ? (size_t)entries.u.arr.size : 1, sizeof(*flat->detectors));
    if (!flat->detectors)
        return 0;
    for (int i = 0; i < entries.u.arr.size; ++i) {
        mef_detector_definition entry;
        if (!mef_detector_catalogue_entry(root, i, &entry))
            return 0;
        if (!entry.enabled || (!mosaic && strcmp(entry.id, selection)))
            continue;
        mef_flat_detector *channel = flat->detectors + flat->detector_count;
        if (!detector_settings(root, &entry, channel) || !stack_settings(channel, settings, flat->sky)) {
            snprintf(flat->run->message, sizeof(flat->run->message),
                "Invalid flat detector or stack settings: %.390s", entry.id);
            return 0;
        }
        if (!mosaic || entry.slot == 0) {
            flat->reference = flat->detector_count;
            reference_found = 1;
        }
        ++flat->detector_count;
    }
    if (!reference_found) {
        snprintf(flat->run->message, sizeof(flat->run->message),
            "Select an enabled detector. A full mosaic requires enabled native slot 1.");
        return 0;
    }
    return 1;
}

static int bind_detector(const mef_flat_stack *flat, mef_flat_detector *channel,
    size_t input, const mef_hdu_layout *planes, size_t count)
{
    int matches = 0;
    mef_flat_exposure *binding = channel->exposures + input;
    for (size_t hdu = 1; hdu < count; ++hdu) {
        const mef_hdu_layout *plane = planes + hdu;
        if (!plane->has_extname || strcmp(plane->extname, channel->id))
            continue;
        ++matches;
        if (plane->kind == MEF_HDU_IMAGE && plane->naxis == 2 &&
            plane->axes[0] == (size_t)channel->raw_width &&
            plane->axes[1] == (size_t)channel->raw_height &&
            (!plane->has_bin_x || plane->bin_x == flat->bin_x) &&
            (!plane->has_bin_y || plane->bin_y == flat->bin_y))
            binding->hdu = plane->hdu_index;
    }
    return matches == 1 && binding->hdu > 0;
}

static int bind_inputs(mef_flat_stack *flat, const char *filter_key)
{
    const char *type = "FLAT,SKY";
    if (!flat->sky)
        type = !strcasecmp(flat->instrument, "wfi") ? "FLAT,SCREEN" : "FLAT,DOME";
    mef_layout_options options = {.max_hdus = 4096,
        .max_header_bytes = MEF_LAYOUT_DEFAULT_HEADER_BYTES,
        .bin_x_key = "HIERARCH ESO DET WIN1 BINX", .bin_y_key = "HIERARCH ESO DET WIN1 BINY"};
    for (size_t i = 0; i < flat->inputs.count; ++i) {
        mef_recipe_input *input = flat->inputs.rows + i;
        mef_flat_input *frame = flat->frames + i;
        snprintf(flat->run->message, sizeof(flat->run->message),
            "Invalid flat input or detector geometry: %.390s", input->path);
        mef_layout *layout = NULL;
        if (strcmp(input->dpr_type, type) ||
            !primary_matches(input->path, "INSTRUME", flat->instrument, 1) ||
            !primary_matches(input->path, filter_key, flat->filter, 0) ||
            !mef_bpm_linearity_hash(input->path, frame->sha256) ||
            mef_layout_read(input->path, &options, NULL, &layout, &flat->error) != MEF_OK) {
            mef_layout_destroy(layout);
            return 0;
        }
        size_t count;
        const mef_hdu_layout *planes = mef_layout_hdus(layout, &count);
        for (size_t d = 0; d < flat->detector_count; ++d) {
            mef_flat_detector *channel = flat->detectors + d;
            if (!bind_detector(flat, channel, i, planes, count)) {
                snprintf(flat->run->message, sizeof(flat->run->message),
                    "Invalid detector %.68s in flat input %.360s", channel->id, input->path);
                mef_layout_destroy(layout);
                return 0;
            }
        }
        mef_layout_destroy(layout);
        snprintf(frame->id, sizeof(frame->id), "exposure-%zu", i + 1);
    }
    return 1;
}

static int bind_master_bias(mef_flat_stack *flat, const char *calibration, const char *name)
{
    mef_layout *layout = NULL;
    mef_detector_binding *bindings = calloc(flat->detector_count, sizeof(*bindings));
    mef_layout_options options = {
        .max_hdus = 4096, .max_header_bytes = MEF_LAYOUT_DEFAULT_HEADER_BYTES,
        .bin_x_key = "HIERARCH ESO DET WIN1 BINX",
        .bin_y_key = "HIERARCH ESO DET WIN1 BINY"
    };
    int okay = 0;

    snprintf(flat->run->message, sizeof(flat->run->message),
        "Master bias must be a compatible active-area CALIB.MASTER_BIAS under project calibration.");
    flat->bias_path = mef_flat_resolve(calibration, name);
    flat->bias_bindings = calloc(flat->detector_count, sizeof(*flat->bias_bindings));
    if (!bindings || !flat->bias_bindings || !flat->bias_path ||
        !mef_flat_below(calibration, flat->bias_path) ||
        !primary_matches(flat->bias_path, "INSTRUME", flat->instrument, 1) ||
        !primary_matches(flat->bias_path, "PRODCATG", "CALIB.MASTER_BIAS", 0) ||
        !mef_bpm_linearity_hash(flat->bias_path, flat->bias_sha256) ||
        mef_layout_read(flat->bias_path, &options, NULL, &layout, &flat->error) != MEF_OK)
        goto done;

    size_t count;
    const mef_hdu_layout *planes = mef_layout_hdus(layout, &count);
    for (size_t d = 0; d < flat->detector_count; ++d) {
        const mef_flat_detector *channel = flat->detectors + d;
        const mef_hdu_layout *plane = NULL;
        int width = channel->ccd.trimreg[1] - channel->ccd.trimreg[0] + 1;
        int height = channel->ccd.trimreg[3] - channel->ccd.trimreg[2] + 1;
        for (size_t hdu = 1; hdu < count; ++hdu) {
            if (planes[hdu].has_extname && !strcmp(planes[hdu].extname, channel->id)) {
                if (plane)
                    goto done;
                plane = planes + hdu;
            }
        }
        if (!plane || plane->kind != MEF_HDU_IMAGE || plane->naxis != 2 ||
            plane->axes[0] != (size_t)width || plane->axes[1] != (size_t)height)
            goto done;
        bindings[d] = (mef_detector_binding){
            .detector_id = channel->id, .extname = channel->id,
            .hdu_index = plane->hdu_index, .unit = "ADU", .readout_id = flat->readout,
            .bin_x = flat->bin_x, .bin_y = flat->bin_y,
            .active_x = 1, .active_y = 1, .active_width = width, .active_height = height,
            .configuration_detector = (size_t)channel->slot,
            .health = MEF_HEALTH_UNKNOWN, .selection = MEF_OUTPUT_SELECTED
        };
        flat->bias_bindings[d] = (mef_qc_calibration_binding){channel->id, plane->hdu_index};
    }
    okay = mef_layout_bind(layout, bindings, flat->detector_count, NULL,
        &flat->bias_mapping, &flat->error) == MEF_OK;
done:
    mef_layout_destroy(layout);
    free(bindings);
    return okay;
}

int mef_flat_stack_admit(mef_flat_stack *flat, const char *path)
{
    const char *const root_keys[] = {flat->sky ? "skyff_recipe_schema_version" :
        "domeff_recipe_schema_version", "project",
        "detector_toml", "run", "inputs", "flat"};
    static const char *const input_keys[] = {"list", "master_bias"};
    static const char *const flat_keys[] = {"filter", "filter_keyword", "detector",
        "use_prescan", "use_overscan", "reject_scan_low", "reject_scan_high", "minimum_frames",
        "frame_mean_low_adu", "frame_mean_high_adu", "clip_low_sigma", "clip_high_sigma",
        "normalization_region"};
    char *project = NULL, *profile = NULL, *raw = NULL, *calibration = NULL;
    int okay = 0, version;
    snprintf(flat->run->message, sizeof(flat->run->message),
        "Invalid flat recipe, project roots or detector/stack settings.");
    char *absolute = realpath(path, NULL);
    flat->recipe = mef_toml_file_read(absolute, 1024 * 1024);
    free(absolute);
    if (!flat->recipe.parsed.ok)
        goto done;
    toml_datum_t root = flat->recipe.parsed.toptab;
    toml_datum_t settings = toml_get(root, "flat"), inputs = toml_get(root, "inputs");
    if (!only_keys(root, root_keys, sizeof(root_keys) / sizeof(*root_keys)) ||
        !only_keys(inputs, input_keys,
            toml_get(inputs, "master_bias").type == TOML_UNKNOWN ? 1 : 2) ||
        !only_keys(settings, flat_keys, sizeof(flat_keys) / sizeof(*flat_keys)) ||
        !integer(toml_get(root, root_keys[0]), 1, 1, &version))
        goto done;
    const char *selection = string(settings, "detector");
    flat->filter = string(settings, "filter");
    const char *filter_key = string(settings, "filter_keyword");
    const char *list = string(inputs, "list"), *run = string(root, "run");
    if (!selection ||
        !flat->filter || !filter_key || !list || list[0] != '/' || !run)
        goto done;
    project = mef_flat_relative_to_file(flat->recipe.path, string(root, "project"));
    profile = mef_flat_relative_to_file(flat->recipe.path, string(root, "detector_toml"));
    if (!project || !profile ||
        !mef_flat_project_paths(flat->run, &flat->recipe, project, run, &flat->project,
            &flat->output, &calibration, &raw))
        goto done;
    flat->detector = mef_toml_file_read(profile, 1024 * 1024);
    if (!flat->detector.parsed.ok || !select_detectors(flat, settings, selection) ||
        !mef_bpm_linearity_hash(list, flat->list_sha256) ||
        !mef_recipe_inputs_read(list, raw, 0, &flat->inputs, flat->run->message,
            sizeof(flat->run->message)) ||
        flat->inputs.count < (size_t)(flat->sky ? flat->detectors[0].stack.sky_minframe :
            flat->detectors[0].stack.dome_minframe))
        goto done;
    flat->list_path = list;
    flat->frames = calloc(flat->inputs.count, sizeof(*flat->frames));
    flat->assembly = calloc(flat->detector_count, sizeof(*flat->assembly));
    if (!flat->frames || !flat->assembly)
        goto done;
    for (size_t d = 0; d < flat->detector_count; ++d) {
        mef_flat_detector *channel = flat->detectors + d;
        channel->exposures = calloc(flat->inputs.count, sizeof(*channel->exposures));
        if (!channel->exposures)
            goto done;
    }
    if (!bind_inputs(flat, filter_key))
        goto done;
    if (toml_get(inputs, "master_bias").type != TOML_UNKNOWN &&
        !bind_master_bias(flat, calibration, string(inputs, "master_bias")))
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
    for (size_t d = 0; d < flat->detector_count; ++d)
        free(flat->detectors[d].exposures);
    free(flat->detectors);
    free(flat->assembly);
    free(flat->frames);
    mef_layout_map_destroy(flat->bias_mapping);
    free(flat->bias_bindings);
    free(flat->bias_path);
    mef_error_destroy(flat->error);
    mef_recipe_inputs_destroy(&flat->inputs);
    mef_toml_file_destroy(&flat->recipe);
    mef_toml_file_destroy(&flat->project);
    mef_toml_file_destroy(&flat->detector);
    free(flat->output);
}
