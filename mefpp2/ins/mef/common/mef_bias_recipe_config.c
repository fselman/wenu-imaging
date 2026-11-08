/* Expand the small bias-recipe TOML envelope into the existing native arguments.
 * The envelope selects shared settings, detectors and optional QC/provenance.
 * The returned owner keeps expanded strings alive until recipe teardown;
 * this layer performs no image correction or scientific measurement.
 */

#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias_recipe_config.h"
#include "tomlc17.h"
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

struct mef_bias_recipe_config {
    toml_result_t parsed;
    char *path, *source, **argv;
    int argc, capacity;
    const char *primary[16], *detector[16];
    size_t primary_count, detector_count;
    const char *median_even_handling;
};

static int report_recipe_error(char *message, size_t count, const char *text)
{
    if (message && count) {
        snprintf(message, count, "%s", text);
    }
    return 0;
}

void mef_bias_recipe_config_destroy(mef_bias_recipe_config *recipe)
{
    if (!recipe) {
        return;
    }
    for (int i = 0; i < recipe->argc; ++i) {
        free(recipe->argv[i]);
    }
    free(recipe->argv);
    toml_free(recipe->parsed);
    free(recipe->source);
    free(recipe->path);
    free(recipe);
}

const char *mef_bias_recipe_source(const mef_bias_recipe_config *recipe)
{
    return recipe ? recipe->source : NULL;
}

const char *mef_bias_recipe_path(const mef_bias_recipe_config *recipe)
{
    return recipe ? recipe->path : NULL;
}

const char *const *mef_bias_recipe_primary_keys(const mef_bias_recipe_config *recipe, size_t *count)
{
    *count = recipe ? recipe->primary_count : 0;
    return recipe ? recipe->primary : NULL;
}

const char *const *mef_bias_recipe_detector_keys(
    const mef_bias_recipe_config *recipe, size_t *count)
{
    *count = recipe ? recipe->detector_count : 0;
    return recipe ? recipe->detector : NULL;
}

static const char *toml_string_value(toml_datum_t value)
{
    return value.type == TOML_STRING && value.u.str.len > 0 &&
                   strlen(value.u.s) == (size_t)value.u.str.len
               ? value.u.s
               : NULL;
}

static int table_has_only_keys(toml_datum_t t, const char *const *names, size_t count)
{
    if (t.type != TOML_TABLE) {
        return 0;
    }
    for (int i = 0; i < t.u.tab.size; ++i) {
        size_t j;
        if (strlen(t.u.tab.key[i]) != (size_t)t.u.tab.len[i]) {
            return 0;
        }
        for (j = 0; j < count; ++j) {
            if (!strcmp(t.u.tab.key[i], names[j])) {
                break;
            }
        }
        if (j == count) {
            return 0;
        }
    }
    return 1;
}

#define TABLE(t, names) table_has_only_keys(t, names, sizeof(names) / sizeof(*(names)))

static int append_argument(mef_bias_recipe_config *recipe, const char *text)
{
    if (recipe->argc >= 1000000 || !text || !*text) {
        return 0;
    }
    if (recipe->argc + 1 >= recipe->capacity) {
        int capacity = recipe->capacity ? recipe->capacity * 2 : 64;
        char **a = realloc(recipe->argv, (size_t)capacity * sizeof(*a));
        if (!a) {
            return 0;
        }
        recipe->argv = a;
        recipe->capacity = capacity;
    }
    recipe->argv[recipe->argc] = strdup(text);
    if (!recipe->argv[recipe->argc]) {
        return 0;
    }
    recipe->argv[++recipe->argc] = NULL;
    return 1;
}

static int append_option_value(mef_bias_recipe_config *recipe, const char *key, const char *value)
{
    return append_argument(recipe, key) && append_argument(recipe, value);
}

static int toml_nonnegative_integer(toml_datum_t value, int *count)
{
    if (value.type != TOML_INT64 || value.u.int64 < 0 || value.u.int64 > INT_MAX) {
        return 0;
    }
    *count = (int)value.u.int64;
    return 1;
}

static int append_integer_option(
    mef_bias_recipe_config *recipe, const char *key, toml_datum_t value)
{
    char text[32];
    int count;
    if (!toml_nonnegative_integer(value, &count)) {
        return 0;
    }
    snprintf(text, sizeof(text), "%d", count);
    return append_option_value(recipe, key, text);
}

static char *resolve_recipe_path(const mef_bias_recipe_config *recipe, const char *text)
{
    char *name, *resolved;
    size_t length;
    if (!text) {
        return NULL;
    }
    if (text[0] == '/') {
        return realpath(text, NULL);
    }
    length = (size_t)(strrchr(recipe->path, '/') - recipe->path) + 1;
    name = malloc(length + strlen(text) + 1);
    if (!name) {
        return NULL;
    }
    memcpy(name, recipe->path, length);
    strcpy(name + length, text);
    resolved = realpath(name, NULL);
    free(name);
    return resolved;
}

static toml_datum_t inherited_option(toml_datum_t entry, toml_datum_t bias, const char *key)
{
    toml_datum_t value = toml_get(entry, key);
    return value.type == TOML_UNKNOWN ? toml_get(bias, key) : value;
}

static int read_header_keys(toml_datum_t value, const char **out, size_t *count)
{
    if (value.type == TOML_UNKNOWN) {
        return 1;
    }
    if (value.type != TOML_ARRAY || value.u.arr.size > 16) {
        return 0;
    }
    for (int i = 0; i < value.u.arr.size; ++i) {
        const char *text = toml_string_value(value.u.arr.elem[i]), *canonical = text;
        if (!text || strlen(text) > 79) {
            return 0;
        }
        if (!strncmp(text, "HIERARCH ", 9)) {
            canonical = text + 9;
        }
        if (!*canonical || !strcmp(canonical, "COMMENT") || !strcmp(canonical, "HISTORY") ||
            !strcmp(canonical, "END") || !strcmp(canonical, "CONTINUE")) {
            return 0;
        }
        for (const char *c = canonical; *c; ++c) {
            if (!isupper((unsigned char)*c) && !isdigit((unsigned char)*c) && !strchr(" _-.", *c)) {
                return 0;
            }
        }
        for (size_t j = 0; j < *count; ++j) {
            if (!strcmp(out[j], canonical)) {
                return 0;
            }
        }
        out[(*count)++] = canonical;
    }
    return 1;
}

static int is_valid_detector_id(const char *text)
{
    if (!text || !*text || strlen(text) > 68) {
        return 0;
    }
    for (; *text; ++text) {
        if ((unsigned char)*text <= 32 || (unsigned char)*text > 126 || *text == ',' ||
            *text == '\'') {
            return 0;
        }
    }
    return 1;
}

int mef_bias_recipe_expand(int argc, char **argv, int *outc, char ***outv,
    mef_bias_recipe_config **owner, char *message, size_t size)
{
    static const char *root_keys[] = {
        "bias_recipe_schema_version", "settings", "bias", "detector", "provenance"};
    static const char *bias_keys[] = {"detectors", "reference_detector", "mad", "ron_pair",
        "high_sigma", "readout_id", "bin_x", "bin_y", "input_bpm", "bpm_hdu", "bpm_good_value",
        "bpm_coordinates", "bpm_expected_extname", "amplifier_id", "median_even_handling"};
    static const char *det_keys[] = {"id", "configuration_detector", "hdus", "expected_extname",
        "readout_id", "bin_x", "bin_y", "input_bpm", "bpm_hdu", "bpm_good_value", "bpm_coordinates",
        "bpm_expected_extname", "amplifier_id"};
    static const char *prov_keys[] = {"primary", "detector"};
    static const char *field_keys[] = {"readout_id", "bin_x", "bin_y", "input_bpm", "bpm_hdu",
        "bpm_good_value", "bpm_coordinates", "bpm_expected_extname", "amplifier_id"};
    static const char *field_args[] = {"--readout-id", "--bin-x", "--bin-y", "--input-bpm",
        "--bpm-hdu", "--bpm-good-value", "--bpm-coordinates", "--bpm-expected-extname",
        "--amplifier-id"};
    const char *path = NULL, *override = NULL, *reason = "Invalid bias recipe TOML envelope";
    mef_bias_recipe_config *recipe = NULL;
    FILE *f = NULL;
    struct stat st;
    long length;
    toml_datum_t root, bias, entries, selection, provenance;
    char *settings = NULL, *csv = NULL;
    const char *ids[4096], *requested[4096], *reference = NULL;
    int slots[4096], selected[4096] = {0};
    size_t requested_count = 0, count = 0;
    *outc = argc;
    *outv = argv;
    *owner = NULL;
    for (int i = 3; i + 1 < argc; i += 2) {
        if (!strcmp(argv[i], "--config")) {
            if (path) {
                return report_recipe_error(message, size, "Duplicate --config");
            }
            path = argv[i + 1];
        }
        if (!strcmp(argv[i], "--detectors")) {
            if (override) {
                return report_recipe_error(message, size, "Duplicate --detectors");
            }
            override = argv[i + 1];
        }
    }
    if (!path) {
        return override ? report_recipe_error(message, size, "--detectors requires recipe TOML")
                        : 1;
    }
    recipe = calloc(1, sizeof(*recipe));
    if (!recipe) {
        goto done;
    }
    recipe->path = realpath(path, NULL);
    if (!recipe->path) {
        goto done;
    }
    f = fopen(recipe->path, "rb");
    if (!f || fstat(fileno(f), &st) || !S_ISREG(st.st_mode) || fseek(f, 0, SEEK_END) ||
        (length = ftell(f)) < 0 || length > 4 * 1024 * 1024 || fseek(f, 0, SEEK_SET)) {
        goto done;
    }
    recipe->source = malloc((size_t)length + 1);
    if (!recipe->source) {
        goto done;
    }
    if (fread(recipe->source, 1, (size_t)length, f) != (size_t)length) {
        goto done;
    }
    recipe->source[length] = 0;
    if (memchr(recipe->source, 0, (size_t)length)) {
        goto done;
    }
    fclose(f);
    f = NULL;
    recipe->parsed = toml_parse(recipe->source, (int)length);
    if (!recipe->parsed.ok) {
        reason = recipe->parsed.errmsg;
        goto done;
    }
    root = recipe->parsed.toptab;
    if (toml_get(root, "bias_recipe_schema_version").type == TOML_UNKNOWN) {
        if (override) {
            reason = "--detectors requires bias_recipe_schema_version=1";
            goto done;
        }
        mef_bias_recipe_config_destroy(recipe);
        return 1;
    }
    if (length > 1024 * 1024 || !TABLE(root, root_keys)) {
        goto done;
    }
    toml_datum_t version = toml_get(root, "bias_recipe_schema_version");
    if (version.type != TOML_INT64 || version.u.int64 != 1) {
        goto done;
    }
    bias = toml_get(root, "bias");
    entries = toml_get(root, "detector");
    provenance = toml_get(root, "provenance");
    if (!TABLE(bias, bias_keys) || entries.type != TOML_ARRAY || entries.u.arr.size < 1 ||
        entries.u.arr.size > 4096) {
        goto done;
    }
    if (provenance.type != TOML_UNKNOWN && (!TABLE(provenance, prov_keys) ||
                                               !read_header_keys(toml_get(provenance, "primary"),
                                                   recipe->primary, &recipe->primary_count) ||
                                               !read_header_keys(toml_get(provenance, "detector"),
                                                   recipe->detector, &recipe->detector_count))) {
        goto done;
    }
    {
        toml_datum_t handling = toml_get(bias, "median_even_handling");
        if (handling.type != TOML_UNKNOWN) {
            recipe->median_even_handling = toml_string_value(handling);
            if (!recipe->median_even_handling ||
                (strcmp(recipe->median_even_handling, "average") &&
                    strcmp(recipe->median_even_handling, "lower"))) {
                reason = "median_even_handling must be average or lower";
                goto done;
            }
        }
    }
    count = (size_t)entries.u.arr.size;
    for (size_t i = 0; i < count; ++i) {
        toml_datum_t e = entries.u.arr.elem[i];
        ids[i] = toml_string_value(toml_get(e, "id"));
        if (!TABLE(e, det_keys) || !is_valid_detector_id(ids[i]) ||
            !toml_nonnegative_integer(toml_get(e, "configuration_detector"), slots + i)) {
            goto done;
        }
        for (size_t j = 0; j < i; ++j) {
            if (!strcmp(ids[i], ids[j]) || slots[i] == slots[j]) {
                reason = "Duplicate detector ID or configuration index";
                goto done;
            }
        }
    }
    selection = toml_get(bias, "detectors");
    if (override) {
        if (!strcmp(override, "all")) {
            for (size_t i = 0; i < count; ++i) {
                selected[i] = 1;
            }
        } else {
            csv = strdup(override);
            if (!csv) {
                goto done;
            }
            char *start = csv;
            while (start) {
                char *comma = strchr(start, ',');
                if (comma) {
                    *comma = 0;
                }
                if (!is_valid_detector_id(start) || requested_count == 4096) {
                    goto done;
                }
                requested[requested_count++] = start;
                start = comma ? comma + 1 : NULL;
            }
        }
    } else if (selection.type == TOML_UNKNOWN ||
               (toml_string_value(selection) && !strcmp(toml_string_value(selection), "all"))) {
        for (size_t i = 0; i < count; ++i) {
            selected[i] = 1;
        }
    } else {
        if (selection.type != TOML_ARRAY || selection.u.arr.size < 1 ||
            selection.u.arr.size > 4096) {
            goto done;
        }
        for (int i = 0; i < selection.u.arr.size; ++i) {
            const char *id = toml_string_value(selection.u.arr.elem[i]);
            if (!is_valid_detector_id(id)) {
                goto done;
            }
            requested[requested_count++] = id;
        }
    }
    for (size_t j = 0; j < requested_count; ++j) {
        size_t i;
        for (i = 0; i < count; ++i) {
            if (!strcmp(ids[i], requested[j])) {
                break;
            }
        }
        if (i == count || selected[i]) {
            reason = "Unknown or duplicate selected detector ID";
            goto done;
        }
        selected[i] = 1;
    }
    reference = toml_string_value(toml_get(bias, "reference_detector"));
    if (toml_get(bias, "reference_detector").type != TOML_UNKNOWN && !reference) {
        goto done;
    }
    int reference_selected = 0;
    for (size_t i = 0; i < count; ++i) {
        if (selected[i]) {
            if (!reference) {
                reference = ids[i];
            }
            if (!strcmp(reference, ids[i])) {
                reference_selected = 1;
            }
        }
    }
    if (!reference_selected) {
        reason = "Reference detector is outside the selected set";
        goto done;
    }
    settings = resolve_recipe_path(recipe, toml_string_value(toml_get(root, "settings")));
    if (!settings) {
        goto done;
    }
    if (!append_argument(recipe, argv[0]) || !append_argument(recipe, "cal") ||
        !append_argument(recipe, "bias") || !append_option_value(recipe, "--config", settings) ||
        !append_option_value(recipe, "--reference-detector", reference)) {
        goto done;
    }
    for (int i = 3; i < argc; i += 2) {
        if (i + 1 >= argc) {
            goto done;
        }
        if (!strcmp(argv[i], "--config") || !strcmp(argv[i], "--detectors")) {
            continue;
        }
        if (strcmp(argv[i], "--bias") && strcmp(argv[i], "--output") &&
            strcmp(argv[i], "--output-dir")) {
            reason = "Recipe TOML owns detector/measurement choices; do not mix legacy CLI fields";
            goto done;
        }
        if (!append_option_value(recipe, argv[i], argv[i + 1])) {
            goto done;
        }
    }
    toml_datum_t mad = toml_get(bias, "mad"), ron = toml_get(bias, "ron_pair"),
                 sigma = toml_get(bias, "high_sigma");
    if (mad.type != TOML_BOOLEAN ||
        !append_option_value(recipe, "--mad", mad.u.boolean ? "yes" : "no")) {
        goto done;
    }
    if (ron.type != TOML_UNKNOWN &&
        (ron.type != TOML_ARRAY || ron.u.arr.size != 2 ||
            !append_integer_option(recipe, "--ron-first", ron.u.arr.elem[0]) ||
            !append_integer_option(recipe, "--ron-second", ron.u.arr.elem[1]))) {
        goto done;
    }
    if (sigma.type != TOML_UNKNOWN) {
        double value = sigma.type == TOML_FP64    ? sigma.u.fp64
                       : sigma.type == TOML_INT64 ? (double)sigma.u.int64
                                                  : NAN;
        char text[64];
        if (!isfinite(value) || value <= 0) {
            goto done;
        }
        snprintf(text, sizeof(text), "%.17g", value);
        if (!append_option_value(recipe, "--high-sigma", text)) {
            goto done;
        }
    }
    for (size_t i = 0; i < count; ++i) {
        if (selected[i]) {
            toml_datum_t e = entries.u.arr.elem[i], hdus = toml_get(e, "hdus");
            if (!append_option_value(recipe, "--detector-id", ids[i]) ||
                !append_integer_option(
                    recipe, "--config-detector", toml_get(e, "configuration_detector")) ||
                hdus.type != TOML_ARRAY || hdus.u.arr.size < 1 || hdus.u.arr.size > 100000) {
                goto done;
            }
            for (int j = 0; j < hdus.u.arr.size; ++j) {
                if (!append_integer_option(recipe, "--hdu", hdus.u.arr.elem[j])) {
                    goto done;
                }
            }
            toml_datum_t extname = toml_get(e, "expected_extname");
            if (extname.type != TOML_UNKNOWN && !toml_string_value(extname)) {
                goto done;
            }
            if (!append_option_value(recipe, "--raw-expected-extname",
                    toml_string_value(extname) ? toml_string_value(extname) : "omitted")) {
                goto done;
            }
            const char *mask = toml_string_value(inherited_option(e, bias, "input_bpm"));
            if (!mask) {
                goto done;
            }
            for (size_t j = 0; j < sizeof(field_keys) / sizeof(*field_keys); ++j) {
                toml_datum_t value = inherited_option(e, bias, field_keys[j]);
                if (j >= 4 && j <= 7 && !strcmp(mask, "omitted")) {
                    if (value.type != TOML_UNKNOWN) {
                        reason = "BPM omitted but BPM fields supplied";
                        goto done;
                    }
                    continue;
                }
                if ((j == 5 || j == 7) && value.type == TOML_UNKNOWN) {
                    continue;
                }
                if (j == 1 || j == 2 || j == 4 || j == 5) {
                    if (!append_integer_option(recipe, field_args[j], value)) {
                        goto done;
                    }
                } else {
                    const char *text = toml_string_value(value);
                    char *absolute = NULL;
                    if (j == 3 && strcmp(mask, "omitted")) {
                        text = absolute = resolve_recipe_path(recipe, mask);
                    }
                    int okay = text && append_option_value(recipe, field_args[j], text);
                    free(absolute);
                    if (!okay) {
                        goto done;
                    }
                }
            }
        }
    }
    free(settings);
    free(csv);
    *outc = recipe->argc;
    *outv = recipe->argv;
    *owner = recipe;
    return 1;
done:
    if (f) {
        fclose(f);
    }
    report_recipe_error(message, size, reason);
    free(settings);
    free(csv);
    mef_bias_recipe_config_destroy(recipe);
    return 0;
}

const char *mef_bias_recipe_median_even_handling(const mef_bias_recipe_config *recipe)
{
    return recipe ? recipe->median_even_handling : NULL;
}
