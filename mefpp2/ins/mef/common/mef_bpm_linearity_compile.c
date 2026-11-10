/* Native authoring admission. Only small control transports are materialized;
 * image payloads remain with the shared detector-cube services.
 */
#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bpm_linearity.h"
#include "mef_config_toml.h"
#include "mef_bias_settings.h"
#include <errno.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define MAX_FILES 65536
#define MAX_PATH 4096

typedef mef_bpm_linearity_frozen frozen_file;

typedef struct {
    toml_result_t recipe, project, geometry, processing;
    frozen_file *files;
    size_t count;
    char *controls, *output, *raw, *calibration, *work, *logs, *orchestration;
    const char *source, *revision;
    FILE *bindings;
    int qc;
} compilation;

static int fields(toml_datum_t table, const char *allowed)
{
    if (table.type != TOML_TABLE) {
        return 0;
    }
    for (int i = 0; i < table.u.tab.size; ++i) {
        char token[128];
        if (snprintf(token, sizeof(token), "|%s|", table.u.tab.key[i]) >= (int)sizeof(token) ||
            !strstr(allowed, token)) {
            return 0;
        }
    }
    return 1;
}

static const char *string(toml_datum_t table, const char *key)
{
    const char *s = mef_bpm_linearity_string(table, key);
    return s && !strpbrk(s, "\t\r\n") ? s : NULL;
}

static long integer(toml_datum_t table, const char *key, long fallback)
{
    toml_datum_t v = toml_get(table, key);
    return v.type == TOML_INT64 ? v.u.int64 : fallback;
}

static double real(toml_datum_t table, const char *key, double fallback)
{
    toml_datum_t v = toml_get(table, key);
    return v.type == TOML_FP64 ? v.u.fp64 : v.type == TOML_INT64 ? (double)v.u.int64 : fallback;
}

static char *format(const char *pattern, ...)
{
    va_list a, b;
    char *s;
    int n;
    va_start(a, pattern);
    va_copy(b, a);
    n = vsnprintf(NULL, 0, pattern, a);
    va_end(a);
    s = n >= 0 ? malloc((size_t)n + 1) : NULL;
    if (s) {
        vsnprintf(s, (size_t)n + 1, pattern, b);
    }
    va_end(b);
    return s;
}

static void quoted(FILE *f, const char *s)
{
    const unsigned char *p = (const unsigned char *)s;
    fputc('"', f);
    for (; p && *p; ++p) {
        if (*p == '"' || *p == '\\') {
            fputc('\\', f);
        }
        if (*p < 32 || *p == 127) {
            fprintf(f, "\\u%04x", (unsigned)*p);
        } else {
            fputc(*p, f);
        }
    }
    fputc('"', f);
}

static char *path(const char *base, const char *value)
{
    char full[MAX_PATH], result[MAX_PATH];
    if (!value ||
        snprintf(full, sizeof(full), "%s%s%s", value[0] == '/' ? "" : base,
            value[0] == '/' ? "" : "/", value) >= (int)sizeof(full) ||
        !realpath(full, result) || strpbrk(result, "\t\r\n")) {
        return NULL;
    }
    return strdup(result);
}

static int freeze(compilation *c, const char *name)
{
    frozen_file *f;
    for (size_t i = 0; i < c->count; ++i) {
        if (!strcmp(c->files[i].path, name)) {
            return 1;
        }
    }
    if (c->count == MAX_FILES) {
        return 0;
    }
    f = c->files + c->count;
    f->path = strdup(name);
    if (!f->path || stat(name, &f->identity) || !S_ISREG(f->identity.st_mode) ||
        !mef_bpm_linearity_hash(name, f->digest)) {
        free(f->path);
        f->path = NULL;
        return 0;
    }
    ++c->count;
    return 1;
}

static int project_freeze(void *user, const char *name)
{
    return freeze(user, name);
}

static toml_result_t document(compilation *c, const char *name)
{
    toml_result_t result = {0};
    if (name && freeze(c, name)) {
        result = toml_parse_file_ex(name);
    }
    return result;
}

static int finish_file(compilation *c, FILE *f, const char *name)
{
    int okay = f && !ferror(f);
    if (f && fclose(f)) {
        okay = 0;
    }
    return okay && freeze(c, name);
}

static FILE *control(compilation *c, const char *directory, const char *name, char **out)
{
    (void)c;
    *out = format("%s/%s", directory, name);
    return *out ? fopen(*out, "wx") : NULL;
}

/* The ordinary native settings reader validates composition and exact types.
 * Freeze every included settings source, not just the top-level filename.
 */
static int settings_sources(compilation *c, const char *name, int depth)
{
    toml_result_t d;
    char *base, *slash;
    toml_datum_t includes;
    int okay = 1;
    if (depth > 16) {
        return 0;
    }
    d = document(c, name);
    if (!d.ok) {
        toml_free(d);
        return 0;
    }
    base = strdup(name);
    if (!base) {
        toml_free(d);
        return 0;
    }
    slash = strrchr(base, '/');
    *slash = 0;
    includes = toml_get(d.toptab, "include");
    if (includes.type != TOML_UNKNOWN && includes.type != TOML_ARRAY) {
        okay = 0;
    }
    if (includes.type == TOML_ARRAY) {
        for (int i = 0; i < includes.u.arr.size && okay; ++i) {
            toml_datum_t v = includes.u.arr.elem[i];
            char *child = v.type == TOML_STRING ? path(base, v.u.s) : NULL;
            okay = child && settings_sources(c, child, depth + 1);
            free(child);
        }
    }
    free(base);
    toml_free(d);
    return okay;
}

static toml_datum_t find(toml_datum_t array, const char *field, const char *id)
{
    toml_datum_t result = {0};
    if (array.type == TOML_ARRAY) {
        for (int i = 0; i < array.u.arr.size; ++i) {
            const char *s = string(array.u.arr.elem[i], field);
            if (s && !strcmp(s, id)) {
                if (result.type != TOML_UNKNOWN) {
                    result.type = TOML_UNKNOWN;
                    return result;
                }
                result = array.u.arr.elem[i];
            }
        }
    }
    return result;
}

static int rectangle(toml_datum_t value, int out[4])
{
    if (value.type != TOML_ARRAY || value.u.arr.size != 4) {
        return 0;
    }
    for (int i = 0; i < 4; ++i) {
        toml_datum_t v = value.u.arr.elem[i];
        if (v.type != TOML_INT64 || v.u.int64 < 1 || v.u.int64 > 100000) {
            return 0;
        }
        out[i] = (int)v.u.int64;
    }
    return out[0] <= out[1] && out[2] <= out[3];
}

static int selected(toml_datum_t ids, const char *id)
{
    if (ids.type != TOML_ARRAY) {
        return 0;
    }
    for (int i = 0; i < ids.u.arr.size; ++i) {
        toml_datum_t v = ids.u.arr.elem[i];
        if (v.type == TOML_STRING && !strcmp(v.u.s, id)) {
            return 1;
        }
    }
    return 0;
}

static int regions(compilation *c, const char *dir, const char *id, const char *amplifier,
    toml_datum_t references, toml_datum_t sites, char **rois_path, char **sites_path,
    char **reference_path)
{
    char *names[3] = {NULL, NULL, NULL};
    FILE *streams[3] = {NULL, NULL, NULL};
    toml_datum_t rois = toml_get(c->processing.toptab, "roi");
    size_t count = 0, reference_count = 0;
    int okay = 0;
    if (rois.type != TOML_ARRAY || references.type != TOML_ARRAY || !references.u.arr.size ||
        sites.type != TOML_ARRAY || !sites.u.arr.size) {
        return 0;
    }
    streams[0] = control(c, dir, "rois.toml", names);
    streams[1] = control(c, dir, "sites.toml", names + 1);
    streams[2] = control(c, dir, "reference-rois.tsv", names + 2);
    if (!streams[0] || !streams[1] || !streams[2]) {
        goto done;
    }
    fputs("roi_schema_version = 1\n", streams[0]);
    fputs("roi_schema_version = 1\n", streams[1]);
    for (int i = 0; i < rois.u.arr.size; ++i) {
        toml_datum_t r = rois.u.arr.elem[i];
        const char *det = string(r, "detector"), *amp = string(r, "amplifier"),
                   *rid = string(r, "id");
        if (!det || strcmp(det, id)) {
            continue;
        }
        int z[4] = {(int)integer(r, "xmin", 0), (int)integer(r, "xmax", 0),
            (int)integer(r, "ymin", 0), (int)integer(r, "ymax", 0)};
        if (!rid || !amp || strcmp(amp, amplifier) || z[0] < 1 || z[0] > z[1] || z[2] < 1 ||
            z[2] > z[3]) {
            goto done;
        }
        ++count;
        fprintf(streams[0], "\n[[roi]]\nid = ");
        quoted(streams[0], rid);
        fputs("\ndetector = ", streams[0]);
        quoted(streams[0], id);
        fputs("\namplifier = ", streams[0]);
        quoted(streams[0], amplifier);
        fprintf(
            streams[0], "\nxmin = %d\nxmax = %d\nymin = %d\nymax = %d\n", z[0], z[1], z[2], z[3]);
        if (selected(references, rid)) {
            fprintf(streams[2], "%d %d %d %d\n", z[0], z[1], z[2], z[3]);
            ++reference_count;
        }
    }
    if (!count || reference_count != (size_t)references.u.arr.size) {
        goto done;
    }
    for (int i = 0; i < sites.u.arr.size; ++i) {
        toml_datum_t site = sites.u.arr.elem[i];
        const char *rid = string(site, "roi");
        long x = integer(site, "x", 0), y = integer(site, "y", 0);
        toml_datum_t roi = find(rois, "id", rid ? rid : "");
        const char *det = string(roi, "detector");
        if (!fields(site, "|roi|x|y|") || !rid || !det || strcmp(det, id) ||
            x < integer(roi, "xmin", 0) || x > integer(roi, "xmax", 0) ||
            y < integer(roi, "ymin", 0) || y > integer(roi, "ymax", 0)) {
            goto done;
        }
        fputs("\n[[roi]]\nid = ", streams[1]);
        quoted(streams[1], rid);
        fputs("\ndetector = ", streams[1]);
        quoted(streams[1], id);
        fputs("\namplifier = ", streams[1]);
        quoted(streams[1], amplifier);
        fprintf(streams[1], "\nxmin = %ld\nxmax = %ld\nymin = %ld\nymax = %ld\n", x, x, y, y);
    }
    okay = 1;
done:
    for (int i = 0; i < 3; ++i) {
        if (!finish_file(c, streams[i], names[i])) {
            okay = 0;
        }
    }
    *rois_path = names[0];
    *sites_path = names[1];
    *reference_path = names[2];
    return okay;
}

static void argument(FILE *f, int *count, const char *value)
{
    if ((*count)++) {
        fputs(", ", f);
    }
    quoted(f, value);
}

static void option(FILE *f, int *count, const char *key, const char *value)
{
    argument(f, count, key);
    argument(f, count, value);
}

static long input_hdu(toml_datum_t detector, const char *key, int index, long fallback)
{
    toml_datum_t values = toml_get(detector, key);
    if (values.type == TOML_UNKNOWN) {
        return fallback;
    }
    if (values.type != TOML_ARRAY || index >= values.u.arr.size ||
        values.u.arr.elem[index].type != TOML_INT64) {
        return -1;
    }
    long value = values.u.arr.elem[index].u.int64;
    return value >= 0 && value <= 127 ? value : -1;
}

static int context_text(FILE *f, const char *key, const char *filename)
{
    char *text = malloc(1024 * 1024 + 1);
    FILE *input = filename ? fopen(filename, "rb") : NULL;
    size_t n;
    int okay = 0;
    if (!text || !input) {
        goto done;
    }
    n = fread(text, 1, 1024 * 1024 + 1, input);
    if (ferror(input) || n > 1024 * 1024 || memchr(text, 0, n)) {
        goto done;
    }
    text[n] = 0;
    fputc(',', f);
    quoted(f, key);
    fputc(':', f);
    quoted(f, text);
    okay = !ferror(f);
done:
    if (input) {
        fclose(input);
    }
    free(text);
    return okay;
}

static int detector(compilation *c, toml_datum_t row, size_t ordinal, const char *settings)
{
    const char *id = string(row, "detector_id"), *readout = string(row, "readout_id");
    toml_datum_t geometry = find(toml_get(c->geometry.toptab, "detector"), "id", id ? id : "");
    toml_datum_t trim = find(toml_get(c->processing.toptab, "trim"), "detector", id ? id : "");
    toml_datum_t controls = toml_get(c->processing.toptab, "linearity_preparation");
    toml_datum_t policy = toml_get(c->recipe.toptab, "bpm"),
                 inputs = toml_get(c->recipe.toptab, "inputs");
    toml_datum_t flats = toml_get(inputs, "flat"), biases = toml_get(inputs, "bias"),
                 accepted = toml_get(row, "bias_accepted");
    toml_datum_t size = toml_get(geometry, "raw_size"),
                 identity = toml_get(c->recipe.toptab, "identity");
    const char *amplifier = string(geometry, "amplifier"),
               *encoding = string(controls, "mask_encoding");
    long slot = integer(row, "configuration_detector", -1), hdu = integer(row, "hdu", -1),
         mhdu = integer(row, "master_hdu", -1);
    long bhdu = integer(row, "bpm_hdu", -1), good = integer(controls, "binary_good_value", -1),
         reject = integer(controls, "reject_bits", -1);
    long pixels = integer(row, "max_loaded_pixels", 0), rows = integer(row, "max_rows", 0);
    double saturation = real(controls, "raw_saturation_adu", NAN),
           tolerance = real(controls, "pair_time_tolerance_s", NAN);
    toml_datum_t mad = toml_get(controls, "with_mad");
    char *dir = NULL, *plan_path = NULL, *bias_path = NULL, *flat_path = NULL, *native = NULL,
         *context = NULL;
    char *roi = NULL, *sites = NULL, *reference = NULL, *master = NULL, *bpm = NULL, *work = NULL,
         *product = NULL, *prepared = NULL;
    char *fits = NULL, *sidecar = NULL, *log = NULL;
    FILE *plan = NULL, *bias = NULL, *flat = NULL, *f = NULL;
    mef_config *configuration = NULL;
    mef_bias_settings g;
    char diagnostic[256], number[128];
    int okay = 0, crop[4], raw[2], n;
    const char *mask = string(row, "input_bpm"), *mode = string(policy, "output_mode"),
               *acquisition = string(policy, "acquisition");
    int supplied = mask && strcmp(mask, "omitted");
    if (!fields(row, "|detector_id|configuration_detector|hdu|flat_hdus|bias_hdus|readout_id|"
                     "master_bias|master_hdu|master_sha256|input_bpm|bpm_hdu|bias_accepted|"
                     "reference_rois|sites|max_loaded_pixels|max_rows|") ||
        !id || !readout || !amplifier || slot < 0 ||
        integer(geometry, "native_paf_chip", 0) != slot + 1 || hdu < 0 || hdu > 127 || mhdu < 0 ||
        mhdu > 127 || !mask || !mode || !acquisition ||
        (strcmp(mode, "new") && strcmp(mode, "combined")) ||
        (!supplied && !strcmp(mode, "combined")) ||
        (strcmp(acquisition, "quick") && strcmp(acquisition, "provisional")) ||
        size.type != TOML_ARRAY || size.u.arr.size != 2 ||
        !rectangle(toml_get(trim, "retained"), crop) || flats.type != TOML_ARRAY ||
        flats.u.arr.size < 2 || flats.u.arr.size > 64 || flats.u.arr.size % 2 ||
        biases.type != TOML_ARRAY || biases.u.arr.size < 3 || biases.u.arr.size > 64 ||
        accepted.type != TOML_ARRAY || accepted.u.arr.size != biases.u.arr.size ||
        mad.type != TOML_BOOLEAN || !encoding || !isfinite(saturation) || saturation <= 0 ||
        !isfinite(tolerance) || tolerance < 0 || pixels <= 0 || rows <= 0 || good < 0 || good > 1 ||
        reject < 0 || reject > 255) {
        goto done;
    }
    for (int i = 0; i < 2; ++i) {
        if (size.u.arr.elem[i].type != TOML_INT64) {
            goto done;
        }
        raw[i] = (int)size.u.arr.elem[i].u.int64;
    }
    if (raw[0] < 1 || raw[1] < 1 ||
        (strcmp(encoding, "binary") && strcmp(encoding, "reason8") &&
            strcmp(encoding, "omitted")) ||
        (supplied && !strcmp(encoding, "omitted")) ||
        (double)flats.u.arr.size * raw[0] * raw[1] +
                2.0 * (crop[1] - crop[0] + 1) * (crop[3] - crop[2] + 1) >
            pixels) {
        goto done;
    }
    for (int cohort = 0; cohort < 2; ++cohort) {
        toml_datum_t hdus = toml_get(row, cohort ? "bias_hdus" : "flat_hdus");
        if (hdus.type != TOML_UNKNOWN &&
            (hdus.type != TOML_ARRAY ||
                hdus.u.arr.size != (cohort ? biases.u.arr.size : flats.u.arr.size))) {
            goto done;
        }
    }
    master = path(c->calibration, string(row, "master_bias"));
    bpm = supplied ? path(c->calibration, mask) : strdup("omitted");
    if (!master || !bpm || !mef_bpm_linearity_below(master, c->calibration) ||
        (supplied && (!mef_bpm_linearity_below(bpm, c->calibration) || bhdu < 0 || bhdu > 127)) ||
        !freeze(c, master) || (supplied && !freeze(c, bpm))) {
        goto done;
    }
    const char *master_digest = string(row, "master_sha256");
    const char *digest = NULL;
    for (size_t input = 0; input < c->count; ++input) {
        if (!strcmp(c->files[input].path, master)) {
            digest = c->files[input].digest;
        }
    }
    if (!master_digest || !digest || strcmp(master_digest, digest)) {
        goto done;
    }
    dir = format("%s/detector-%03lu", c->controls, (unsigned long)ordinal);
    work = format(
        "%s/%s/detector-%03lu", c->work, strrchr(c->output, '/') + 1, (unsigned long)ordinal);
    product = format("%s/detector-%03lu", c->output, (unsigned long)ordinal);
    if (!dir || !work || !product || mkdir(dir, 0700)) {
        goto done;
    }
    native = format("%s/native.toml", dir);
    f = native ? fopen(native, "wx") : NULL;
    if (!f) {
        goto done;
    }
    mef_config_toml_initialize();
    if (mef_config_from_toml(settings, NULL, &configuration, diagnostic, sizeof(diagnostic)) !=
        MEF_OK) {
        fprintf(stderr, "Native settings: %s\n", diagnostic);
        goto done;
    }
    if (mef_config_response_toml(configuration, f, real(policy, "response_low", 0.5),
            real(policy, "response_high", 1.5)) != MEF_OK ||
        !finish_file(c, f, native)) {
        f = NULL;
        goto done;
    }
    f = NULL;
    if (mef_config_bias_settings(configuration, (size_t)slot, &g) != MEF_OK ||
        memcmp(crop, g.trim, sizeof(crop))) {
        fprintf(stderr, "Detector %s: native settings disagree with processing geometry\n", id);
        goto done;
    }
    if (g.minimum_frames != integer(controls, "bias_min_frames", 0) ||
        g.kappa != real(controls, "bias_stack_kappa", NAN) ||
        real(controls, "bias_mean_min_adu", NAN) != 0 ||
        real(controls, "bias_mean_max_adu", NAN) != 1000) {
        goto done;
    }
    if (g.use_prescan != integer(c->processing.toptab, "use_prescan", -1) ||
        g.use_overscan != integer(c->processing.toptab, "use_overscan", -1) ||
        g.rejection[0] != integer(c->processing.toptab, "scan_reject_low", -1) ||
        g.rejection[1] != integer(c->processing.toptab, "scan_reject_high", -1)) {
        goto done;
    }
    for (int band = 0; band < 2; ++band) {
        int z[4];
        if (!rectangle(toml_get(trim, band ? "overscan_sample" : "prescan_sample"), z)) {
            goto done;
        }
        const int *wanted = band ? g.overscan : g.prescan;
        if (z[0] != wanted[0] || z[1] != wanted[1]) {
            goto done;
        }
    }
    if (!regions(c, dir, id, amplifier, toml_get(row, "reference_rois"), toml_get(row, "sites"),
            &roi, &sites, &reference)) {
        goto done;
    }
    plan = control(c, dir, "plan.tsv", &plan_path);
    bias = control(c, dir, "biases.tsv", &bias_path);
    flat = control(c, dir, "flats.tsv", &flat_path);
    if (!plan || !bias || !flat) {
        goto done;
    }
    fprintf(plan, "detector\t%s\namplifier\t%s\nslot\t%ld\nreadout\t%s\n", id, amplifier, slot,
        readout);
    const char *identity_keys[] = {
        "identity_key", "amplifier_key", "bin_x_key", "bin_y_key", "exposure_key"};
    const char *defaults[] = {
        "EXTNAME", "-", "HIERARCH ESO DET WIN1 BINX", "HIERARCH ESO DET WIN1 BINY", "EXPTIME"};
    for (int i = 0; i < 4; ++i) {
        fprintf(plan, "%s\t%s\n", identity_keys[i],
            string(identity, identity_keys[i]) ? string(identity, identity_keys[i]) : defaults[i]);
    }
    fprintf(plan,
        "bin_x\t1\nbin_y\t1\nmask_encoding\t%s\ngood_value\t%ld\nmask_registry\t%s\nreject_bits\t%"
        "ld\n",
        supplied ? encoding : "omitted", good, !strcmp(encoding, "reason8") ? "WENU_BPM_V1" : "-",
        reject);
    fprintf(plan,
        "saturation\t%.17g\ntolerance\t%.17g\nmax_pixels\t%ld\nmax_rows\t%ld\nexposure_key\t%"
        "s\nexposure_hdu\t%ld\nwith_mad\t%d\nschema\traw-pair-plan-v1\ncrop\t%d,%d,%d,%d\nraw_"
        "width\t%d\nraw_height\t%d\n",
        saturation, tolerance, pixels, rows,
        string(identity, "exposure_key") ? string(identity, "exposure_key") : "EXPTIME",
        integer(identity, "exposure_hdu", 0), mad.u.boolean, crop[0], crop[1], crop[2], crop[3],
        raw[0], raw[1]);
    for (int i = 0; i < flats.u.arr.size; ++i) {
        toml_datum_t item = flats.u.arr.elem[i];
        if (!fields(item, "|path|pair|input_index|asset|")) {
            goto done;
        }
        char *input = path(c->raw, string(item, "path"));
        long pair = integer(item, "pair", -1);
        if (!input || pair < 0 || pair > 63 || !mef_bpm_linearity_below(input, c->raw) ||
            !freeze(c, input)) {
            free(input);
            goto done;
        }
        long ihdu = input_hdu(row, "flat_hdus", i, hdu), index = integer(item, "input_index", i);
        const char *asset = string(item, "asset");
        if (!asset) {
            asset = strrchr(input, '/') + 1;
        }
        if (ihdu < 0 || index < 0 || strlen(asset) > 127) {
            free(input);
            goto done;
        }
        fprintf(plan, "flat\t%s\t%ld\t%s\t%ld\tpair-%03ld\n", input, ihdu, asset, index, pair);
        fprintf(flat, "%s\t%ld\t%ld\n", input, ihdu, pair);
        free(input);
    }
    fputs("input_index\thdu\tasset\tpath\taccepted\n", bias);
    for (int i = 0; i < biases.u.arr.size; ++i) {
        toml_datum_t item = biases.u.arr.elem[i], yes = accepted.u.arr.elem[i];
        char *input = item.type == TOML_STRING ? path(c->raw, item.u.s) : NULL;
        if (!input || yes.type != TOML_BOOLEAN || !mef_bpm_linearity_below(input, c->raw) ||
            !freeze(c, input)) {
            free(input);
            goto done;
        }
        long ihdu = input_hdu(row, "bias_hdus", i, hdu);
        const char *asset = strrchr(input, '/') + 1;
        if (ihdu < 0) {
            free(input);
            goto done;
        }
        fprintf(bias, "%d\t%ld\t%s\t%s\t%d\n", i, ihdu, asset, input, yes.u.boolean);
        if (i < 2) {
            fprintf(plan, "bias\t%s\t%ld\t%s\n", input, ihdu, asset);
        }
        free(input);
    }
    if (supplied) {
        fprintf(plan, "bpm\t%s\t%ld\tinput-bpm\n", bpm, bhdu);
    }
    if (!finish_file(c, plan, plan_path)) {
        plan = NULL;
        goto done;
    }
    plan = NULL;
    if (!finish_file(c, bias, bias_path)) {
        bias = NULL;
        goto done;
    }
    bias = NULL;
    if (!finish_file(c, flat, flat_path)) {
        flat = NULL;
        goto done;
    }
    flat = NULL;
    f = control(c, dir, "context.json", &context);
    if (!f) {
        goto done;
    }
    fputs("{\"native_recipe_schema_version\":2,\"recipe\":", f);
    quoted(f, c->source);
    fputs(",\"source_revision\":", f);
    quoted(f, c->revision);
    fputs(",\"detector\":", f);
    quoted(f, id);
    fputs(",\"master_sha256\":", f);
    quoted(f, master_digest);
    fprintf(f, ",\"qc_requested\":%s", c->qc ? "true" : "false");
    fputs(",\"raw_root\":", f);
    quoted(f, c->raw);
    fputs(",\"calibration_root\":", f);
    quoted(f, c->calibration);
    toml_datum_t prep = toml_get(c->recipe.toptab, "preparation");
    char *geometry_source = path(c->orchestration, string(prep, "detector_toml"));
    char *processing_source = path(c->orchestration, string(prep, "processing_toml"));
    int complete = context_text(f, "recipe_source", c->source) &&
                   context_text(f, "detector_profile", geometry_source) &&
                   context_text(f, "processing_profile", processing_source) &&
                   context_text(f, "effective_settings_toml", native);
    free(geometry_source);
    free(processing_source);
    if (!complete) {
        goto done;
    }
    fputs(",\"input_sha256\":{", f);
    for (size_t input = 0; input < c->count; ++input) {
        if (input) {
            fputc(',', f);
        }
        quoted(f, c->files[input].path);
        fputc(':', f);
        quoted(f, c->files[input].digest);
    }
    fputs(
        "},\"historical_comparison\":\"not_requested\",\"linearity_correction\":\"not_applied\"}\n",
        f);
    if (!finish_file(c, f, context)) {
        f = NULL;
        goto done;
    }
    f = NULL;
    prepared = format("%s/linearity/linearity-preparation.asdf", product);
    fits = format("%s/bpm/CMDP.${START}.001.fits", product);
    sidecar = format("%s/bpm/CMDP.${START}.001.asdf", product);
    log = format("%s/bpm/CMDP.${START}.001.log", product);
    if (!prepared || !fits || !sidecar || !log) {
        goto done;
    }
    fprintf(c->bindings, "\n[[detectors]]\ndetector_id = ");
    quoted(c->bindings, id);
    fprintf(c->bindings, "\nconfiguration_detector = %ld\nfits = ", slot);
    quoted(c->bindings, fits);
    fputs("\nasdf = ", c->bindings);
    quoted(c->bindings, sidecar);
    fputs("\nprepared = ", c->bindings);
    quoted(c->bindings, prepared);
    fputs("\npreparation = [", c->bindings);
    n = 0;
    argument(c->bindings, &n, "mefpp_linearity_prepare_command");
    argument(c->bindings, &n, native);
    argument(c->bindings, &n, roi);
    argument(c->bindings, &n, sites);
    argument(c->bindings, &n, plan_path);
    argument(c->bindings, &n, master);
    snprintf(number, sizeof(number), "%ld", mhdu);
    argument(c->bindings, &n, number);
    argument(c->bindings, &n, "master-bias");
    argument(c->bindings, &n, bias_path);
    char *native_work = format("%s/linearity", work),
         *runlog = format("%s/CMDP.${START}.001.log", c->output);
    argument(c->bindings, &n, native_work);
    argument(c->bindings, &n, "--native-asdf");
    argument(c->bindings, &n, prepared);
    argument(c->bindings, &n, "${START}");
    argument(c->bindings, &n, runlog);
    argument(c->bindings, &n, "--context");
    argument(c->bindings, &n, context);
    fputs("]\nbpm = [", c->bindings);
    n = 0;
    argument(c->bindings, &n, "mefpp_m5");
    argument(c->bindings, &n, "cal");
    argument(c->bindings, &n, "bpm");
    option(c->bindings, &n, "--config", native);
    option(c->bindings, &n, "--flats", flat_path);
    option(c->bindings, &n, "--detector-id", id);
    snprintf(number, sizeof(number), "%ld", slot);
    option(c->bindings, &n, "--config-detector", number);
    option(c->bindings, &n, "--readout-id", readout);
    option(c->bindings, &n, "--bin-x", "1");
    option(c->bindings, &n, "--bin-y", "1");
    option(c->bindings, &n, "--master-bias", master);
    snprintf(number, sizeof(number), "%ld", mhdu);
    option(c->bindings, &n, "--bias-hdu", number);
    option(c->bindings, &n, "--input-bpm", bpm);
    option(c->bindings, &n, "--bpm-encoding", supplied ? encoding : "omitted");
    snprintf(number, sizeof(number), "%ld", reject);
    option(c->bindings, &n, "--reject-bits", number);
    option(c->bindings, &n, "--acquisition", acquisition);
    option(c->bindings, &n, "--exposure-key",
        string(identity, "exposure_key") ? string(identity, "exposure_key") : "EXPTIME");
    snprintf(number, sizeof(number), "%ld", integer(identity, "exposure_hdu", 0));
    option(c->bindings, &n, "--exposure-hdu", number);
    snprintf(number, sizeof(number), "%.17g", saturation);
    option(c->bindings, &n, "--saturation", number);
    const char *pkeys[] = {"upper_fraction", "minimum_span_fraction", "maximum_pair_difference"};
    const char *poptions[] = {"--upper-fraction", "--minimum-span", "--maximum-pair-difference"};
    for (int i = 0; i < 3; ++i) {
        snprintf(number, sizeof(number), "%.17g", real(policy, pkeys[i], NAN));
        option(c->bindings, &n, poptions[i], number);
    }
    option(c->bindings, &n, "--roi-file", reference);
    option(c->bindings, &n, "--mad", mad.u.boolean ? "yes" : "no");
    option(c->bindings, &n, "--output-mode", mode);
    option(c->bindings, &n, "--created-at", "${START_SECONDS}");
    option(c->bindings, &n, "--output", fits);
    option(c->bindings, &n, "--native-asdf", sidecar);
    char *bpm_work = format("%s/bpm", work), *record = format("%s/bpm/configuration.json", work);
    option(c->bindings, &n, "--work-dir", bpm_work);
    option(c->bindings, &n, "--log-path", log);
    option(c->bindings, &n, "--config-record", record);
    if (supplied) {
        snprintf(number, sizeof(number), "%ld", bhdu);
        option(c->bindings, &n, "--bpm-hdu", number);
        option(c->bindings, &n, "--bpm-coordinates", "active");
    }
    if (supplied && !strcmp(encoding, "binary")) {
        snprintf(number, sizeof(number), "%ld", good);
        option(c->bindings, &n, "--bpm-good-value", number);
    } else if (supplied && !strcmp(encoding, "reason8")) {
        option(c->bindings, &n, "--bpm-registry", "WENU_BPM_V1");
    }
    fputs("]\n", c->bindings);
    /* The begin phase creates these fresh directories, after full admission. */
    fprintf(c->bindings, "# directories are declared in the top-level transport\n");
    free(native_work);
    free(runlog);
    free(bpm_work);
    free(record);
    okay = !ferror(c->bindings);
done:
    if (f) {
        fclose(f);
    }
    if (plan) {
        fclose(plan);
    }
    if (bias) {
        fclose(bias);
    }
    if (flat) {
        fclose(flat);
    }
    mef_config_destroy(configuration);
    free(dir);
    free(plan_path);
    free(bias_path);
    free(flat_path);
    free(native);
    free(context);
    free(roi);
    free(sites);
    free(reference);
    free(master);
    free(bpm);
    free(work);
    free(product);
    free(prepared);
    free(fits);
    free(sidecar);
    free(log);
    return okay;
}

int mef_bpm_linearity_compile(const char *source, const char *revision, int qc_override, char **out,
    mef_bpm_linearity_frozen **frozen, size_t *frozen_count, char *diagnostic, size_t capacity)
{
    compilation c = {0};
    char *project = NULL, *geometry = NULL, *processing = NULL, *settings = NULL, *binding = NULL;
    char *slash;
    FILE *body = NULL;
    char *body_text = NULL;
    size_t body_size = 0;
    int okay = 0;
    c.source = source;
    c.revision = revision;
    c.files = calloc(MAX_FILES, sizeof(*c.files));
    if (!c.files) {
        goto done;
    }
    c.recipe = document(&c, source);
    if (!c.recipe.ok) {
        goto done;
    }
    if (integer(c.recipe.toptab, "bpm_linearity_recipe_schema_version", 0) != 2 ||
        !fields(c.recipe.toptab, "|bpm_linearity_recipe_schema_version|project|settings|run|qc|"
                                 "assembly|preparation|bpm|inputs|identity|detectors|")) {
        goto done;
    }
    if (!fields(toml_get(c.recipe.toptab, "bpm"),
            "|acquisition|output_mode|upper_fraction|minimum_span_fraction|maximum_pair_difference|"
            "response_low|response_high|") ||
        !fields(toml_get(c.recipe.toptab, "inputs"), "|flat|bias|") ||
        !fields(toml_get(c.recipe.toptab, "preparation"), "|detector_toml|processing_toml|") ||
        !fields(toml_get(c.recipe.toptab, "assembly"), "|reference_detector|")) {
        goto done;
    }
    toml_datum_t identity = toml_get(c.recipe.toptab, "identity");
    if (identity.type != TOML_UNKNOWN) {
        if (!fields(identity,
                "|identity_key|amplifier_key|bin_x_key|bin_y_key|exposure_key|exposure_hdu|")) {
            goto done;
        }
        for (int i = 0; i < identity.u.tab.size; ++i) {
            const char *key = identity.u.tab.key[i];
            toml_datum_t value = toml_get(identity, key);
            if (!strcmp(key, "exposure_hdu")) {
                if (value.type != TOML_INT64 || value.u.int64 < 0 || value.u.int64 > 127) {
                    goto done;
                }
            } else if (!string(identity, key)) {
                goto done;
            }
        }
    }
    c.orchestration = strdup(source);
    if (!c.orchestration) {
        goto done;
    }
    slash = strrchr(c.orchestration, '/');
    *slash = 0;
    project = path(c.orchestration, string(c.recipe.toptab, "project"));
    char *origin = NULL;
    if (!project || !mef_bpm_linearity_project(project, &c.project, &origin, project_freeze, &c)) {
        goto done;
    }
    toml_datum_t roots = toml_get(toml_get(c.project.toptab, "project"), "roots");
    /* Project roots are relative to the document defining the project domain. */
    char *project_base = origin;
    *strrchr(project_base, '/') = 0;
    c.raw = path(project_base, string(roots, "raw"));
    c.calibration = path(project_base, string(roots, "calibration"));
    char *reduced = path(project_base, string(roots, "output"));
    c.work = path(project_base, string(roots, "work"));
    c.logs = path(project_base, string(roots, "logs"));
    free(project_base);
    const char *run = string(c.recipe.toptab, "run");
    if (!c.raw || !c.calibration || !reduced || !c.work || !c.logs || !run || run[0] == '/' ||
        strstr(run, "..")) {
        free(reduced);
        goto done;
    }
    char invocation[4096];
    char *project_directory = strdup(project);
    if (!project_directory) {
        free(reduced);
        goto done;
    }
    *strrchr(project_directory, '/') = 0;
    int valid_roots =
        getcwd(invocation, sizeof(invocation)) && !strcmp(invocation, project_directory) &&
        mef_bpm_linearity_below(source, project_directory) &&
        mef_bpm_linearity_below(c.calibration, reduced) &&
        mef_bpm_linearity_below(c.work, reduced) && mef_bpm_linearity_below(c.logs, reduced) &&
        strcmp(c.raw, reduced) && strcmp(c.raw, project_directory) &&
        !mef_bpm_linearity_below(c.raw, reduced) && !mef_bpm_linearity_below(reduced, c.raw) &&
        !mef_bpm_linearity_below(project_directory, c.raw) &&
        !mef_bpm_linearity_below(project_directory, reduced);
    free(project_directory);
    if (!valid_roots) {
        free(reduced);
        goto done;
    }
    c.output = path(reduced, run);
    free(reduced);
    if (!c.output) {
        goto done;
    }
    const char *basename = strrchr(c.output, '/') + 1;
    c.controls = format("%s/%s", c.orchestration, basename);
    if (!c.controls || mkdir(c.controls, 0700)) {
        goto done;
    }
    toml_datum_t prep = toml_get(c.recipe.toptab, "preparation");
    geometry = path(c.orchestration, string(prep, "detector_toml"));
    processing = path(c.orchestration, string(prep, "processing_toml"));
    settings = path(c.orchestration, string(c.recipe.toptab, "settings"));
    c.geometry = document(&c, geometry);
    c.processing = document(&c, processing);
    if (!c.geometry.ok || !c.processing.ok || !settings || !settings_sources(&c, settings, 0)) {
        goto done;
    }
    const char *instrument = string(c.geometry.toptab, "instrument"),
               *processed = string(c.processing.toptab, "instrument");
    toml_datum_t binning = toml_get(c.geometry.toptab, "binning");
    if (!instrument || !processed || strcmp(instrument, processed) ||
        integer(c.geometry.toptab, "footprint_schema_version", 0) != 1 ||
        integer(c.processing.toptab, "linearity_preparation_schema_version", 0) != 1 ||
        binning.type != TOML_ARRAY || binning.u.arr.size != 2 ||
        binning.u.arr.elem[0].type != TOML_INT64 || binning.u.arr.elem[0].u.int64 != 1 ||
        binning.u.arr.elem[1].type != TOML_INT64 || binning.u.arr.elem[1].u.int64 != 1) {
        goto done;
    }
    toml_datum_t selected = toml_get(c.recipe.toptab, "detectors"),
                 qc = toml_get(c.recipe.toptab, "qc");
    if (selected.type != TOML_ARRAY || selected.u.arr.size < 1 || selected.u.arr.size > 4095 ||
        (qc.type != TOML_UNKNOWN && qc.type != TOML_BOOLEAN)) {
        goto done;
    }
    c.qc = qc_override >= 0 ? qc_override : qc.type == TOML_BOOLEAN ? qc.u.boolean : 1;
    body = open_memstream(&body_text, &body_size);
    if (!body) {
        goto done;
    }
    c.bindings = body;
    for (int i = 0; i < selected.u.arr.size; ++i) {
        if (!detector(&c, selected.u.arr.elem[i], (size_t)i, settings)) {
            goto done;
        }
    }
    if (fclose(body)) {
        body = NULL;
        goto done;
    }
    body = NULL;
    FILE *f = control(&c, c.controls, "native-bindings.toml", &binding);
    if (!f) {
        goto done;
    }
    fprintf(f, "bpm_linearity_bindings_schema_version = 1\nsource_revision = ");
    quoted(f, revision);
    fputs("\nrecipe = ", f);
    quoted(f, source);
    fputs("\ncopies = []\ndirectories = [", f);
    int count = 0;
    for (int i = 0; i < selected.u.arr.size; ++i) {
        char *work = format("%s/%s/detector-%03d", c.work, basename, i);
        char *product = format("%s/detector-%03d", c.output, i);
        char *dirs[] = {format("%s/bpm", work), format("%s/linearity", work),
            format("%s/bpm", product), format("%s/linearity", product)};
        for (int j = 0; j < 4; ++j) {
            argument(f, &count, dirs[j]);
            free(dirs[j]);
        }
        free(work);
        free(product);
    }
    fputs("]\n", f);
    for (size_t i = 0; i < c.count; ++i) {
        mef_bpm_linearity_dependency check = {
            .path = c.files[i].path, .sha256 = c.files[i].digest, .identity = c.files[i].identity};
        if (!mef_bpm_linearity_dependency_check(&check, 0)) {
            fclose(f);
            goto done;
        }
        fputs("\n[[dependencies]]\npath = ", f);
        quoted(f, c.files[i].path);
        fprintf(f, "\nsha256 = \"%s\"\n", c.files[i].digest);
    }
    if (fwrite(body_text, 1, body_size, f) != body_size || ferror(f)) {
        fclose(f);
        goto done;
    }
    if (fclose(f)) {
        goto done;
    }
    *out = binding;
    binding = NULL;
    *frozen = c.files;
    *frozen_count = c.count;
    c.files = NULL;
    c.count = 0;
    okay = 1;
done:
    if (!okay && diagnostic && capacity) {
        snprintf(diagnostic, capacity,
            "Native recipe admission failed; retain control evidence%s%s", c.controls ? ": " : "",
            c.controls ? c.controls : "");
    }
    if (body) {
        fclose(body);
    }
    for (size_t i = 0; i < c.count; ++i) {
        free(c.files[i].path);
    }
    free(c.files);
    free(c.controls);
    free(c.output);
    free(c.raw);
    free(c.calibration);
    free(c.work);
    free(c.logs);
    free(c.orchestration);
    free(project);
    free(geometry);
    free(processing);
    free(settings);
    free(binding);
    free(body_text);
    toml_free(c.recipe);
    toml_free(c.project);
    toml_free(c.geometry);
    toml_free(c.processing);
    return okay;
}
