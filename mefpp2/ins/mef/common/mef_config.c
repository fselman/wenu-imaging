/* Owned immutable snapshot adapter. Legacy numerical processing is untouched. */
#include "mef_config.h"
#include "mefp_lib.h"
#include <float.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int prescan_x[2], overscan_x[2], trimreg[4];
    float ron, gain, crval1, crval2, crpix1, crpix2;
} mef_detector_config;

struct mef_config {
    mef_allocator allocator;
    mef_detector_config *detectors;
#include "mef_config_members.h"
};

static void *default_allocate(void *user, size_t bytes)
{
    (void)user;
    /* Parentheses bypass Eclipse's function-like malloc/free macros. */
    return (malloc)(bytes);
}

static void default_release(void *user, void *pointer)
{
    (void)user;
    (free)(pointer);
}

static void release_owned(mef_config *config, void *pointer)
{
    if (pointer != NULL)
        config->allocator.release(config->allocator.user, pointer);
}

void mef_config_destroy(mef_config *config)
{
    mef_allocator allocator;
    if (config == NULL) return;
    allocator = config->allocator;
#define MEF_STRING(member, key) release_owned(config, config->member);
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    release_owned(config, config->detectors);
    allocator.release(allocator.user, config);
}

mef_status mef_config_from_legacy(const struct _mef_bb_ *source,
    const mef_allocator *allocator, mef_config **out, const char **diagnostic)
{
    mef_allocator selected;
    mef_config *config;
    size_t bytes;
    int i;
    mef_status status;
    const char *detail;
    if (diagnostic != NULL) *diagnostic = NULL;
    if (out == NULL || *out != NULL || source == NULL ||
        source->nchips <= 0 || source->ccd == NULL ||
        (allocator != NULL && (allocator->allocate == NULL ||
                               allocator->release == NULL))) {
        if (diagnostic != NULL) *diagnostic = "Invalid snapshot arguments";
        return MEF_ERR_CONFIG;
    }
    if ((size_t)source->nchips > (size_t)-1 / sizeof(mef_detector_config)) {
        if (diagnostic != NULL) *diagnostic = "Detector allocation size overflow";
        return MEF_ERR_MEMORY;
    }
    selected.user = NULL;
    selected.allocate = default_allocate;
    selected.release = default_release;
    if (allocator != NULL) selected = *allocator;
    config = selected.allocate(selected.user, sizeof(*config));
    if (config == NULL) {
        if (diagnostic != NULL) *diagnostic = "Cannot allocate snapshot";
        return MEF_ERR_MEMORY;
    }
    /* Initialize pointer members explicitly; do not assume all-zero NULL bits. */
    config->allocator = selected;
    config->detectors = NULL;
#define MEF_STRING(member, key) config->member = NULL;
#define MEF_INT(member, key) config->member = source->member;
#define MEF_FLOAT(member, key) config->member = source->member;
#define MEF_DOUBLE(member, key) config->member = source->member;
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    status = MEF_ERR_MEMORY;
    detail = "Cannot allocate detector settings";
    bytes = (size_t)source->nchips * sizeof(*config->detectors);
    config->detectors = selected.allocate(selected.user, bytes);
    if (config->detectors == NULL) goto fail;
    for (i = 0; i < source->nchips; ++i) {
        memcpy(config->detectors[i].prescan_x, source->ccd[i].prescan_x,
               sizeof(config->detectors[i].prescan_x));
        memcpy(config->detectors[i].overscan_x, source->ccd[i].overscan_x,
               sizeof(config->detectors[i].overscan_x));
        memcpy(config->detectors[i].trimreg, source->ccd[i].trimreg,
               sizeof(config->detectors[i].trimreg));
        config->detectors[i].ron = source->ccd[i].ron;
        config->detectors[i].gain = source->ccd[i].gain;
        config->detectors[i].crval1 = source->ccd[i].crval1;
        config->detectors[i].crval2 = source->ccd[i].crval2;
        config->detectors[i].crpix1 = source->ccd[i].crpix1;
        config->detectors[i].crpix2 = source->ccd[i].crpix2;
    }
#define MEF_STRING(member, key) \
    if (source->member == NULL) { \
        status = MEF_ERR_CONFIG; detail = key; goto fail; \
    } \
    bytes = strlen(source->member); \
    if (bytes == (size_t)-1) { detail = key; goto fail; } \
    config->member = selected.allocate(selected.user, bytes + 1); \
    if (config->member == NULL) { detail = key; goto fail; } \
    memcpy(config->member, source->member, bytes + 1);
#define MEF_INT(member, key)
#define MEF_FLOAT(member, key)
#define MEF_DOUBLE(member, key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    *out = config;
    return MEF_OK;
fail:
    mef_config_destroy(config);
    if (diagnostic != NULL) *diagnostic = detail;
    return status;
}

static void json_string(FILE *stream, const char *text)
{
    const unsigned char *p;
    fputc('"', stream);
    for (p = (const unsigned char *)text; *p != 0; ++p) {
        if (*p == '"' || *p == '\\') {
            fputc('\\', stream); fputc(*p, stream);
        } else if (*p < 32) {
            fprintf(stream, "\\u%04x", (unsigned int)*p);
        } else fputc(*p, stream);
    }
    fputc('"', stream);
}

static void bits(FILE *stream, const void *value, size_t size)
{
    unsigned char bytes[sizeof(double)];
    unsigned int endian;
    size_t i;
    endian = 1;
    memcpy(bytes, value, size);
    fputc('"', stream);
    for (i = 0; i < size; ++i)
        fprintf(stream, "%02x", (unsigned int)
            bytes[*(const unsigned char *)&endian ? size - 1 - i : i]);
    fputc('"', stream);
}

static void entry(FILE *stream, int *first, const char *key, const char *type)
{
    if (!*first) fputs(",\n", stream);
    *first = 0;
    json_string(stream, key);
    fputs(":{\"type\":", stream); json_string(stream, type);
    fputs(",\"value\":", stream);
}

mef_status mef_config_dump(const mef_config *config, FILE *stream)
{
    int first, i, j;
    char key[80];
    const mef_detector_config *d;
    if (config == NULL || stream == NULL) return MEF_ERR_CONFIG;
    if (CHAR_BIT != 8 || sizeof(float) != 4 || sizeof(double) != 8 ||
        FLT_RADIX != 2 || FLT_MANT_DIG != 24 || DBL_MANT_DIG != 53 ||
        FLT_MAX_EXP != 128 || DBL_MAX_EXP != 1024) return MEF_ERR_UNSUPPORTED;
    first = 1;
    fputs("{\n", stream);
#define MEF_STRING(member, key) entry(stream, &first, key, "string"); \
    json_string(stream, config->member); fputc('}', stream);
#define MEF_INT(member, key) entry(stream, &first, key, "int"); \
    fprintf(stream, "%d}", config->member);
#define MEF_FLOAT(member, key) entry(stream, &first, key, "float32-bits"); \
    bits(stream, &config->member, sizeof(float)); fputc('}', stream);
#define MEF_DOUBLE(member, key) entry(stream, &first, key, "float64-bits"); \
    bits(stream, &config->member, sizeof(double)); fputc('}', stream);
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    for (i = 0; i < config->nchips; ++i) {
        d = config->detectors + i;
        for (j = 0; j < 2; ++j) {
            sprintf(key, "MEF.PRESCAN.X.%s.CHIP%d", j ? "MAX" : "MIN", i + 1);
            entry(stream, &first, key, "int"); fprintf(stream, "%d}", d->prescan_x[j]);
            sprintf(key, "MEF.OVERSCAN.X.%s.CHIP%d", j ? "MAX" : "MIN", i + 1);
            entry(stream, &first, key, "int"); fprintf(stream, "%d}", d->overscan_x[j]);
        }
        for (j = 0; j < 4; ++j) {
            sprintf(key, "MEF.CROP.%s.CHIP%d", j == 0 ? "X.MIN" : j == 1 ? "X.MAX" : j == 2 ? "Y.MIN" : "Y.MAX", i + 1);
            entry(stream, &first, key, "int"); fprintf(stream, "%d}", d->trimreg[j]);
        }
#define DET_FLOAT(member, name) \
        sprintf(key, name ".CHIP%d", i + 1); \
        entry(stream, &first, key, "float32-bits"); \
        bits(stream, &d->member, sizeof(float)); fputc('}', stream);
        DET_FLOAT(ron, "MEF.CCD.RON")
        DET_FLOAT(gain, "MEF.CCD.GAIN")
        DET_FLOAT(crval1, "MEF.CRVAL1")
        DET_FLOAT(crval2, "MEF.CRVAL2")
        DET_FLOAT(crpix1, "MEF.CRPIX1")
        DET_FLOAT(crpix2, "MEF.CRPIX2")
#undef DET_FLOAT
    }
    fputs("\n}\n", stream);
    return ferror(stream) ? MEF_ERR_IO : MEF_OK;
}
