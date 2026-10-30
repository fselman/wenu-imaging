/* C90 mapping into the accepted M1 configuration constructor. */
#include "mef_config_toml.h"
#include "mef_toml_bundle.h"
#include "mef_config_domains.h"
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
    static const char *allowed[] = {
#define MEF_OVERRIDE(name) name,
#include "mef_toml_override_keys.def"
#undef MEF_OVERRIDE
    };
    mef_domain_field field;
    size_t i;
    int permitted;
    if (override) {
        permitted = 0;
        for (i = 0; i < sizeof(allowed) / sizeof(allowed[0]); ++i)
            if (!strcmp(key, allowed[i])) permitted = 1;
        if (!permitted) return 0;
    }
    if (!mef_domain_from_native(key, &field)) return 0;
    if (!strcmp(field.storage, "string")) return value->kind == MEF_TOML_TEXT;
    if (!strcmp(field.storage, "int32")) return value->kind == MEF_TOML_INTEGER;
    if (value->kind != MEF_TOML_REAL) return 0;
    return strcmp(field.storage, "float32") || (value->real <= FLT_MAX && value->real >= -FLT_MAX);
}

static mef_status config_from_bundle(mef_toml_bundle *document, const mef_allocator *allocator,
    mef_config **out, char *diagnostic, size_t capacity)
{
    mef_toml_value value;
    mef_bb source;
    mef_status status;
    const char *failed_key, *snapshot_detail;
    size_t count;
    int i, j;
    char key[80];
    detail(diagnostic, capacity, "");
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
    return status;
}

mef_status mef_config_from_toml(const char *path, const mef_allocator *allocator,
    mef_config **out, char *diagnostic, size_t capacity)
{
    mef_toml_bundle *document;
    mef_status status;
    detail(diagnostic, capacity, "");
    if (path == NULL || out == NULL || *out != NULL ||
        (allocator != NULL && (allocator->allocate == NULL || allocator->release == NULL))) {
        detail(diagnostic, capacity, "Invalid TOML snapshot arguments"); return MEF_ERR_CONFIG;
    }
    document = NULL;
    status = mef_toml_bundle_open(path, allocator, setting_valid, &document, diagnostic, capacity);
    if (status != MEF_OK) return status;
    status = config_from_bundle(document, allocator, out, diagnostic, capacity);
    mef_toml_bundle_close(document); return status;
}

struct mef_config_document {
    mef_allocator allocator;
    mef_config *settings;
    char *sources;
};
static void *doc_allocate(void *user, size_t bytes) { (void)user; return (malloc)(bytes); }
static void doc_release(void *user, void *pointer) { (void)user; (free)(pointer); }
static mef_config_document *document_new(const mef_allocator *allocator)
{
    mef_config_document *doc;
    mef_allocator a;
    a.user = NULL; a.allocate = doc_allocate; a.release = doc_release;
    if (allocator != NULL) a = *allocator;
    doc = a.allocate(a.user, sizeof(*doc));
    if (doc != NULL) { doc->allocator = a; doc->settings = NULL; doc->sources = NULL; }
    return doc;
}
void mef_config_document_destroy(mef_config_document *doc)
{
    mef_allocator a;
    if (doc == NULL) return;
    a = doc->allocator; mef_config_destroy(doc->settings);
    if (doc->sources != NULL) a.release(a.user, doc->sources);
    a.release(a.user, doc);
}
const mef_config *mef_config_document_settings(const mef_config_document *doc)
{ return doc == NULL ? NULL : doc->settings; }
mef_status mef_config_document_dump_sources(const mef_config_document *doc, FILE *stream)
{
    if (doc == NULL || stream == NULL) return MEF_ERR_CONFIG;
    return fputs(doc->sources, stream) == EOF ? MEF_ERR_IO : MEF_OK;
}
mef_status mef_config_document_from_toml(const char *path, const mef_allocator *allocator,
    mef_config_document **out, char *diagnostic, size_t capacity)
{
    mef_config_document *doc;
    mef_toml_bundle *bundle;
    const char *sources;
    size_t length;
    mef_status status;
    detail(diagnostic, capacity, "");
    if (path == NULL || out == NULL || *out != NULL ||
        (allocator != NULL && (allocator->allocate == NULL || allocator->release == NULL))) {
        detail(diagnostic, capacity, "Invalid configuration document arguments"); return MEF_ERR_CONFIG;
    }
    doc = document_new(allocator); bundle = NULL;
    if (doc == NULL) { detail(diagnostic, capacity, "Cannot allocate configuration document"); return MEF_ERR_MEMORY; }
    status = mef_toml_bundle_open(path, allocator, setting_valid, &bundle, diagnostic, capacity);
    if (status != MEF_OK) goto failure;
    status = config_from_bundle(bundle, allocator, &doc->settings, diagnostic, capacity);
    if (status != MEF_OK) goto failure;
    sources = NULL; status = mef_toml_bundle_sources(bundle, &sources);
    if (status != MEF_OK) goto failure;
    length = strlen(sources);
    doc->sources = doc->allocator.allocate(doc->allocator.user, length + 1);
    if (doc->sources == NULL) { status = MEF_ERR_MEMORY; detail(diagnostic, capacity, "Cannot copy source record"); goto failure; }
    memcpy(doc->sources, sources, length + 1);
    mef_toml_bundle_close(bundle); *out = doc; return MEF_OK;
failure:
    mef_toml_bundle_close(bundle); mef_config_document_destroy(doc); return status;
}
mef_status mef_config_document_clone(const mef_config_document *source, const mef_allocator *allocator,
    mef_config_document **out, char *diagnostic, size_t capacity)
{
    mef_config_document *copy;
    mef_status status;
    const char *message;
    size_t length;
    detail(diagnostic, capacity, "");
    if (source == NULL || out == NULL || *out != NULL ||
        (allocator != NULL && (allocator->allocate == NULL || allocator->release == NULL))) {
        detail(diagnostic, capacity, "Invalid configuration document clone"); return MEF_ERR_CONFIG;
    }
    copy = document_new(allocator);
    if (copy == NULL) { detail(diagnostic, capacity, "Cannot allocate document clone"); return MEF_ERR_MEMORY; }
    status = mef_config_clone(source->settings, allocator, &copy->settings, &message);
    if (status != MEF_OK) { detail(diagnostic, capacity, message); goto failure; }
    length = strlen(source->sources);
    copy->sources = copy->allocator.allocate(copy->allocator.user, length + 1);
    if (copy->sources == NULL) { status = MEF_ERR_MEMORY; detail(diagnostic, capacity, "Cannot copy source record"); goto failure; }
    memcpy(copy->sources, source->sources, length + 1); *out = copy; return MEF_OK;
failure:
    mef_config_document_destroy(copy); return status;
}
