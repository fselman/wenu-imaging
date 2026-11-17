#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_mff.h"
#include "mef_detector_catalogue.h"
#include "mef_project.h"
#include "mef_bpm_linearity.h" /* Shared streaming file identity. */
#include <limits.h>
#include <strings.h>
#include <sys/stat.h>
#undef malloc
#undef calloc
#undef free
#undef strdup

static const char *string(toml_datum_t table, const char *key)
{
    if (table.type != TOML_TABLE)
        return NULL;
    toml_datum_t value = toml_get(table, key);
    return value.type == TOML_STRING && value.u.str.len > 0 &&
        strlen(value.u.s) == (size_t)value.u.str.len ? value.u.s : NULL;
}

static int integer(toml_datum_t value, int min, int max, int *out)
{
    if (value.type != TOML_INT64 || value.u.int64 < min || value.u.int64 > max)
        return 0;
    *out = (int)value.u.int64;
    return 1;
}

static int only_keys(toml_datum_t table, const char *const *keys, size_t count)
{
    if (table.type != TOML_TABLE)
        return 0;
    for (int i = 0; i < table.u.tab.size; ++i) {
        size_t j = 0;
        while (j < count && strcmp(keys[j], table.u.tab.key[i]))
            ++j;
        if (j == count)
            return 0;
    }
    return 1;
}

static char *resolve(const char *directory, const char *name)
{
    char path[MEF_PRODUCT_PATH_SIZE];
    if (name == NULL || snprintf(path, sizeof(path), "%s%s%s",
            name[0] == '/' ? "" : directory, name[0] == '/' ? "" : "/", name)
            >= (int)sizeof(path))
        return NULL;
    return realpath(path, NULL);
}

static char *relative_to_file(const char *file, const char *name)
{
    char directory[MEF_PRODUCT_PATH_SIZE];
    size_t length = (size_t)(strrchr(file, '/') - file);
    memcpy(directory, file, length);
    directory[length] = '\0';
    return resolve(directory, name);
}

static int below(const char *root, const char *path)
{
    size_t length = strlen(root);
    return !strncmp(path, root, length) && path[length] == '/';
}

static int directory(const char *path)
{
    struct stat st;
    return path && stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

static int project_paths(mef_mff *mff, const char *project, const char *run_name,
                         char **calibration)
{
    toml_result_t document = {0};
    char *origin = NULL, *reduced = NULL, *orchestration = NULL, *raw = NULL;
    int okay = 0;

    if (!mef_project_read(project, &document, &origin, NULL, NULL))
        goto done;
    toml_datum_t roots = toml_get(toml_get(document.toptab, "project"), "roots");
    reduced = relative_to_file(origin, string(roots, "output"));
    orchestration = relative_to_file(project, ".");
    raw = relative_to_file(origin, string(roots, "raw"));
    *calibration = relative_to_file(origin, string(roots, "calibration"));
    if (!directory(reduced) || !directory(raw) || !directory(orchestration) ||
        !directory(*calibration) || !below(reduced, *calibration) ||
        below(raw, reduced) || below(reduced, raw) || !strcmp(raw, reduced) ||
        below(raw, orchestration) || below(orchestration, raw) || !strcmp(raw, orchestration) ||
        below(reduced, orchestration) || below(orchestration, reduced) || !strcmp(reduced, orchestration) ||
        strcmp(orchestration, mff->run->invocation_directory) ||
        !below(orchestration, mff->recipe.path) || run_name[0] == '/')
        goto done;
    mff->output = resolve(reduced, run_name);
    if (!directory(mff->output) || !below(*calibration, mff->output))
        goto done;
    mff->project_evidence = mef_toml_file_read(origin, 1024 * 1024);
    okay = mff->project_evidence.parsed.ok;
done:
    toml_free(document);
    free(origin);
    free(raw);
    free(reduced);
    free(orchestration);
    return okay;
}

static int primary_matches(const mef_mff *mff, int role, char *path)
{
    qfits_header *header = qfits_header_read(path);
    int okay = 0;
    if (header == NULL)
        return 0;

    char *value = qfits_header_getstr(header, "INSTRUME");
    if (!value || strcasecmp(qfits_pretty_string(value), mff->instrument))
        goto done;
    if (role != MFF_BPM) {
        const char *category = role == MFF_DOME ? "CALIB.MASTER_DOME_FLAT" : "CALIB.MASTER_SKY_FLAT";
        value = qfits_header_getstr(header, "PRODCATG");
        if (!value || strcmp(qfits_pretty_string(value), category))
            goto done;
        value = qfits_header_getstr(header, "FILTER");
        if (!value || strcmp(qfits_pretty_string(value), mff->filter))
            goto done;
    }
    okay = 1;
done:
    qfits_header_destroy(header);
    return okay;
}

static int bind_components(mef_mff *mff, const char *root, toml_datum_t inputs,
                           mef_detector_definition *selected)
{
    static const char *const keys[] = {"dome", "sky", "bpm"};
    mef_detector_binding *bindings = calloc(mff->detector_count, sizeof(*bindings));
    mef_layout_options layout_options = {
        .max_hdus = 4096, .max_header_bytes = MEF_LAYOUT_DEFAULT_HEADER_BYTES,
        .bin_x_key = "HIERARCH ESO DET WIN1 BINX",
        .bin_y_key = "HIERARCH ESO DET WIN1 BINY"
    };
    int okay = 0;

    if (!bindings)
        return 0;
    for (int role = 0; role < MFF_COMPONENTS; ++role) {
        mef_mff_component *component = mff->components + role;
        const char *name = string(inputs, keys[role]);
        if (role == MFF_BPM && toml_get(inputs, keys[role]).type == TOML_UNKNOWN)
            continue;
        struct stat identity;
        component->path = resolve(root, name);
        if (!component->path || !below(root, component->path) ||
            stat(component->path, &identity) || !S_ISREG(identity.st_mode) ||
            !mef_bpm_linearity_hash(component->path, component->sha256) ||
            !primary_matches(mff, role, component->path) ||
            mef_layout_read(component->path, &layout_options, NULL, &component->layout,
                &mff->error) != MEF_OK) {
            snprintf(mff->run->message, sizeof(mff->run->message),
                "Cannot admit %s FITS: expected a compatible product under project calibration.", keys[role]);
            goto done;
        }
        if (role != MFF_DOME && !strcmp(component->path, mff->components[MFF_DOME].path))
            goto done;
        if (role == MFF_BPM && !strcmp(component->path, mff->components[MFF_SKY].path))
            goto done;

        size_t hdu_count;
        const mef_hdu_layout *hdus = mef_layout_hdus(component->layout, &hdu_count);
        for (size_t i = 0; i < mff->detector_count; ++i) {
            const char *id = selected[i].id;
            const mef_hdu_layout *plane = NULL;
            for (size_t hdu = 1; hdu < hdu_count; ++hdu) {
                if (hdus[hdu].has_extname && !strcmp(hdus[hdu].extname, id)) {
                    if (plane) {
                        snprintf(mff->run->message, sizeof(mff->run->message),
                            "Ambiguous detector %.68s in %s master.", id, keys[role]);
                        goto done;
                    }
                    plane = hdus + hdu;
                }
            }
            if (!plane || strlen(id) > 68 || strchr(id, '\'') ||
                plane->kind != MEF_HDU_IMAGE || plane->naxis != 2 ||
                plane->axes[0] > INT_MAX || plane->axes[1] > INT_MAX ||
                plane->axes[0] < (size_t)mff->radius || plane->axes[1] < (size_t)mff->radius)
                goto done;
            const mef_bound_detector *dome = role == MFF_DOME ? NULL :
                mef_layout_find(mff->components[MFF_DOME].mapping, id);
            if (dome && (dome->image.axes[0] != plane->axes[0] ||
                         dome->image.axes[1] != plane->axes[1] ||
                         (dome->image.detsec[0] && plane->detsec[0] &&
                          strcmp(dome->image.detsec, plane->detsec)) ||
                         (dome->image.ccdsec[0] && plane->ccdsec[0] &&
                          strcmp(dome->image.ccdsec, plane->ccdsec))))
                goto done;

            bindings[i] = (mef_detector_binding){
                .detector_id = id, .extname = id, .hdu_index = plane->hdu_index,
                .unit = role == MFF_BPM ? NULL : "1", .readout_id = mff->readout,
                .bin_x = mff->bin_x, .bin_y = mff->bin_y, .active_x = 1, .active_y = 1,
                .active_width = (int)plane->axes[0], .active_height = (int)plane->axes[1],
                .configuration_detector = (size_t)selected[i].slot,
                .health = MEF_HEALTH_UNKNOWN, .selection = MEF_OUTPUT_SELECTED
            };
        }
        if (mef_layout_bind(component->layout, bindings, mff->detector_count, NULL,
                &component->mapping, &mff->error) != MEF_OK)
            goto done;
    }
    okay = 1;
done:
    free(bindings);
    return okay;
}

int mef_mff_admit(mef_mff *mff, const char *config)
{
    static const char *const root_keys[] = {"mff_recipe_schema_version", "project",
        "detector_toml", "run", "inputs", "mff"};
    static const char *const input_keys[] = {"dome", "sky", "bpm", "bpm_good_value"};
    static const char *const settings_keys[] = {"filter", "radius", "reference_detector"};
    char *recipe_path = realpath(config, NULL), *profile = NULL, *project = NULL, *calibration = NULL;
    mef_detector_definition *selected = NULL;
    int okay = 0, version;

    snprintf(mff->run->message, sizeof(mff->run->message),
        "Invalid MFF recipe, project paths or detector binding.");
    if (!recipe_path)
        goto done;
    mff->recipe = mef_toml_file_read(recipe_path, 1024 * 1024);
    if (!mff->recipe.parsed.ok)
        goto done;
    toml_datum_t root = mff->recipe.parsed.toptab;
    if (!only_keys(root, root_keys, sizeof(root_keys) / sizeof(*root_keys)) ||
        !integer(toml_get(root, root_keys[0]), 1, 1, &version))
        goto done;
    toml_datum_t inputs = toml_get(root, "inputs"), settings = toml_get(root, "mff");
    if (!only_keys(inputs, input_keys, sizeof(input_keys) / sizeof(*input_keys)) ||
        !only_keys(settings, settings_keys, sizeof(settings_keys) / sizeof(*settings_keys)))
        goto done;
    mff->filter = string(settings, "filter");
    mff->reference = string(settings, "reference_detector");
    if (!mff->filter || !mff->reference ||
        !integer(toml_get(settings, "radius"), 1, INT_MAX, &mff->radius))
        goto done;
    if (toml_get(inputs, "bpm").type != TOML_UNKNOWN) {
        if (!integer(toml_get(inputs, "bpm_good_value"), 0, 1, &mff->bpm_good))
            goto done;
    } else if (toml_get(inputs, "bpm_good_value").type != TOML_UNKNOWN) {
        goto done;
    }
    const char *run = string(root, "run");
    project = relative_to_file(recipe_path, string(root, "project"));
    profile = relative_to_file(recipe_path, string(root, "detector_toml"));
    if (!run || !project || !profile || !project_paths(mff, project, run, &calibration))
        goto done;
    mff->profile = mef_toml_file_read(profile, 1024 * 1024);
    if (!mff->profile.parsed.ok || !mef_detector_catalogue_valid(mff->profile.parsed.toptab))
        goto done;
    toml_datum_t geometry = mff->profile.parsed.toptab;
    toml_datum_t binning = toml_get(geometry, "binning"), entries = toml_get(geometry, "detector");
    mff->instrument = string(geometry, "instrument");
    mff->readout = string(geometry, "readout_id");
    if (!mff->instrument || !mff->readout || binning.type != TOML_ARRAY || binning.u.arr.size != 2 ||
        !integer(binning.u.arr.elem[0], 1, INT_MAX, &mff->bin_x) ||
        !integer(binning.u.arr.elem[1], 1, INT_MAX, &mff->bin_y))
        goto done;
    selected = calloc((size_t)entries.u.arr.size, sizeof(*selected));
    if (!selected)
        goto done;
    int reference_selected = 0;
    for (int i = 0; i < entries.u.arr.size; ++i) {
        mef_detector_definition detector;
        if (!mef_detector_catalogue_entry(geometry, i, &detector))
            goto done;
        if (detector.enabled) {
            selected[mff->detector_count++] = detector;
            reference_selected |= !strcmp(detector.id, mff->reference);
        }
    }
    if (!reference_selected || !bind_components(mff, calibration, inputs, selected))
        goto done;
    size_t count = mff->detector_count;
    mff->detectors = calloc(count, sizeof(*mff->detectors));
    mff->assembly = calloc(count, sizeof(*mff->assembly));
    mff->qc = calloc(count, sizeof(*mff->qc));
    if (mff->components[MFF_BPM].path)
        mff->bpm_bindings = calloc(count, sizeof(*mff->bpm_bindings));
    if (!mff->detectors || !mff->assembly || !mff->qc ||
        (mff->components[MFF_BPM].path && !mff->bpm_bindings))
        goto done;
    for (size_t i = 0; i < count; ++i) {
        mff->detectors[i].id = selected[i].id;
        mff->detectors[i].slot = selected[i].slot;
        mff->detectors[i].amplifier = string(selected[i].definition, "amplifier");
        if (!mff->detectors[i].amplifier)
            goto done;
    }
    mff->run->message[0] = '\0';
    okay = 1;
done:
    free(recipe_path);
    free(profile);
    free(project);
    free(calibration);
    free(selected);
    return okay;
}

int mef_mff_inputs_unchanged(mef_mff *mff)
{
    for (int i = 0; i < MFF_COMPONENTS; ++i) {
        const mef_mff_component *component = mff->components + i;
        char digest[65];
        if (component->path && (!mef_bpm_linearity_hash(component->path, digest) ||
                strcmp(digest, component->sha256))) {
            snprintf(mff->run->message, sizeof(mff->run->message),
                "MFF input changed during processing: %.400s", component->path);
            return 0;
        }
    }
    return 1;
}

void mef_mff_destroy(mef_mff *mff)
{
    for (int i = 0; i < MFF_COMPONENTS; ++i) {
        mef_layout_map_destroy(mff->components[i].mapping);
        mef_layout_destroy(mff->components[i].layout);
        free(mff->components[i].path);
    }
    mef_toml_file_destroy(&mff->recipe);
    mef_toml_file_destroy(&mff->profile);
    mef_toml_file_destroy(&mff->project_evidence);
    mef_error_destroy(mff->error);
    free(mff->output);
    free(mff->detectors);
    free(mff->assembly);
    free(mff->qc);
    free(mff->bpm_bindings);
}
