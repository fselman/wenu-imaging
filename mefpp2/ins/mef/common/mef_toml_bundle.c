/* C90 native-config composition only. No observation or calibration resolver. */
#include "mef_toml_bundle.h"
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FILES 64
#define MAX_DEPTH 16
#define MAX_FIELDS 65536
typedef struct {
    const char *key;
    mef_toml_value value;
    const char *source;
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
        if (local) *old = *item;
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
    if (depth && mef_toml_version(s->document) != 2)
        return fail(b, MEF_ERR_CONFIG, "Included subsets require schema_version=2", NULL, canonical, NULL);
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
