#define _POSIX_C_SOURCE 200809L
#include "mef_mef_assemble.h"
#include "qfits.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <sys/stat.h>

_Static_assert(sizeof(off_t) >= 8 && sizeof(long) >= 8 && CHAR_BIT == 8,
    "MEF assembly requires the qualified LP64 wide-I/O representation");

typedef struct {
    struct stat identity;
    off_t data_start, data_size;
} source_span;

static int fail(char *message, size_t size, const char *text)
{
    if (message != NULL && size != 0) snprintf(message, size, "%s", text);
    return -1;
}
static int same_file(const struct stat *a, const struct stat *b)
{
    return a->st_dev == b->st_dev && a->st_ino == b->st_ino &&
        a->st_size == b->st_size && a->st_mtime == b->st_mtime;
}
static int header_string(qfits_header *h, const char *key, const char *expected)
{
    char *value = qfits_header_getstr(h, key);
    return value != NULL && !strcmp(qfits_pretty_string(value), expected);
}
static int bit_width(int bitpix)
{
    switch (bitpix) {
    case 8: return 1;
    case 16: return 2;
    case 32: case -32: return 4;
    case 64: case -64: return 8;
    default: return 0;
    }
}
static int inspect(const mef_assembly_detector *d, source_span *span)
{
    qfits_header *primary = NULL, *extension = NULL;
    off_t header_start, header_size, primary_size;
    uint64_t bytes, padded;
    int okay = 0, width = bit_width(d->bitpix);
    if (lstat(d->path, &span->identity) || !S_ISREG(span->identity.st_mode) ||
        span->identity.st_size <= 0 || span->identity.st_size % 2880 ||
        qfits_cache_prime_bounded((char *)d->path, 3, 1048576) ||
        qfits_query_n_ext((char *)d->path) != 1) goto done;
    primary = qfits_header_read((char *)d->path);
    extension = qfits_header_readext((char *)d->path, 1);
    if (primary == NULL || extension == NULL ||
        !header_string(primary, "SIMPLE", "T") ||
        qfits_header_getint(primary, "NAXIS", -1) != 0 ||
        !header_string(extension, "XTENSION", "IMAGE") ||
        !header_string(extension, "EXTNAME", d->detector_id) ||
        qfits_header_getint(extension, "NAXIS", -1) != 2 ||
        qfits_header_getint(extension, "NAXIS1", -1) != d->width ||
        qfits_header_getint(extension, "NAXIS2", -1) != d->height ||
        qfits_header_getint(extension, "BITPIX", 0) != d->bitpix ||
        qfits_header_getint(extension, "PCOUNT", -1) != 0 ||
        qfits_header_getint(extension, "GCOUNT", -1) != 1 ||
        qfits_header_getdouble(extension, "BSCALE", 1.0) != d->bscale ||
        qfits_header_getdouble(extension, "BZERO", 0.0) != d->bzero) goto done;
    if (qfits_get_datinfo_wide((char *)d->path, 0, NULL, &primary_size) || primary_size ||
        qfits_get_hdrinfo_wide((char *)d->path, 1, &header_start, &header_size) ||
        qfits_get_datinfo_wide((char *)d->path, 1, &span->data_start, &span->data_size)) goto done;
    bytes = (uint64_t)d->width * (uint64_t)d->height * (unsigned)width;
    padded = (bytes + 2879) / 2880 * 2880;
    if (header_start < 2880 || header_size < 2880 ||
        header_start > span->identity.st_size - header_size ||
        span->data_start != header_start + header_size ||
        span->data_size < 0 || (uint64_t)span->data_size != padded ||
        span->data_start > span->identity.st_size ||
        span->data_size != span->identity.st_size - span->data_start) goto done;
    okay = 1;
done:
    qfits_header_destroy(primary);
    qfits_header_destroy(extension);
    return okay;
}
static int write_header(FILE *out, qfits_header *h, const char *basename, size_t count, int primary, size_t *header_bytes)
{
    qfits_header *copy = qfits_header_new();
    char value[80], key[81], val[81], comment[81], line[81];
    int i, okay = 0;
    off_t begin = ftello(out), end;
    if (copy == NULL || begin < 0) goto done;
    /* Rebuild without deletion: qfits_header_del leaves n inconsistent (#212).
     * Retain original card text and ordering except the explicit edited cards. */
    for (i = 0; i < h->n; ++i) {
        if (qfits_header_getitem(h, i, key, val, comment, line)) goto done;
        if (!strcmp(key, "END") || !strcmp(key, "ORIGFILE") ||
            !strcmp(key, "CHECKSUM") || (primary && !strcmp(key, "NEXTEND"))) continue;
        qfits_header_append(copy, key, *val ? val : NULL,
            *comment ? comment : NULL, *line ? line : NULL);
    }
    snprintf(value, sizeof(value), "'%s'", basename);
    qfits_header_append(copy, "ORIGFILE", value, "Name for this file", NULL);
    if (primary) {
        snprintf(value, sizeof(value), "%lu", (unsigned long)count);
        qfits_header_append(copy, "NEXTEND", value, "Number of image extensions", NULL);
    }
    qfits_header_append(copy, "END", NULL, NULL, NULL);
    if (!header_string(copy, "ORIGFILE", basename)) goto done;
    if (qfits_header_dump(copy, out) != 0 || ferror(out)) goto done;
    end = ftello(out);
    /* The qfits bound is cumulative over the complete MEF, not per HDU.
     * Use exact emitted, padded header bytes; do not include image payloads
     * or disable the bounded scanner. Source inspection remains capped. */
    if (end < begin || end - begin < 2880 || (end - begin) % 2880 ||
        (uintmax_t)(end - begin) > SIZE_MAX - *header_bytes) goto done;
    *header_bytes += (size_t)(end - begin);
    okay = 1;
 done:
    qfits_header_destroy(copy);
    return okay;
}
static int copy_span(FILE *out, const char *path, const source_span *span)
{
    unsigned char buffer[65536];
    struct stat before, after;
    FILE *in = fopen(path, "rb");
    off_t remaining = span->data_size;
    int okay = 0;
    if (in == NULL) return 0;
    if (fstat(fileno(in), &before) || !same_file(&before, &span->identity) ||
        fseeko(in, span->data_start, SEEK_SET)) goto done;
    while (remaining > 0) {
        size_t n = remaining > (off_t)sizeof(buffer) ? sizeof(buffer) : (size_t)remaining;
        if (fread(buffer, 1, n, in) != n || fwrite(buffer, 1, n, out) != n) goto done;
        remaining -= (off_t)n;
    }
    if (ferror(in) || ferror(out) || fstat(fileno(in), &after) ||
        !same_file(&before, &after)) goto done;
    okay = 1;
done:
    if (fclose(in)) okay = 0;
    return okay;
}
int mef_mef_assemble(const char *final_path, const char *reference_id,
    const mef_assembly_detector *detectors, size_t count, char *message, size_t size)
{
    source_span *spans = NULL;
    FILE *out = NULL;
    qfits_header *h = NULL;
    char *temporary = NULL;
    const char *basename, *detail = "Invalid assembly manifest";
    struct stat st;
    size_t i, j, reference = SIZE_MAX, length, header_bytes = 0;
    int fd = -1, owned = 0, committed = 0;
    if (final_path == NULL || final_path[0] != '/' || reference_id == NULL ||
        !*reference_id || detectors == NULL || count == 0 || count > 4096) goto done;
    length = strlen(final_path);
    basename = strrchr(final_path, '/') + 1;
    if (length < 6 || strcmp(final_path + length - 5, ".fits") ||
        strlen(basename) > 68 || strchr(basename, '\'') || strchr(basename, '\n') ||
        length > SIZE_MAX - 32) goto done;
    for (i = 0; basename[i]; ++i)
        if ((unsigned char)basename[i] < 32 || (unsigned char)basename[i] > 126) goto done;
    for (i = 0; i < count; ++i) {
        const mef_assembly_detector *d = detectors + i;
        if (d->path == NULL || d->path[0] != '/' || d->detector_id == NULL || !*d->detector_id ||
            d->output_hdu != i + 1 || d->width < 1 || d->height < 1 ||
            !bit_width(d->bitpix) ||
            (uint64_t)d->width * (uint64_t)d->height >
                ((uint64_t)INT64_MAX - 2879) / (unsigned)bit_width(d->bitpix) || !isfinite(d->bscale) || d->bscale == 0 || !isfinite(d->bzero)) goto done;
        for (j = 0; j < i; ++j)
            if (!strcmp(d->detector_id, detectors[j].detector_id) ||
                !strcmp(d->path, detectors[j].path) ||
                d->configuration_detector == detectors[j].configuration_detector) goto done;
        if (!strcmp(reference_id, d->detector_id)) reference = i;
    }
    if (reference == SIZE_MAX) goto done;
    detail = "Final MEF destination exists or is inaccessible";
    if (lstat(final_path, &st) == 0 || errno != ENOENT) goto done;
    spans = calloc(count, sizeof(*spans));
    if (spans == NULL) { detail = "Cannot allocate assembly metadata"; goto done; }
    qfits_cache_purge();
    detail = "Detector product identity, layout or byte span does not match manifest";
    for (i = 0; i < count; ++i) if (!inspect(detectors + i, spans + i)) goto done;
    temporary = malloc(length + 32);
    if (temporary == NULL) goto done;
    snprintf(temporary, length + 32, "%s.assembling-XXXXXX", final_path);
    detail = "Cannot write private MEF assembly";
    fd = mkstemp(temporary);
    if (fd < 0) goto done;
    owned = 1;
    out = fdopen(fd, "wb");
    if (out == NULL) goto done;
    fd = -1;
    h = qfits_header_read((char *)detectors[reference].path);
    if (h == NULL || !write_header(out, h, basename, count, 1, &header_bytes)) goto done;
    qfits_header_destroy(h); h = NULL;
    for (i = 0; i < count; ++i) {
        h = qfits_header_readext((char *)detectors[i].path, 1);
        if (h == NULL || !write_header(out, h, basename, count, 0, &header_bytes) ||
            !copy_span(out, detectors[i].path, spans + i)) goto done;
        qfits_header_destroy(h); h = NULL;
    }
    if (fclose(out)) { out = NULL; goto done; }
    out = NULL;
    detail = "Assembled MEF failed native readback";
    qfits_cache_purge();
    if (qfits_cache_prime_bounded(temporary, count + 1, header_bytes) ||
        qfits_query_n_ext(temporary) != (int)count) goto done;
    h = qfits_header_read(temporary);
    if (h == NULL || qfits_header_getint(h, "NAXIS", -1) != 0 ||
        qfits_header_getint(h, "NEXTEND", -1) != (int)count ||
        !header_string(h, "ORIGFILE", basename)) goto done;
    qfits_header_destroy(h); h = NULL;
    for (i = 0; i < count; ++i) {
        off_t start, bytes;
        h = qfits_header_readext(temporary, (int)i + 1);
        if (h == NULL || !header_string(h, "EXTNAME", detectors[i].detector_id) ||
            !header_string(h, "ORIGFILE", basename) ||
            qfits_header_getint(h, "NAXIS1", -1) != detectors[i].width ||
            qfits_header_getint(h, "NAXIS2", -1) != detectors[i].height ||
            qfits_header_getint(h, "BITPIX", 0) != detectors[i].bitpix ||
            qfits_get_datinfo_wide(temporary, (int)i + 1, &start, &bytes) ||
            bytes != spans[i].data_size) goto done;
        qfits_header_destroy(h); h = NULL;
        if (lstat(detectors[i].path, &st) || !same_file(&st, &spans[i].identity)) goto done;
    }
    detail = "Cannot exclusively publish final MEF";
    if (link(temporary, final_path)) goto done;
    committed = 1;
done:
    qfits_header_destroy(h);
    if (out != NULL) fclose(out);
    if (fd >= 0) close(fd);
    if (owned && unlink(temporary) && committed) {
        if (message != NULL && size) snprintf(message, size, "MEF complete; private staging retained: %s", temporary);
        free(temporary); free(spans); qfits_cache_purge(); return 0;
    }
    free(temporary); free(spans); qfits_cache_purge();
    if (!committed) return fail(message, size, detail);
    if (message != NULL && size) message[0] = '\0';
    return 0;
}

/* BPM layout admission is separate from the bias one-extension contract. */
#define BPM_PLANES 7
static const char *const bpm_names[BPM_PLANES] = {
    "BPM", "COVERAGE", "NSAMPLE", "NEWFLAGS", "SELECTION", "PRIORFLAGS", "PRIORSEL"
};
typedef struct {
    source_span planes[BPM_PLANES];
    int count, width, height;
    const char *names[BPM_PLANES];
} bpm_source;

static int inspect_bpm(const mef_bpm_assembly_detector *d, bpm_source *source)
{
    struct stat st;
    qfits_header *h = NULL;
    int i, count, okay = 0;
    off_t start, length, previous = 0;
    if (lstat(d->path, &st) || !S_ISREG(st.st_mode) || st.st_size <= 0 ||
        st.st_size % 2880 || qfits_cache_prime_bounded((char *)d->path, BPM_PLANES, 1048576)) return 0;
    count = qfits_query_n_ext((char *)d->path) + 1;
    if (count < 5 || count > 6) return 0;
    source->count = count;
    for (i = 0; i < count; ++i) {
        uint64_t bytes;
        h = i ? qfits_header_readext((char *)d->path, i) : qfits_header_read((char *)d->path);
        source->names[i] = i == 5 && h && header_string(h, "EXTNAME", "PRIORSEL") ? "PRIORSEL" : bpm_names[i];
        if (!h || !header_string(h, "EXTNAME", source->names[i]) ||
            qfits_header_getint(h, "NAXIS", -1) != 2 ||
            qfits_header_getint(h, "BITPIX", 0) != (i == 2 ? 16 : 8) ||
            qfits_header_getdouble(h, "BSCALE", 1.0) != 1.0 ||
            qfits_header_getdouble(h, "BZERO", 0.0) != 0.0) goto done;
        if (i == 0) {
            source->width = qfits_header_getint(h, "NAXIS1", 0);
            source->height = qfits_header_getint(h, "NAXIS2", 0);
            if (!header_string(h, "SIMPLE", "T") || !header_string(h, "DETID", d->detector_id) ||
                !header_string(h, "MASKENC", "REASON8") || !header_string(h, "MASKREG", "WENU_BPM_V1") ||
                source->width < 1 || source->height < 1) goto done;
        } else if (!header_string(h, "XTENSION", "IMAGE") ||
            qfits_header_getint(h, "PCOUNT", -1) != 0 || qfits_header_getint(h, "GCOUNT", -1) != 1) goto done;
        if (qfits_header_getint(h, "NAXIS1", 0) != source->width ||
            qfits_header_getint(h, "NAXIS2", 0) != source->height ||
            qfits_get_hdrinfo_wide((char *)d->path, i, &start, &length) || start != previous ||
            qfits_get_datinfo_wide((char *)d->path, i, &source->planes[i].data_start, &source->planes[i].data_size)) goto done;
        bytes = (uint64_t)source->width * (uint64_t)source->height * (i == 2 ? 2u : 1u);
        if (bytes > INT64_MAX - 2879 || length < 2880 || length % 2880 ||
            start > st.st_size - length || source->planes[i].data_start != start + length ||
            source->planes[i].data_size != (off_t)((bytes + 2879) / 2880 * 2880) ||
            source->planes[i].data_size > st.st_size - source->planes[i].data_start) goto done;
        source->planes[i].identity = st;
        previous = source->planes[i].data_start + source->planes[i].data_size;
        qfits_header_destroy(h); h = NULL;
    }
    okay = previous == st.st_size;
done:
    qfits_header_destroy(h);
    return okay;
}

static qfits_header *bpm_header(qfits_header *source, const mef_bpm_assembly_detector *d,
    int plane, const char *plane_name, size_t total)
{
    qfits_header *h = qfits_header_new();
    char key[81], value[81], comment[81], line[81], number[32], quoted[81];
    int i;
    if (!h) return NULL;
    if (plane < 0) {
        qfits_header_append(h, "SIMPLE", "T", NULL, NULL);
        qfits_header_append(h, "BITPIX", "8", NULL, NULL);
        qfits_header_append(h, "NAXIS", "0", NULL, NULL);
        qfits_header_append(h, "EXTEND", "T", NULL, NULL);
    } else {
        qfits_header_append(h, "XTENSION", "'IMAGE'", NULL, NULL);
        snprintf(number, sizeof(number), "%d", plane == 2 ? 16 : 8);
        qfits_header_append(h, "BITPIX", number, NULL, NULL);
        qfits_header_append(h, "NAXIS", "2", NULL, NULL);
        for (i = 1; i <= 2; ++i) {
            snprintf(key, sizeof(key), "NAXIS%d", i);
            snprintf(number, sizeof(number), "%d", qfits_header_getint(source, key, 0));
            qfits_header_append(h, key, number, NULL, NULL);
        }
        qfits_header_append(h, "PCOUNT", "0", NULL, NULL);
        qfits_header_append(h, "GCOUNT", "1", NULL, NULL);
    }
    for (i = 0; i < source->n; ++i) {
        if (qfits_header_getitem(source, i, key, value, comment, line)) goto failed;
        if (!strcmp(key, "SIMPLE") || !strcmp(key, "XTENSION") || !strcmp(key, "BITPIX") ||
            !strncmp(key, "NAXIS", 5) || !strcmp(key, "PCOUNT") || !strcmp(key, "GCOUNT") ||
            !strcmp(key, "EXTEND") || !strcmp(key, "NEXTEND") || !strcmp(key, "EXTNAME") ||
            !strcmp(key, "EXTVER") || !strcmp(key, "DETID") || !strcmp(key, "END") ||
            !strcmp(key, "CHECKSUM") || (plane < 0 && !strcmp(key, "DATASUM"))) continue;
        qfits_header_append(h, key, *value ? value : NULL, *comment ? comment : NULL, *line ? line : NULL);
    }
    snprintf(quoted, sizeof(quoted), "'%s'", d->detector_id);
    qfits_header_append(h, "DETID", quoted, NULL, NULL);
    if (plane >= 0) {
        snprintf(quoted, sizeof(quoted), "'%s'", plane == 0 ? d->detector_id : plane_name);
        qfits_header_append(h, "EXTNAME", quoted, NULL, NULL);
        snprintf(number, sizeof(number), "%lu", (unsigned long)d->configuration_detector + 1);
        qfits_header_append(h, "EXTVER", number, NULL, NULL);
    } else {
        snprintf(number, sizeof(number), "%lu", (unsigned long)total);
        qfits_header_append(h, "NEXTEND", number, NULL, NULL);
    }
    qfits_header_append(h, "END", NULL, NULL, NULL);
    return h;
failed:
    qfits_header_destroy(h);
    return NULL;
}

int mef_bpm_mef_assemble(const char *path, const char *reference,
    const mef_bpm_assembly_detector *detectors, size_t count, char *message, size_t size)
{
    bpm_source *sources = NULL;
    qfits_header *original = NULL, *h = NULL;
    FILE *out = NULL;
    struct stat st;
    char *temporary = NULL;
    const char *name, *detail = "Invalid BPM assembly request";
    size_t i, j, ref = SIZE_MAX, total = 0, bytes = 0, output_hdu = 0;
    int plane, pass, fd = -1, owned = 0, status = -1;
    if (!path || path[0] != '/' || !reference || !detectors || !count || count > 4096) goto done;
    name = strrchr(path, '/') + 1;
    if (strlen(name) < 6 || strlen(name) > 68 || strcmp(name + strlen(name) - 5, ".fits") ||
        strchr(name, '\'') || strspn(name, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-") != strlen(name)) goto done;
    for (i = 0; i < count; ++i) {
        const mef_bpm_assembly_detector *d = detectors + i;
        if (!d->path || d->path[0] != '/' || !d->detector_id || !*d->detector_id ||
            strlen(d->detector_id) > 64 || strchr(d->detector_id, '\'') ||
            d->configuration_detector > INT_MAX - 1) goto done;
        for (j = 0; j < i; ++j)
            if (!strcmp(d->path, detectors[j].path) || !strcmp(d->detector_id, detectors[j].detector_id) ||
                d->configuration_detector == detectors[j].configuration_detector) goto done;
        if (!strcmp(d->detector_id, reference)) ref = i;
    }
    if (ref == SIZE_MAX || lstat(path, &st) == 0 || errno != ENOENT) goto done;
    sources = calloc(count, sizeof(*sources));
    if (!sources) goto done;
    qfits_cache_purge();
    detail = "BPM detector identity, diagnostic layout or padded data span differs";
    for (i = 0; i < count; ++i) {
        if (!inspect_bpm(detectors + i, sources + i)) goto done;
        total += (size_t)sources[i].count;
    }
    temporary = malloc(strlen(path) + 32);
    if (!temporary) goto done;
    snprintf(temporary, strlen(path) + 32, "%s.assembling-XXXXXX", path);
    fd = mkstemp(temporary);
    if (fd < 0) goto done;
    owned = 1; out = fdopen(fd, "wb");
    if (!out) goto done;
    fd = -1;
    original = qfits_header_read((char *)detectors[ref].path);
    if (!original || !(h = bpm_header(original, detectors + ref, -1, NULL, total)) ||
        !write_header(out, h, name, total, 1, &bytes)) goto done;
    qfits_header_destroy(original); original = NULL;
    qfits_header_destroy(h); h = NULL;
    /* Masks form a contiguous catalogue-ordered group, then diagnostic planes. */
    for (pass = 0; pass < 2; ++pass) for (i = 0; i < count; ++i) {
        for (plane = pass ? 1 : 0; plane < (pass ? sources[i].count : 1); ++plane) {
            original = plane ? qfits_header_readext((char *)detectors[i].path, plane) : qfits_header_read((char *)detectors[i].path);
            h = original ? bpm_header(original, detectors + i, plane, sources[i].names[plane], total) : NULL;
            if (!h || !write_header(out, h, name, total, 0, &bytes) ||
                !copy_span(out, detectors[i].path, sources[i].planes + plane)) goto done;
            qfits_header_destroy(original); original = NULL;
            qfits_header_destroy(h); h = NULL;
        }
    }
    if (fflush(out) || fsync(fileno(out))) goto done;
    if (fclose(out)) { out = NULL; goto done; }
    out = NULL;
    detail = "Assembled BPM MEF native readback failed";
    qfits_cache_purge();
    if (qfits_cache_prime_bounded(temporary, total + 1, bytes) || qfits_query_n_ext(temporary) != (int)total) goto done;
    for (pass = 0; pass < 2; ++pass) for (i = 0; i < count; ++i) {
        for (plane = pass ? 1 : 0; plane < (pass ? sources[i].count : 1); ++plane) {
            off_t start, length;
            h = qfits_header_readext(temporary, (int)++output_hdu);
            if (!h || !header_string(h, "DETID", detectors[i].detector_id) ||
                !header_string(h, "EXTNAME", plane ? sources[i].names[plane] : detectors[i].detector_id) ||
                !header_string(h, "ORIGFILE", name) ||
                qfits_header_getint(h, "EXTVER", 0) != (int)detectors[i].configuration_detector + 1 ||
                qfits_header_getint(h, "BITPIX", 0) != (plane == 2 ? 16 : 8) ||
                qfits_header_getint(h, "NAXIS1", 0) != sources[i].width ||
                qfits_header_getint(h, "NAXIS2", 0) != sources[i].height ||
                qfits_get_datinfo_wide(temporary, (int)output_hdu, &start, &length) ||
                length != sources[i].planes[plane].data_size) goto done;
            qfits_header_destroy(h); h = NULL;
        }
        if (lstat(detectors[i].path, &st) || !same_file(&st, &sources[i].planes[0].identity)) goto done;
    }
    detail = "Cannot exclusively publish BPM MEF";
    if (link(temporary, path)) goto done;
    status = 0;
done:
    qfits_header_destroy(original); qfits_header_destroy(h);
    if (out) fclose(out);
    if (fd >= 0) close(fd);
    if (owned) unlink(temporary);
    free(temporary); free(sources); qfits_cache_purge();
    if (message && size) snprintf(message, size, "%s", status ? detail : "");
    return status;
}
