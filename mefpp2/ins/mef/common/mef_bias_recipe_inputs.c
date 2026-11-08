#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias_recipe.h"
#include "mef_bias_qc_fits.h"
#include <errno.h>
#include <limits.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef realloc
#undef free

static int bind_detector_inputs(detector_plan *detector, mef_layout *const *layouts,
    size_t frame_count, const mef_config *config, mef_error **error)
{
    mef_detector_binding binding;
    size_t i;
    int configured;
    const mef_bpm_policy *policy = &mef_config_processing(config)->bpm;
    if (!mef_bias_recipe_parse_nonnegative_int(detector->option_values[CFG], &configured) ||
        !mef_bias_recipe_parse_nonnegative_int(detector->option_values[BINX], &detector->bin_x) ||
        detector->bin_x == 0 ||
        !mef_bias_recipe_parse_nonnegative_int(detector->option_values[BINY], &detector->bin_y) ||
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
        if (!mef_bias_recipe_parse_nonnegative_int(
                detector->option_values[BPM_HDU], &detector->bpm_hdu) ||
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
                    !mef_bias_recipe_parse_nonnegative_int(
                        detector->option_values[GOOD], &legacy_good) ||
                    legacy_good != detector->bpm_good_value) {
                    return 0;
                }
            }
        } else if (!mef_bias_recipe_parse_nonnegative_int(
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

int mef_bias_recipe_admit(mef_bias_recipe *recipe)
{
    size_t i, j;
    int reference_found = 0;
    mef_layout_options layout_options;
    recipe->layouts = calloc(recipe->frame_count, sizeof(*recipe->layouts));
    recipe->raw_paths = calloc(recipe->frame_count, sizeof(*recipe->raw_paths));
    recipe->assembly = calloc(recipe->arguments.detector_count, sizeof(*recipe->assembly));
    if (recipe->layouts == NULL || recipe->raw_paths == NULL || recipe->assembly == NULL) {
        return 0;
    }
    memset(&layout_options, 0, sizeof(layout_options));
    layout_options.max_hdus = 4096;
    layout_options.max_header_bytes = 16 * 1024 * 1024;

    /* Header-only admission of every input/detector precedes output creation. */

    for (i = 0; i < recipe->frame_count; ++i) {
        if (recipe->frames->name[i][0] != '/' ||
            (recipe->raw_paths[i] = realpath(recipe->frames->name[i], NULL)) == NULL) {
            return 0;
        }
        for (j = 0; j < i; ++j) {
            if (!strcmp(recipe->raw_paths[i], recipe->raw_paths[j])) {
                strcpy(recipe->run->message, "Duplicate raw input path");
                return 0;
            }
        }
        if (mef_layout_read(recipe->raw_paths[i], &layout_options, NULL, recipe->layouts + i,
                &recipe->error) != MEF_OK) {
            return 0;
        }
    }
    for (i = 0; i < recipe->arguments.detector_count; ++i) {
        detector_plan *detector = recipe->arguments.detectors + i;
        if (!bind_detector_inputs(
                detector, recipe->layouts, recipe->frame_count, recipe->config, &recipe->error)) {
            strcpy(recipe->run->message, "Invalid explicit detector/BPM binding or geometry");
            return 0;
        }
        if (!strcmp(detector->detector_id, recipe->arguments.reference_detector_id)) {
            reference_found = 1;
        }

        /* Different logical detectors may not reuse one physical input plane. */

        for (j = 0; j < i; ++j) {
            size_t frame;
            for (frame = 0; frame < recipe->frame_count; ++frame) {
                const mef_bound_detector *now =
                    mef_layout_find(detector->raw_layouts[frame], detector->detector_id);
                const mef_bound_detector *old =
                    mef_layout_find(recipe->arguments.detectors[j].raw_layouts[frame],
                        recipe->arguments.detectors[j].detector_id);
                if (now->image.hdu_index == old->image.hdu_index) {
                    strcpy(recipe->run->message, "Selected detector catalogue reuses an input HDU");
                    return 0;
                }
            }
        }
        for (j = 0; j < i; ++j) {
            if (!strcmp(detector->detector_id, recipe->arguments.detectors[j].detector_id) ||
                detector->configuration_index ==
                    recipe->arguments.detectors[j].configuration_index) {
                strcpy(recipe->run->message, "Duplicate detector identity or configuration slot");
                return 0;
            }
        }
    }
    if (!reference_found) {
        strcpy(recipe->run->message, "Reference detector must be in the selected set");
        return 0;
    }
    return 1;
}
