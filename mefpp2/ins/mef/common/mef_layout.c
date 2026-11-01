/* M4 bounded file-layout discovery/binding, reusing qfits/Eclipse (#182). */
#include "mef_layout.h"
#include "image_io.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <float.h>
#include <limits.h>

struct mef_layout {
    mef_allocator allocator;
    char *path;
    struct stat identity;
    mef_hdu_layout *hdus;
    size_t count, capacity;
};
struct mef_layout_map {
    mef_allocator allocator;
    char *path;
    struct stat identity;
    mef_bound_detector *detectors;
    size_t count;
};
static void *standard_allocate(void *user, size_t n) { (void)user; return (malloc)(n); }
static void standard_release(void *user, void *p) { (void)user; (free)(p); }
static int allocator_for(const mef_allocator *source, mef_allocator *out)
{
    if (source == NULL) {
        out->user = NULL; out->allocate = standard_allocate; out->release = standard_release;
    } else {
        if (source->allocate == NULL || source->release == NULL) return 0;
        *out = *source;
    }
    return 1;
}
static void release(const mef_allocator *a, void *p) { if (p != NULL) a->release(a->user, p); }
static char *copy_path(const mef_allocator *a, const char *path)
{
    size_t n;
    char *p;
    n = strlen(path) + 1;
    p = a->allocate(a->user, n);
    if (p != NULL) memcpy(p, path, n);
    return p;
}
static mef_status failure(mef_status status, const char *detail,
    const mef_allocator *a, mef_error **error)
{
    if (error != NULL && *error == NULL) (void)mef_error_create(status, detail, a, error);
    return status;
}
static int text(const char *s) { return s != NULL && *s != '\0'; }
static int fixed(char *out, const char *s)
{
    if (s == NULL) { out[0] = '\0'; return 1; }
    if (strlen(s) >= MEF_LAYOUT_TEXT) return 0;
    strcpy(out, s); return 1;
}
static int same_identity(const struct stat *a, const struct stat *b)
{
    if (a->st_dev != b->st_dev || a->st_ino != b->st_ino || a->st_size != b->st_size ||
        a->st_mtime != b->st_mtime || a->st_ctime != b->st_ctime) return 0;
#ifdef __APPLE__
    return a->st_mtimespec.tv_nsec == b->st_mtimespec.tv_nsec &&
        a->st_ctimespec.tv_nsec == b->st_ctimespec.tv_nsec;
#else
    return a->st_mtim.tv_nsec == b->st_mtim.tv_nsec && a->st_ctim.tv_nsec == b->st_ctim.tv_nsec;
#endif
}
static int integer(const char *s, long *value)
{
    char *end;
    if (!text(s)) return 0;
    errno = 0; *value = strtol(s, &end, 10);
    while (*end == ' ') ++end;
    return errno == 0 && end != s && *end == '\0';
}
static int number(const char *s, double *value)
{
    char local[MEF_LAYOUT_TEXT], *end;
    size_t i;
    if (!text(s) || !fixed(local, s)) return 0;
    for (i = 0; local[i]; ++i) if (local[i] == 'D' || local[i] == 'd') local[i] = 'E';
    errno = 0; *value = strtod(local, &end);
    while (*end == ' ') ++end;
    return errno == 0 && end != local && *end == '\0' &&
        *value == *value && *value >= -DBL_MAX && *value <= DBL_MAX;
}
static int string_value(const char *s, char *out)
{
    size_t i, n;
    if (s == NULL || *s != '\'') return 0;
    n = 0;
    for (i = 1; s[i]; ++i) {
        if (s[i] == '\'') {
            if (s[i + 1] == '\'') ++i;
            else {
                ++i; while (s[i] == ' ') ++i;
                if (s[i] != '\0') return 0;
                while (n && out[n - 1] == ' ') --n;
                out[n] = '\0'; return 1;
            }
        }
        if (n + 1 >= MEF_LAYOUT_TEXT) return 0;
        out[n++] = s[i];
    }
    return 0;
}
static int multiply(size_t *value, size_t factor)
{
    if (factor != 0 && *value > (size_t)-1 / factor) return 0;
    *value *= factor; return 1;
}

/* qfits owns file framing/discovery and stored cards. This layer selects and
 * validates metadata, without interpreting FITS blocks or seeking over payloads. */
typedef struct {
    const char *keys[22];
    char values[22][MEF_LAYOUT_TEXT];
    unsigned long seen;
} selected_header;
static int select_card(const char *key, const char *value, const char *line, void *user)
{
    selected_header *selected;
    size_t j;
    (void)line; selected = user;
    for (j = 0; j < 22; ++j) if (selected->keys[j] != NULL && !strcmp(key, selected->keys[j])) {
        if (selected->seen & (1UL << j)) return -1;
        selected->seen |= 1UL << j;
        if (!fixed(selected->values[j], value) || !text(value)) return -1;
        break;
    }
    return 0;
}
static mef_status inspect_header(const qfits_header *header, const mef_layout_options *options,
    mef_hdu_layout *hdu, size_t *payload)
{
    selected_header selected;
    const char **keys;
    char (*values)[MEF_LAYOUT_TEXT], extension[81];
    unsigned long seen;
    size_t i, j, bytes, pixels, pcount, gcount;
    long n;
    memset(&selected, 0, sizeof(selected)); keys = selected.keys; values = selected.values;
    keys[0] = "SIMPLE"; keys[1] = "XTENSION"; keys[2] = "BITPIX"; keys[3] = "NAXIS";
    keys[4] = "NAXIS1"; keys[5] = "NAXIS2"; keys[6] = "NAXIS3";
    keys[7] = "PCOUNT"; keys[8] = "GCOUNT"; keys[9] = "GROUPS";
    keys[10] = "BSCALE"; keys[11] = "BZERO"; keys[12] = "EXTNAME";
    keys[13] = "EXTVER"; keys[14] = "BUNIT";
    keys[15] = options->identity_key; keys[16] = options->amplifier_key;
    keys[17] = options->bin_x_key ? options->bin_x_key : "XBINNING";
    keys[18] = options->bin_y_key ? options->bin_y_key : "YBINNING";
    keys[19] = "DATASEC"; keys[20] = "DETSEC"; keys[21] = "CCDSEC";
    for (i = 0; i < 22; ++i) if (keys[i] != NULL) {
        if (!text(keys[i]) || strlen(keys[i]) > 80) return MEF_ERR_INPUT;
        for (j = 0; j < i; ++j) if (keys[j] != NULL && !strcmp(keys[i], keys[j])) return MEF_ERR_INPUT;
    }
    if (qfits_header_visit(header, select_card, &selected) != 0) return MEF_ERR_INPUT;
    seen = selected.seen;
    if (hdu->hdu_index == 0) {
        if (strcmp(values[0], "T") || (seen & (1UL << 1))) return MEF_ERR_INPUT;
        hdu->kind = MEF_HDU_IMAGE;
    } else {
        if (!string_value(values[1], extension)) return MEF_ERR_INPUT;
        if (!strcmp(extension, "IMAGE")) hdu->kind = MEF_HDU_IMAGE;
        else if (!strcmp(extension, "BINTABLE") || !strcmp(extension, "TABLE")) hdu->kind = MEF_HDU_TABLE;
        else return MEF_ERR_UNSUPPORTED;
        if (!(seen & (1UL << 7)) || !(seen & (1UL << 8))) return MEF_ERR_INPUT;
    }
    if ((seen & (1UL << 9)) && strcmp(values[9], "F")) return MEF_ERR_UNSUPPORTED;
    if (!integer(values[2], &n) || (n != 8 && n != 16 && n != 32 && n != 64 && n != -32 && n != -64)) return MEF_ERR_INPUT;
    hdu->bitpix = (int)n;
    if (!integer(values[3], &n) || n < 0 || n > 3) return MEF_ERR_UNSUPPORTED;
    hdu->naxis = (int)n; pixels = n == 0 ? 0 : 1;
    for (i = 0; i < 3; ++i) {
        if ((int)i < hdu->naxis) {
            if (!integer(values[4 + i], &n) || n < 0 || (unsigned long)n > (size_t)-1) return MEF_ERR_INPUT;
            hdu->axes[i] = (size_t)n;
            if (!multiply(&pixels, (size_t)n)) return MEF_ERR_INPUT;
        } else if (seen & (1UL << (4 + i))) return MEF_ERR_INPUT;
    }
    pcount = 0; gcount = 1;
    if (seen & (1UL << 7)) { if (!integer(values[7], &n) || n < 0) return MEF_ERR_INPUT; pcount = (size_t)n; }
    if (seen & (1UL << 8)) { if (!integer(values[8], &n) || n < 1) return MEF_ERR_INPUT; gcount = (size_t)n; }
    if (hdu->kind == MEF_HDU_IMAGE && (pcount != 0 || gcount != 1)) return MEF_ERR_UNSUPPORTED;
    if (hdu->naxis == 0 && hdu->kind == MEF_HDU_IMAGE) hdu->kind = MEF_HDU_EMPTY;
    if (pixels > (size_t)-1 - pcount) return MEF_ERR_INPUT;
    bytes = pixels + pcount;
    if (!multiply(&bytes, gcount) || !multiply(&bytes, (size_t)(abs(hdu->bitpix) / 8))) return MEF_ERR_INPUT;
    if (bytes > (size_t)-1 - 2879) return MEF_ERR_INPUT;
    *payload = ((bytes + 2879) / 2880) * 2880;
    hdu->bscale = 1.0; hdu->bzero = 0.0;
    hdu->has_bscale = !!(seen & (1UL << 10)); hdu->has_bzero = !!(seen & (1UL << 11));
    if (hdu->has_bscale && (!number(values[10], &hdu->bscale) || hdu->bscale == 0.0)) return MEF_ERR_INPUT;
    if (hdu->has_bzero && !number(values[11], &hdu->bzero)) return MEF_ERR_INPUT;
    hdu->has_extname = !!(seen & (1UL << 12)); hdu->has_extver = !!(seen & (1UL << 13));
    if (hdu->has_extname && (!string_value(values[12], hdu->extname) || !text(hdu->extname))) return MEF_ERR_INPUT;
    if (hdu->has_extver) { if (!integer(values[13], &n) || n < 1 || n > INT_MAX) return MEF_ERR_INPUT; hdu->extver = (int)n; }
    if ((seen & (1UL << 14)) && !string_value(values[14], hdu->bunit)) return MEF_ERR_INPUT;
    if ((seen & (1UL << 15)) && !string_value(values[15], hdu->reported_id)) return MEF_ERR_INPUT;
    if ((seen & (1UL << 16)) && !string_value(values[16], hdu->amplifier)) return MEF_ERR_INPUT;
    hdu->has_bin_x = !!(seen & (1UL << 17)); hdu->has_bin_y = !!(seen & (1UL << 18));
    if (hdu->has_bin_x) { if (!integer(values[17], &n) || n < 1 || n > INT_MAX) return MEF_ERR_INPUT; hdu->bin_x = (int)n; }
    if (hdu->has_bin_y) { if (!integer(values[18], &n) || n < 1 || n > INT_MAX) return MEF_ERR_INPUT; hdu->bin_y = (int)n; }
    if ((seen & (1UL << 19)) && !string_value(values[19], hdu->datasec)) return MEF_ERR_INPUT;
    if ((seen & (1UL << 20)) && !string_value(values[20], hdu->detsec)) return MEF_ERR_INPUT;
    if ((seen & (1UL << 21)) && !string_value(values[21], hdu->ccdsec)) return MEF_ERR_INPUT;
    return MEF_OK;
}

void mef_layout_destroy(mef_layout *layout)
{
    mef_allocator a;
    if (layout == NULL) return;
    a = layout->allocator; release(&a, layout->hdus); release(&a, layout->path); release(&a, layout);
}
mef_status mef_layout_read(const char *path, const mef_layout_options *options,
    const mef_allocator *allocator, mef_layout **out, mef_error **error)
{
    mef_layout_options defaults;
    mef_layout *layout;
    mef_allocator a;
    qfits_header *header;
    struct stat after;
    mef_hdu_layout hdu, *grown;
    mef_status status;
    size_t payload, capacity;
    int nextensions, index;
    off_t header_start, header_size, data_start, data_size;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (!allocator_for(allocator, &a)) return MEF_ERR_INPUT;
    if (path == NULL || path[0] != '/') return failure(MEF_ERR_INPUT, "Layout requires an absolute input path", &a, error);
    memset(&defaults, 0, sizeof(defaults)); defaults.max_hdus = 4096; defaults.max_header_bytes = 16 * 1024 * 1024;
    if (options == NULL) options = &defaults;
    if (options->max_hdus == 0 || options->max_hdus > INT_MAX || options->max_header_bytes < 2880 ||
        options->max_hdus > (size_t)-1 / sizeof(hdu)) return failure(MEF_ERR_INPUT, "Invalid layout limits", &a, error);
    layout = a.allocate(a.user, sizeof(*layout));
    if (layout == NULL) return failure(MEF_ERR_MEMORY, "Cannot allocate layout", &a, error);
    memset(layout, 0, sizeof(*layout)); layout->allocator = a;
    layout->path = copy_path(&a, path); header = NULL; status = MEF_ERR_MEMORY;
    if (layout->path == NULL) goto failed;
    status = MEF_ERR_IO;
    /* #185: reject nonregular inputs before the dependency opens them. */
    if (stat(path, &layout->identity) != 0 || !S_ISREG(layout->identity.st_mode) ||
        layout->identity.st_size <= 0) goto failed;
    /* Additive checked entry point shares the existing qfits cache walker.
     * It enforces HDU/header budgets before publishing an offset catalogue. */
    status = MEF_ERR_INPUT;
    if (qfits_cache_prime_bounded(layout->path, options->max_hdus, options->max_header_bytes) != 0) goto failed;
    nextensions = qfits_query_n_ext(layout->path);
    if (nextensions < 0 || (size_t)nextensions >= options->max_hdus) goto failed;
    for (index = 0; index <= nextensions; ++index) {
        if (qfits_get_hdrinfo_wide(layout->path, index, &header_start, &header_size) != 0 ||
            qfits_get_datinfo_wide(layout->path, index, &data_start, &data_size) != 0 ||
            header_start < 0 || header_size < 2880 || data_start < 0 || data_size < 0) goto failed;
        header = qfits_header_readext(layout->path, index);
        if (header == NULL) { status = MEF_ERR_IO; goto failed; }
        memset(&hdu, 0, sizeof(hdu)); hdu.hdu_index = index;
        status = inspect_header(header, options, &hdu, &payload);
        qfits_header_destroy(header); header = NULL;
        if (status != MEF_OK) goto failed;
        /* Validate the dependency's reported storage span against metadata. */
        if (payload != (size_t)data_size ||
            data_start > layout->identity.st_size ||
            payload > (size_t)(layout->identity.st_size - data_start)) { status = MEF_ERR_IO; goto failed; }
        if (layout->count == layout->capacity) {
            capacity = layout->capacity ? layout->capacity * 2 : 4;
            if (capacity > options->max_hdus) capacity = options->max_hdus;
            grown = a.allocate(a.user, capacity * sizeof(*grown));
            if (grown == NULL) { status = MEF_ERR_MEMORY; goto failed; }
            if (layout->count) memcpy(grown, layout->hdus, layout->count * sizeof(*grown));
            release(&a, layout->hdus); layout->hdus = grown; layout->capacity = capacity;
        }
        layout->hdus[layout->count++] = hdu;
    }
    if (!layout->count || stat(path, &after) != 0 || !same_identity(&layout->identity, &after)) { status = MEF_ERR_IO; goto failed; }
    *out = layout; return MEF_OK;
failed:
    if (header != NULL) qfits_header_destroy(header);
    mef_layout_destroy(layout);
    return failure(status, "Cannot discover bounded FITS layout (required card, limit, I/O or allocation)", &a, error);
}
const mef_hdu_layout *mef_layout_hdus(const mef_layout *layout, size_t *count)
{
    if (count != NULL) *count = layout ? layout->count : 0;
    return layout ? layout->hdus : NULL;
}
const char *mef_layout_path(const mef_layout *layout) { return layout ? layout->path : NULL; }

void mef_layout_map_destroy(mef_layout_map *map)
{
    mef_allocator a;
    if (map == NULL) return;
    a = map->allocator; release(&a, map->detectors); release(&a, map->path); release(&a, map);
}
static int ordered(const void *left, const void *right)
{
    const mef_bound_detector *a, *b;
    a = left; b = right;
    return (a->image.hdu_index > b->image.hdu_index) - (a->image.hdu_index < b->image.hdu_index);
}
mef_status mef_layout_bind(const mef_layout *layout,
    const mef_detector_binding *bindings, size_t count,
    const mef_allocator *allocator, mef_layout_map **out, mef_error **error)
{
    mef_allocator a;
    mef_layout_map *map;
    const mef_detector_binding *b;
    const mef_hdu_layout *h;
    mef_bound_detector *d;
    size_t i, j, matches;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    if (!allocator_for(allocator, &a)) return MEF_ERR_INPUT;
    if (layout == NULL || bindings == NULL || !count || count > layout->count || count > (size_t)-1 / sizeof(*d))
        return failure(MEF_ERR_INPUT, "Invalid detector mapping", &a, error);
    map = a.allocate(a.user, sizeof(*map));
    if (map == NULL) return failure(MEF_ERR_MEMORY, "Cannot allocate detector map", &a, error);
    memset(map, 0, sizeof(*map)); map->allocator = a; map->identity = layout->identity;
    map->path = copy_path(&a, layout->path); map->detectors = a.allocate(a.user, count * sizeof(*d));
    if (map->path == NULL || map->detectors == NULL) {
        mef_layout_map_destroy(map); return failure(MEF_ERR_MEMORY, "Cannot copy detector map", &a, error);
    }
    memset(map->detectors, 0, count * sizeof(*d)); map->count = count;
    for (i = 0; i < count; ++i) {
        b = bindings + i; d = map->detectors + i; h = NULL; matches = 0;
        if (!text(b->detector_id) || b->hdu_index < -1 || b->bin_x < 1 || b->bin_y < 1 ||
            !text(b->readout_id) || (b->health != MEF_HEALTH_UNKNOWN && b->health != MEF_HEALTH_GOOD && b->health != MEF_HEALTH_BAD) ||
            (b->selection != MEF_OUTPUT_SELECTED && b->selection != MEF_OUTPUT_EXCLUDED) ||
            (b->has_extver != 0 && b->has_extver != 1) || (b->has_extver && b->extver < 1) ||
            (b->hdu_index == -1 && !text(b->expected_header_id))) goto invalid;
        for (j = 0; j < layout->count; ++j) {
            if (b->hdu_index >= 0) {
                if ((size_t)b->hdu_index != j) continue;
            } else if (strcmp(b->expected_header_id, layout->hdus[j].reported_id)) continue;
            h = layout->hdus + j; ++matches;
        }
        if (matches != 1 || h == NULL || h->kind != MEF_HDU_IMAGE || h->naxis != 2 ||
            !h->axes[0] || !h->axes[1] || h->axes[0] > INT_MAX || h->axes[1] > INT_MAX ||
            h->axes[0] > (size_t)INT_MAX / h->axes[1] ||
            (text(b->expected_header_id) && strcmp(b->expected_header_id, h->reported_id)) ||
            (b->extname != NULL && (!h->has_extname || strcmp(b->extname, h->extname))) ||
            (b->has_extver && (!h->has_extver || b->extver != h->extver)) ||
            b->active_x < 1 || b->active_y < 1 || b->active_width < 1 || b->active_height < 1 ||
            (size_t)b->active_x > h->axes[0] || (size_t)b->active_y > h->axes[1] ||
            (size_t)b->active_width > h->axes[0] - (size_t)b->active_x + 1 ||
            (size_t)b->active_height > h->axes[1] - (size_t)b->active_y + 1 ||
            (h->has_bin_x && b->bin_x != h->bin_x) || (h->has_bin_y && b->bin_y != h->bin_y) ||
            (text(b->unit) && text(h->bunit) && strcmp(b->unit, h->bunit))) goto invalid;
        d->image = *h; d->identity_header_matched = text(b->expected_header_id);
        d->unit_from_header = text(h->bunit);
        if (!fixed(d->detector_id, b->detector_id) || !fixed(d->physical_id, b->physical_id) ||
            !fixed(d->unit, text(h->bunit) ? h->bunit : b->unit) || !fixed(d->readout_id, b->readout_id)) goto invalid;
        d->bin_x = b->bin_x; d->bin_y = b->bin_y; d->configuration_detector = b->configuration_detector;
        d->active_x = b->active_x; d->active_y = b->active_y;
        d->active_width = b->active_width; d->active_height = b->active_height;
        d->health = b->health; d->selection = b->selection;
        for (j = 0; j < i; ++j) if (!strcmp(d->detector_id, map->detectors[j].detector_id) ||
            d->image.hdu_index == map->detectors[j].image.hdu_index ||
            (text(d->image.reported_id) && !strcmp(d->image.reported_id, map->detectors[j].image.reported_id))) goto invalid;
    }
    qsort(map->detectors, count, sizeof(*d), ordered);
    *out = map; return MEF_OK;
invalid:
    mef_layout_map_destroy(map);
    return failure(MEF_ERR_INPUT, "Missing, ambiguous or inconsistent detector/selector/geometry/unit mapping", &a, error);
}
const mef_bound_detector *mef_layout_map_view(const mef_layout_map *map, size_t *count)
{
    if (count != NULL) *count = map ? map->count : 0;
    return map ? map->detectors : NULL;
}
const mef_bound_detector *mef_layout_find(const mef_layout_map *map, const char *id)
{
    size_t i;
    if (map == NULL || !text(id)) return NULL;
    for (i = 0; i < map->count; ++i) if (!strcmp(id, map->detectors[i].detector_id)) return map->detectors + i;
    return NULL;
}
mef_status mef_layout_compatible(const mef_layout_map *science,
    const mef_layout_map *calibration, const char *science_unit,
    const char *calibration_unit, const char *normalization_reference, mef_error **error)
{
    const mef_bound_detector *s, *c;
    size_t i;
    if (error != NULL && *error != NULL) return MEF_ERR_INPUT;
    if (science == NULL || calibration == NULL || !text(science_unit) || !text(calibration_unit))
        return failure(MEF_ERR_INPUT, "Compatibility needs explicit maps and units", NULL, error);
    if (normalization_reference != NULL && mef_layout_find(science, normalization_reference) == NULL)
        return failure(MEF_ERR_INPUT, "Required normalization reference is unavailable", &science->allocator, error);
    for (i = 0; i < science->count; ++i) {
        s = science->detectors + i;
        if (s->selection == MEF_OUTPUT_EXCLUDED &&
            (normalization_reference == NULL || strcmp(s->detector_id, normalization_reference))) continue;
        c = mef_layout_find(calibration, s->detector_id);
        if (c == NULL || strcmp(s->unit, science_unit) || strcmp(c->unit, calibration_unit) ||
            (text(s->physical_id) && text(c->physical_id) && strcmp(s->physical_id, c->physical_id)) ||
            (text(s->image.amplifier) && text(c->image.amplifier) && strcmp(s->image.amplifier, c->image.amplifier)) ||
            strcmp(s->readout_id, c->readout_id) || s->bin_x != c->bin_x || s->bin_y != c->bin_y ||
            s->active_width != c->active_width || s->active_height != c->active_height)
            return failure(MEF_ERR_INPUT, "Selected detector/reference has incompatible calibration", &science->allocator, error);
    }
    return MEF_OK;
}
mef_status mef_layout_load(const mef_layout_map *map, const char *detector_id,
    image_t **out, mef_error **error)
{
    struct stat before, after;
    const mef_bound_detector *d;
    image_t *image;
    if (out == NULL || *out != NULL || (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    d = mef_layout_find(map, detector_id);
    if (d == NULL) return failure(MEF_ERR_INPUT, "Unknown detector for plane load", NULL, error);
    if (d->image.bitpix == 64) return failure(MEF_ERR_UNSUPPORTED, "Existing pixel loader does not support BITPIX64", &map->allocator, error);
    if (stat(map->path, &before) != 0 || !same_identity(&map->identity, &before))
        return failure(MEF_ERR_IO, "Input changed since layout discovery", &map->allocator, error);
    image = image_loadext(map->path, d->image.hdu_index, 0, 1);
    if (image == NULL) return failure(MEF_ERR_IO, "Existing plane loader failed", &map->allocator, error);
    if (image->lx != (int)d->image.axes[0] || image->ly != (int)d->image.axes[1] ||
        stat(map->path, &after) != 0 || !same_identity(&before, &after)) {
        image_del(image); return failure(MEF_ERR_IO, "Loaded plane/source disagrees with layout", &map->allocator, error);
    }
    *out = image; return MEF_OK;
}
