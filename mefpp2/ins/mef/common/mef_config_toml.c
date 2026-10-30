/* C90 mapping into the accepted M1 configuration constructor. */
#include "mef_config_toml.h"
#include "mef_toml_bundle.h"
#include "mefp_lib.h"
#include <float.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

static void detail(char *buffer, size_t capacity, const char *message)
{
    size_t length;
    if (buffer == NULL || capacity == 0) return;
    length = strlen(message);
    if (length >= capacity) length = capacity - 1;
    memcpy(buffer, message, length); buffer[length] = '\0';
}

/* The explicit compatibility override allowlist enumerates current global
 * numeric settings except detector count. Detector/header/prefix/identity changes require an
 * explicit alternative subset, not an override. This does not alter CLI rules. */
static int setting_valid(const char *key, const mef_toml_value *value, int override)
{
    static const char *integer_detector[] = {
        "MEF.PRESCAN.X.MIN.CHIP", "MEF.PRESCAN.X.MAX.CHIP",
        "MEF.OVERSCAN.X.MIN.CHIP", "MEF.OVERSCAN.X.MAX.CHIP",
        "MEF.CROP.X.MIN.CHIP", "MEF.CROP.X.MAX.CHIP",
        "MEF.CROP.Y.MIN.CHIP", "MEF.CROP.Y.MAX.CHIP"
    };
    static const char *real_detector[] = {
        "MEF.CCD.RON.CHIP", "MEF.CCD.GAIN.CHIP", "MEF.CRVAL1.CHIP",
        "MEF.CRVAL2.CHIP", "MEF.CRPIX1.CHIP", "MEF.CRPIX2.CHIP"
    };
    static const char *allowed[] = {
#define MEF_OVERRIDE(name) name,
#include "mef_toml_override_keys.def"
#undef MEF_OVERRIDE
    };
    const char *suffix;
    size_t i, length;
    int number, digit, real, permitted;
    if (override) {
        permitted = 0;
        for (i = 0; i < sizeof(allowed) / sizeof(allowed[0]); ++i)
            if (!strcmp(key, allowed[i])) permitted = 1;
        if (!permitted) return 0;
    }
#define MEF_INT(member, name) if (!strcmp(key, name)) return value->kind == MEF_TOML_INTEGER;
#define MEF_STRING(member, name) if (!strcmp(key, name)) return !override && value->kind == MEF_TOML_TEXT;
#define MEF_FLOAT(member, name) if (!strcmp(key, name)) return value->kind == MEF_TOML_REAL && value->real <= FLT_MAX && value->real >= -FLT_MAX;
#define MEF_DOUBLE(member, name) if (!strcmp(key, name)) return value->kind == MEF_TOML_REAL;
#include "mef_config_fields.def"
#undef MEF_INT
#undef MEF_STRING
#undef MEF_FLOAT
#undef MEF_DOUBLE
    if (override) return 0;
    for (i = 0; i < 14; ++i) {
        real = i >= 8;
        suffix = real ? real_detector[i - 8] : integer_detector[i];
        length = strlen(suffix);
        if (strncmp(key, suffix, length)) continue;
        suffix = key + length;
        if (*suffix < '1' || *suffix > '9') return 0;
        number = 0;
        while (*suffix) {
            if (*suffix < '0' || *suffix > '9') return 0;
            digit = *suffix++ - '0';
            if (number > (INT_MAX - digit) / 10) return 0;
            number = 10 * number + digit;
        }
        return real ? value->kind == MEF_TOML_REAL && value->real <= FLT_MAX && value->real >= -FLT_MAX
                    : value->kind == MEF_TOML_INTEGER;
    }
    return 0;
}

mef_status mef_config_from_toml(const char *path, const mef_allocator *allocator,
    mef_config **out, char *diagnostic, size_t capacity)
{
    mef_toml_bundle *document;
    mef_toml_value value;
    mef_bb source;
    mef_status status;
    const char *failed_key, *snapshot_detail;
    size_t count;
    int i, j;
    char key[80];
    detail(diagnostic, capacity, "");
    if (path == NULL || out == NULL || *out != NULL ||
        (allocator != NULL && (allocator->allocate == NULL || allocator->release == NULL))) {
        detail(diagnostic, capacity, "Invalid TOML snapshot arguments"); return MEF_ERR_CONFIG;
    }
    document = NULL;
    status = mef_toml_bundle_open(path, allocator, setting_valid, &document, diagnostic, capacity);
    if (status != MEF_OK) return status;
    source.ccd = NULL;
    failed_key = "MEF.NCHIPS";
    status = MEF_ERR_CONFIG;
    if (mef_toml_bundle_get(document, failed_key, &value) != MEF_OK ||
        value.kind != MEF_TOML_INTEGER || value.integer <= 0) goto cleanup;
    source.nchips = value.integer;
    /* Bound by the actual supplied field count before allocating/iterating. */
    if ((size_t)source.nchips > mef_toml_bundle_count(document) / 14 ||
        (size_t)source.nchips > (size_t)-1 / sizeof(*source.ccd)) goto cleanup;
    source.ccd = (malloc)((size_t)source.nchips * sizeof(*source.ccd));
    if (source.ccd == NULL) { status = MEF_ERR_MEMORY; goto cleanup; }
    count = 0;
#define FETCH(name, type) \
    failed_key = name; \
    if (mef_toml_bundle_get(document, name, &value) != MEF_OK || value.kind != type) goto cleanup; \
    ++count;
#define MEF_INT(member, name) FETCH(name, MEF_TOML_INTEGER) source.member = value.integer;
#define MEF_STRING(member, name) FETCH(name, MEF_TOML_TEXT) source.member = (char *)value.text;
#define MEF_FLOAT(member, name) FETCH(name, MEF_TOML_REAL) \
    if (value.real > FLT_MAX || value.real < -FLT_MAX) goto cleanup; \
    source.member = (float)value.real;
#define MEF_DOUBLE(member, name) FETCH(name, MEF_TOML_REAL) source.member = value.real;
#include "mef_config_fields.def"
#undef MEF_INT
#undef MEF_STRING
#undef MEF_FLOAT
#undef MEF_DOUBLE
    for (i = 0; i < source.nchips; ++i) {
        for (j = 0; j < 2; ++j) {
            sprintf(key, "MEF.PRESCAN.X.%s.CHIP%d", j ? "MAX" : "MIN", i + 1);
            FETCH(key, MEF_TOML_INTEGER) source.ccd[i].prescan_x[j] = value.integer;
            sprintf(key, "MEF.OVERSCAN.X.%s.CHIP%d", j ? "MAX" : "MIN", i + 1);
            FETCH(key, MEF_TOML_INTEGER) source.ccd[i].overscan_x[j] = value.integer;
        }
        for (j = 0; j < 4; ++j) {
            sprintf(key, "MEF.CROP.%s.CHIP%d", j == 0 ? "X.MIN" : j == 1 ? "X.MAX" : j == 2 ? "Y.MIN" : "Y.MAX", i + 1);
            FETCH(key, MEF_TOML_INTEGER) source.ccd[i].trimreg[j] = value.integer;
        }
#define DET_FLOAT(member, name) \
        sprintf(key, name ".CHIP%d", i + 1); FETCH(key, MEF_TOML_REAL) \
        if (value.real > FLT_MAX || value.real < -FLT_MAX) goto cleanup; \
        source.ccd[i].member = (float)value.real;
        DET_FLOAT(ron, "MEF.CCD.RON")
        DET_FLOAT(gain, "MEF.CCD.GAIN")
        DET_FLOAT(crval1, "MEF.CRVAL1")
        DET_FLOAT(crval2, "MEF.CRVAL2")
        DET_FLOAT(crpix1, "MEF.CRPIX1")
        DET_FLOAT(crpix2, "MEF.CRPIX2")
#undef DET_FLOAT
#undef FETCH
    }
    failed_key = "Unknown native key (all known fields required)";
    if (count != mef_toml_bundle_count(document)) goto cleanup;
    /* Strings are borrowed only while this constructor deep-copies them. */
    status = mef_config_from_legacy(&source, allocator, out, &snapshot_detail);
    if (status != MEF_OK) failed_key = snapshot_detail == NULL ? "Snapshot construction failed" : snapshot_detail;
cleanup:
    if (status != MEF_OK) detail(diagnostic, capacity, failed_key);
    (free)(source.ccd);
    mef_toml_bundle_close(document);
    return status;
}
