/* C90 native-config composition only. No observation or calibration resolver. */
#include "mef_toml_bundle.h"
#include "mef_config_domains.h"
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FILES 64
#define MAX_DEPTH 16
#define MAX_FIELDS 65536
typedef struct {
    const char *key;
    mef_toml_value value;
    const char *source, *source_key;
    int line, version, overridden;
} binding;
typedef struct {
    char path[PATH_MAX];
    mef_toml_document *document;
    binding *items;
    size_t count, capacity;
    int active;
} subset;
struct mef_toml_bundle {
    mef_allocator allocator;
    mef_toml_check check;
    char *diagnostic;
    size_t diagnostic_capacity, count;
    char *metadata;
    size_t metadata_size, metadata_capacity;
    subset files[MAX_FILES];
};

static void *allocate(void *user, size_t bytes) { (void)user; return malloc(bytes); }
static void release(void *user, void *pointer) { (void)user; free(pointer); }
static void append(mef_toml_bundle *b, const char *text)
{
    size_t used, length;
    if (b->diagnostic == NULL || b->diagnostic_capacity == 0) return;
    used = strlen(b->diagnostic); length = strlen(text);
    if (length >= b->diagnostic_capacity - used) length = b->diagnostic_capacity - used - 1;
    memcpy(b->diagnostic + used, text, length); b->diagnostic[used + length] = '\0';
}
static mef_status fail(mef_toml_bundle *b, mef_status status, const char *reason,
    const char *key, const char *path, const char *other)
{
    if (b->diagnostic != NULL && b->diagnostic_capacity) b->diagnostic[0] = '\0';
    append(b, reason);
    if (key != NULL) { append(b, ": "); append(b, key); }
    if (path != NULL) { append(b, " ["); append(b, path); append(b, "]"); }
    if (other != NULL) { append(b, " versus ["); append(b, other); append(b, "]"); }
    return status;
}
static binding *find(subset *s, const char *key)
{
    size_t i;
    for (i = 0; i < s->count; ++i) if (!strcmp(s->items[i].key, key)) return s->items + i;
    return NULL;
}
static int declared(subset *s, const char *key)
{
    size_t i;
    for (i = 0; i < mef_toml_override_count(s->document); ++i)
        if (!strcmp(mef_toml_override(s->document, i), key)) return 1;
    return 0;
}
static int equal(const mef_toml_value *a, const mef_toml_value *b)
{
    if (a->kind != b->kind) return 0;
    if (a->kind == MEF_TOML_INTEGER) return a->integer == b->integer;
    if (a->kind == MEF_TOML_REAL) return !memcmp(&a->real, &b->real, sizeof(a->real));
    return !strcmp(a->text, b->text);
}
static mef_status insert(mef_toml_bundle *b, subset *s, const binding *item, int local)
{
    binding *old, *grown;
    size_t capacity;
    old = find(s, item->key);
    if (old != NULL) {
        if (!equal(&old->value, &item->value) && !declared(s, item->key))
            return fail(b, MEF_ERR_CONFIG, "Conflicting definitions", item->key, old->source, item->source);
        /* Parent declarations may resolve sibling conflicts, but only using
         * that parent's validated local binding. No implicit last-include wins. */
        if (local) { *old = *item; old->overridden = declared(s, item->key); }
        return MEF_OK;
    }
    if (s->count == s->capacity) {
        capacity = s->capacity ? 2 * s->capacity : 32;
        if (capacity > MAX_FIELDS || capacity > (size_t)-1 / sizeof(*grown))
            return fail(b, MEF_ERR_CONFIG, "Composition field limit", NULL, s->path, NULL);
        grown = b->allocator.allocate(b->allocator.user, capacity * sizeof(*grown));
        if (grown == NULL) return fail(b, MEF_ERR_MEMORY, "Cannot allocate composition bindings", NULL, s->path, NULL);
        if (s->count) memcpy(grown, s->items, s->count * sizeof(*grown));
        if (s->items != NULL) b->allocator.release(b->allocator.user, s->items);
        s->items = grown; s->capacity = capacity;
    }
    s->items[s->count++] = *item;
    return MEF_OK;
}

static mef_status load(mef_toml_bundle *b, const char *path, size_t depth, subset **out)
{
    char canonical[PATH_MAX], child_path[PATH_MAX], parser_detail[512];
    const char *key, *include, *slash;
    subset *s, *child;
    binding item;
    mef_toml_value value;
    mef_status status;
    size_t i, j, base, length;
    if (depth >= MAX_DEPTH) return fail(b, MEF_ERR_CONFIG, "Composition depth limit", NULL, path, NULL);
    if (realpath(path, canonical) == NULL) return fail(b, MEF_ERR_IO, "Cannot resolve configuration", NULL, path, NULL);
    for (i = 0; i < b->count; ++i) {
        if (strcmp(b->files[i].path, canonical)) continue;
        if (b->files[i].active) return fail(b, MEF_ERR_CONFIG, "Include cycle", NULL, canonical, NULL);
        *out = b->files + i; return MEF_OK;
    }
    if (b->count == MAX_FILES) return fail(b, MEF_ERR_CONFIG, "Composition file limit", NULL, canonical, NULL);
    s = b->files + b->count++;
    strcpy(s->path, canonical); s->document = NULL; s->items = NULL;
    s->count = 0; s->capacity = 0; s->active = 1;
    status = mef_toml_open(canonical, &s->document, parser_detail, sizeof(parser_detail));
    if (status != MEF_OK) return fail(b, status, parser_detail, NULL, canonical, NULL);
    if (depth && mef_toml_version(s->document) != mef_toml_version(b->files[0].document))
        return fail(b, MEF_ERR_CONFIG, mef_toml_version(b->files[0].document) == 3 ?
            "Included subsets require schema_version=3" : "Included subsets require schema_version=2", NULL, canonical, NULL);
    /* Validate every local binding, including one later replaced by a parent. */
    for (i = 0; i < mef_toml_count(s->document); ++i) {
        key = mef_toml_key(s->document, i);
        if (mef_toml_get(s->document, key, &value) != MEF_OK || !b->check(key, &value, 0))
            return fail(b, MEF_ERR_CONFIG, "Invalid subset setting", key, canonical, NULL);
    }
    for (i = 0; i < mef_toml_override_count(s->document); ++i) {
        key = mef_toml_override(s->document, i);
        if (mef_toml_get(s->document, key, &value) != MEF_OK || !b->check(key, &value, 1))
            return fail(b, MEF_ERR_CONFIG, "Override forbidden or missing local value", key, canonical, NULL);
    }
    for (i = 0; i < mef_toml_include_count(s->document); ++i) {
        include = mef_toml_include(s->document, i); length = strlen(include);
        slash = strrchr(canonical, '/'); base = (size_t)(slash - canonical) + 1;
        if (include[0] == '/') base = 0;
        if (length >= sizeof(child_path) - base)
            return fail(b, MEF_ERR_CONFIG, "Include path limit", include, canonical, NULL);
        memcpy(child_path, canonical, base); memcpy(child_path + base, include, length + 1);
        status = load(b, child_path, depth + 1, &child);
        if (status != MEF_OK) return status;
        for (j = 0; j < child->count; ++j) {
            status = insert(b, s, child->items + j, 0);
            if (status != MEF_OK) return status;
        }
    }
    for (i = 0; i < mef_toml_override_count(s->document); ++i) {
        key = mef_toml_override(s->document, i);
        if (find(s, key) == NULL) return fail(b, MEF_ERR_CONFIG, "Override has no inherited value", key, canonical, NULL);
    }
    for (i = 0; i < mef_toml_count(s->document); ++i) {
        item.key = mef_toml_key(s->document, i); item.source = s->path;
        item.source_key = mef_toml_source_key(s->document, item.key);
        item.line = mef_toml_source_line(s->document, item.key);
        item.version = mef_toml_version(s->document); item.overridden = 0;
        status = mef_toml_get(s->document, item.key, &item.value);
        if (status != MEF_OK) return status;
        status = insert(b, s, &item, 1);
        if (status != MEF_OK) return status;
    }
    s->active = 0; *out = s; return MEF_OK;
}

void mef_toml_bundle_close(mef_toml_bundle *b)
{
    size_t i;
    mef_allocator a;
    if (b == NULL) return;
    a = b->allocator;
    for (i = 0; i < b->count; ++i) {
        if (b->files[i].items != NULL) a.release(a.user, b->files[i].items);
        mef_toml_close(b->files[i].document);
    }
    if (b->metadata != NULL) a.release(a.user, b->metadata);
    a.release(a.user, b);
}
mef_status mef_toml_bundle_open(const char *path, const mef_allocator *allocator,
    mef_toml_check check, mef_toml_bundle **out, char *diagnostic, size_t capacity)
{
    mef_allocator a;
    mef_toml_bundle *b;
    subset *root;
    mef_status status;
    if (diagnostic != NULL && capacity) diagnostic[0] = '\0';
    if (path == NULL || check == NULL || out == NULL || *out != NULL ||
        (allocator != NULL && (allocator->allocate == NULL || allocator->release == NULL))) return MEF_ERR_CONFIG;
    if (!mef_toml_is_initialized()) {
        if (diagnostic != NULL && capacity) { strncpy(diagnostic, "Parser not initialized", capacity - 1); diagnostic[capacity - 1] = '\0'; }
        return MEF_ERR_CONFIG;
    }
    a.user = NULL; a.allocate = allocate; a.release = release;
    if (allocator != NULL) a = *allocator;
    b = a.allocate(a.user, sizeof(*b));
    if (b == NULL) {
        if (diagnostic != NULL && capacity) { strncpy(diagnostic, "Cannot allocate composition", capacity - 1); diagnostic[capacity - 1] = '\0'; }
        return MEF_ERR_MEMORY;
    }
    b->allocator = a; b->check = check; b->count = 0;
    b->metadata = NULL; b->metadata_size = b->metadata_capacity = 0;
    b->diagnostic = diagnostic; b->diagnostic_capacity = capacity;
    status = load(b, path, 0, &root);
    if (status != MEF_OK) { mef_toml_bundle_close(b); return status; }
    *out = b; return MEF_OK;
}
size_t mef_toml_bundle_count(const mef_toml_bundle *b) { return b->files[0].count; }
mef_status mef_toml_bundle_get(const mef_toml_bundle *b, const char *key, mef_toml_value *out)
{
    size_t i;
    for (i = 0; i < b->files[0].count; ++i) if (!strcmp(b->files[0].items[i].key, key)) {
        *out = b->files[0].items[i].value; return MEF_OK;
    }
    return MEF_ERR_CONFIG;
}

static mef_status text(mef_toml_bundle *b, const char *value)
{
    size_t length, needed, capacity;
    char *grown;
    length = strlen(value);
    if (length > (size_t)-1 - b->metadata_size - 1) return MEF_ERR_MEMORY;
    needed = b->metadata_size + length + 1;
    if (needed > b->metadata_capacity) {
        capacity = b->metadata_capacity ? b->metadata_capacity : 512;
        while (capacity < needed) {
            if (capacity > (size_t)-1 / 2) return MEF_ERR_MEMORY;
            capacity *= 2;
        }
        grown = b->allocator.allocate(b->allocator.user, capacity);
        if (grown == NULL) return MEF_ERR_MEMORY;
        if (b->metadata_size) memcpy(grown, b->metadata, b->metadata_size);
        if (b->metadata != NULL) b->allocator.release(b->allocator.user, b->metadata);
        b->metadata = grown; b->metadata_capacity = capacity;
    }
    memcpy(b->metadata + b->metadata_size, value, length + 1);
    b->metadata_size += length; return MEF_OK;
}
static int utf8(const unsigned char *p)
{
    int n, i;
    unsigned int first;
    while (*p) {
        first = *p;
        if (first < 128) { ++p; continue; }
        n = first >= 0xc2 && first <= 0xdf ? 2 : first >= 0xe0 && first <= 0xef ? 3 :
            first >= 0xf0 && first <= 0xf4 ? 4 : 0;
        if (!n) return 0;
        for (i = 1; i < n; ++i) if (p[i] < 0x80 || p[i] > 0xbf) return 0;
        if ((first == 0xe0 && p[1] < 0xa0) || (first == 0xed && p[1] >= 0xa0) ||
            (first == 0xf0 && p[1] < 0x90) || (first == 0xf4 && p[1] >= 0x90)) return 0;
        p += n;
    }
    return 1;
}
static mef_status quoted(mef_toml_bundle *b, const char *value)
{
    const unsigned char *p;
    char escaped[8];
    mef_status status;
    if (!utf8((const unsigned char *)value)) return MEF_ERR_CONFIG;
    status = text(b, "\""); if (status != MEF_OK) return status;
    for (p = (const unsigned char *)value; *p; ++p) {
        if (*p == '"' || *p == '\\') { escaped[0] = '\\'; escaped[1] = (char)*p; escaped[2] = '\0'; }
        else if (*p < 32) sprintf(escaped, "\\u%04x", (unsigned int)*p);
        else { escaped[0] = (char)*p; escaped[1] = '\0'; }
        status = text(b, escaped); if (status != MEF_OK) return status;
    }
    return text(b, "\"");
}

mef_status mef_toml_bundle_sources(mef_toml_bundle *b, const char **out)
{
    size_t i;
    const binding *item;
    mef_domain_field field;
    mef_status status;
    char number[32];
    if (b == NULL || out == NULL || *out != NULL) return MEF_ERR_CONFIG;
    /* A failed serialization is never exposed; retry starts with empty text. */
    b->metadata_size = 0;
#define PUT(value) do { status = text(b, value); if (status != MEF_OK) goto failure; } while (0)
#define QUOTE(value) do { status = quoted(b, value); if (status != MEF_OK) goto failure; } while (0)
    PUT("{\"metadata_schema_version\":1,\"domain_schema_version\":1,\"source_hash_state\":\"not-recorded\",\"fields\":{");
    for (i = 0; i < b->files[0].count; ++i) {
        item = b->files[0].items + i;
        if (!mef_domain_from_native(item->key, &field)) { status = MEF_ERR_CONFIG; goto failure; }
        if (i) PUT(",");
        QUOTE(item->key); PUT(":{\"path\":"); QUOTE(field.path);
        PUT(",\"storage\":"); QUOTE(field.storage); PUT(",\"unit\":"); QUOTE(field.unit);
        PUT(",\"role\":"); QUOTE(field.role); PUT(",\"authority\":\"configured\",\"source_file\":"); QUOTE(item->source);
        PUT(",\"source_key\":"); QUOTE(item->source_key);
        sprintf(number, "%d", item->line); PUT(",\"source_line\":"); PUT(number);
        sprintf(number, "%d", item->version); PUT(",\"input_schema_version\":"); PUT(number);
        PUT(",\"unit_origin\":"); QUOTE(item->version == 3 ? "declared" : "schema");
        PUT(",\"inherited\":"); PUT(strcmp(item->source, b->files[0].path) ? "true" : "false");
        PUT(",\"explicit_override\":"); PUT(item->overridden ? "true" : "false"); PUT("}");
    }
    PUT("}}\n"); *out = b->metadata;
#undef PUT
#undef QUOTE
    return MEF_OK;
failure:
    return fail(b, status, status == MEF_ERR_MEMORY ? "Cannot allocate source record" : "Invalid UTF-8/source record", NULL, NULL, NULL);
}
