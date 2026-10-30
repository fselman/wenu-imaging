/* Parser-specific C99 shim. Numerical code and native adapter remain C90.
 * Only built in the opt-in configuration probe lane; no installed engine link.
 * tomlc17 is unmodified and owns its tree until mef_toml_close. */
#include "mef_toml_bridge.h"
#include "tomlc17.h"
#include "mef_config_domains.h"
#include <limits.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef struct { char key[96], path[192]; toml_datum_t value; } domain_entry;
struct mef_toml_document {
    toml_result_t parsed;
    toml_datum_t native, includes, overrides;
    int version;
    domain_entry *entries;
    size_t count, capacity;
    char override_native[64][96];
};
static int initialized;
/* The compatibility envelope deliberately supports single-line strings only.
 * This excludes TOML 1.1 escape additions while retaining the 1.0 emitter's
 * quotes, Unicode, comments and escaped control bytes. It is not a new parser. */
static int shared_strings(const char *bytes, size_t length)
{
    int quote = 0, comment = 0;
    for (size_t i = 0; i < length; ++i) {
        unsigned char c = (unsigned char)bytes[i];
        if (comment) { if (c == '\n') comment = 0; continue; }
        if (!quote) {
            if (c == '#') { comment = 1; continue; }
            if (c != '\'' && c != '"') continue;
            if (i + 2 < length && bytes[i + 1] == c && bytes[i + 2] == c) return 0;
            quote = c;
        } else if (c == quote) quote = 0;
        else if (c == '\n' || c == '\r') return 0;
        else if (quote == '"' && c == '\\') {
            if (++i == length || strchr("\"\\btnfruU", bytes[i]) == NULL) return 0;
        }
    }
    return 1; /* Other malformed syntax is diagnosed by tomlc17 itself. */
}
static void detail(char *buffer, size_t capacity, const char *message)
{
    if (buffer != NULL && capacity != 0) snprintf(buffer, capacity, "%s", message);
}

void mef_config_toml_initialize(void)
{
    if (!initialized) {
        toml_option_t options = toml_default_option();
        options.check_utf8 = true;
        toml_set_option(options);
        initialized = 1;
    }
}

int mef_toml_is_initialized(void) { return initialized; }

void mef_toml_close(mef_toml_document *document)
{
    if (document != NULL) { toml_free(document->parsed); free(document->entries); free(document); }
}

/* Translation of the versioned parsed tree only; merge policy remains C90. */
static mef_status domain_walk(mef_toml_document *doc, const char *path,
    toml_datum_t node, int root, char *diagnostic, size_t capacity)
{
    mef_domain_field field;
    if (mef_domain_from_path(path, &field)) {
        toml_datum_t value = toml_get(node, "value"), unit = toml_get(node, "unit");
        if (node.type != TOML_TABLE || node.u.tab.size != 2 ||
            unit.type != TOML_STRING || strlen(unit.u.str.ptr) != (size_t)unit.u.str.len ||
            strcmp(unit.u.str.ptr, field.unit) || value.type == TOML_UNKNOWN ||
            (value.type == TOML_STRING && strlen(value.u.str.ptr) != (size_t)value.u.str.len)) {
            if (diagnostic && capacity) snprintf(diagnostic, capacity, "Invalid value/unit descriptor: %s", path);
            return MEF_ERR_CONFIG;
        }
        if (doc->count == doc->capacity) {
            size_t n = doc->capacity ? 2 * doc->capacity : 32;
            if (n > 65536 || n > (size_t)-1 / sizeof(*doc->entries)) {
                detail(diagnostic, capacity, "Domain field limit"); return MEF_ERR_CONFIG;
            }
            domain_entry *grown = realloc(doc->entries, n * sizeof(*grown));
            if (!grown) { detail(diagnostic, capacity, "Cannot allocate parsed domain entries"); return MEF_ERR_MEMORY; }
            doc->entries = grown; doc->capacity = n;
        }
        domain_entry *entry = doc->entries + doc->count++;
        strcpy(entry->key, field.native_key); strcpy(entry->path, field.path); entry->value = value;
        return MEF_OK;
    }
    if (!mef_domain_container(path) || node.type != TOML_TABLE) {
        if (diagnostic && capacity) snprintf(diagnostic, capacity, "Unknown domain key/container: %s", path);
        return MEF_ERR_CONFIG;
    }
    for (int i = 0; i < node.u.tab.size; ++i) {
        const char *key = node.u.tab.key[i];
        if (strlen(key) != (size_t)node.u.tab.len[i] || strchr(key, '.') ||
            strlen(path) + strlen(key) + 2 > 192) {
            detail(diagnostic, capacity, "Invalid or oversized domain key"); return MEF_ERR_CONFIG;
        }
        if (root && !strcmp(key, "schema_version")) continue;
        char child[192]; snprintf(child, sizeof(child), "%s.%s", path, key);
        mef_status status = domain_walk(doc, child, node.u.tab.value[i], 0, diagnostic, capacity);
        if (status != MEF_OK) return status;
    }
    return MEF_OK;
}
static domain_entry *domain_find(const mef_toml_document *doc, const char *key)
{
    for (size_t i = 0; i < doc->count; ++i) if (!strcmp(doc->entries[i].key, key)) return doc->entries + i;
    return NULL;
}

mef_status mef_toml_open(const char *path, mef_toml_document **out,
    char *diagnostic, size_t capacity)
{
    FILE *stream;
    long length;
    char *bytes;
    mef_toml_document *document;
    toml_datum_t root, version, native;
    detail(diagnostic, capacity, "");
    if (!initialized || path == NULL || out == NULL || *out != NULL) {
        detail(diagnostic, capacity, "Invalid TOML arguments or uninitialized parser");
        return MEF_ERR_CONFIG;
    }
    stream = fopen(path, "rb");
    if (stream == NULL) { detail(diagnostic, capacity, "Cannot open TOML"); return MEF_ERR_IO; }
    /* Bounded seekable configuration text, never FITS or a stream/device. */
    if (fseek(stream, 0, SEEK_END) != 0 || (length = ftell(stream)) < 0 ||
        length > 4 * 1024 * 1024 || fseek(stream, 0, SEEK_SET) != 0) {
        fclose(stream); detail(diagnostic, capacity, "TOML size/seek limit"); return MEF_ERR_IO;
    }
    bytes = malloc((size_t)length + 1);
    if (bytes == NULL) { fclose(stream); detail(diagnostic, capacity, "Cannot allocate TOML text"); return MEF_ERR_MEMORY; }
    size_t actual = fread(bytes, 1, (size_t)length + 1, stream);
    int read_error = ferror(stream);
    int close_error = fclose(stream);
    if (actual != (size_t)length || read_error || close_error) {
        free(bytes); detail(diagnostic, capacity, "TOML read failed or size changed"); return MEF_ERR_IO;
    }
    if (!shared_strings(bytes, (size_t)length)) {
        free(bytes); detail(diagnostic, capacity, "Requires TOML 1.0 single-line strings/escapes");
        return MEF_ERR_CONFIG;
    }
    document = malloc(sizeof(*document));
    if (document == NULL) { free(bytes); detail(diagnostic, capacity, "Cannot allocate TOML owner"); return MEF_ERR_MEMORY; }
    document->entries = NULL; document->count = 0; document->capacity = 0;
    document->parsed = toml_parse_named(bytes, (int)length, path);
    free(bytes);
    if (!document->parsed.ok) {
        detail(diagnostic, capacity, document->parsed.errmsg);
        mef_toml_close(document); return MEF_ERR_CONFIG;
    }
    root = document->parsed.toptab;
    for (int i = 0; i < root.u.tab.size; ++i) {
        if (strlen(root.u.tab.key[i]) != (size_t)root.u.tab.len[i]) {
            detail(diagnostic, capacity, "Embedded NUL in TOML root key");
            mef_toml_close(document); return MEF_ERR_CONFIG;
        }
    }
    version = toml_get(root, "schema_version");
    native = toml_get(root, "native");
    if (version.type != TOML_INT64 || (version.u.int64 != 1 && version.u.int64 != 2 && version.u.int64 != 3) ||
        (version.u.int64 != 3 && (native.type != TOML_TABLE || !(native.flag & TOML_FLAG_STDEXPR) ||
        (native.flag & TOML_FLAG_INLINED)))) {
        detail(diagnostic, capacity, "Expected supported schema_version and settings tables");
        mef_toml_close(document); return MEF_ERR_CONFIG;
    }
    document->version = (int)version.u.int64;
    document->includes = toml_get(root, "include");
    document->overrides = toml_get(root, "override_keys");
    for (int i = 0; i < root.u.tab.size; ++i) {
        const char *key = root.u.tab.key[i];
        if (!strcmp(key, "schema_version")) continue;
        if (document->version != 3 && !strcmp(key, "native")) continue;
        if (document->version == 3 && (!strcmp(key, "instrument") || !strcmp(key, "processing") || !strcmp(key, "product"))) continue;
        if (document->version >= 2 && (!strcmp(key, "include") || !strcmp(key, "override_keys"))) continue;
        detail(diagnostic, capacity, "Unknown root key or composition in version 1");
        mef_toml_close(document); return MEF_ERR_CONFIG;
    }
    for (int list = 0; list < 2; ++list) {
        toml_datum_t array = list ? document->overrides : document->includes;
        if (array.type == TOML_UNKNOWN) continue;
        if (array.type != TOML_ARRAY || array.u.arr.size > 64) {
            detail(diagnostic, capacity, "Composition lists must be arrays of at most 64 strings");
            mef_toml_close(document); return MEF_ERR_CONFIG;
        }
        for (int i = 0; i < array.u.arr.size; ++i) {
            toml_datum_t item = array.u.arr.elem[i];
            if (item.type != TOML_STRING || item.u.str.len == 0 ||
                strlen(item.u.str.ptr) != (size_t)item.u.str.len) {
                detail(diagnostic, capacity, "Composition list contains invalid string");
                mef_toml_close(document); return MEF_ERR_CONFIG;
            }
            for (int j = 0; j < i; ++j) {
                if (!strcmp(array.u.arr.elem[j].u.str.ptr, item.u.str.ptr)) {
                    detail(diagnostic, capacity, "Duplicate composition-list entry");
                    mef_toml_close(document); return MEF_ERR_CONFIG;
                }
            }
        }
    }
    /* Keys and strings must have a faithful C string representation. */
    for (int i = 0; document->version != 3 && i < native.u.tab.size; ++i) {
        toml_datum_t value = native.u.tab.value[i];
        if (strlen(native.u.tab.key[i]) != (size_t)native.u.tab.len[i] ||
            (value.type == TOML_STRING && strlen(value.u.str.ptr) != (size_t)value.u.str.len)) {
            detail(diagnostic, capacity, "Embedded NUL in TOML key/string");
            mef_toml_close(document); return MEF_ERR_CONFIG;
        }
    }
    if (document->version == 3) {
        const char *domains[] = {"instrument", "processing", "product"};
        for (size_t i = 0; i < 3; ++i) {
            toml_datum_t table = toml_get(root, domains[i]);
            if (table.type == TOML_UNKNOWN) continue;
            toml_datum_t domain_version = toml_get(table, "schema_version");
            if (table.type != TOML_TABLE || domain_version.type != TOML_INT64 || domain_version.u.int64 != 1) {
                detail(diagnostic, capacity, "Each declared domain requires schema_version=1");
                mef_toml_close(document); return MEF_ERR_CONFIG;
            }
            mef_status status = domain_walk(document, domains[i], table, 1, diagnostic, capacity);
            if (status != MEF_OK) { mef_toml_close(document); return status; }
        }
        for (size_t i = 0; i < mef_toml_override_count(document); ++i) {
            mef_domain_field field;
            if (!mef_domain_from_path(document->overrides.u.arr.elem[i].u.str.ptr, &field)) {
                detail(diagnostic, capacity, "Unknown domain override key");
                mef_toml_close(document); return MEF_ERR_CONFIG;
            }
            strcpy(document->override_native[i], field.native_key);
        }
    }
    document->native = native;
    *out = document;
    return MEF_OK;
}

int mef_toml_version(const mef_toml_document *document) { return document->version; }
const char *mef_toml_key(const mef_toml_document *document, size_t index)
{ return document->version == 3 ? (index < document->count ? document->entries[index].key : NULL)
    : index < (size_t)document->native.u.tab.size ? document->native.u.tab.key[index] : NULL; }
size_t mef_toml_include_count(const mef_toml_document *document)
{ return document->includes.type == TOML_ARRAY ? (size_t)document->includes.u.arr.size : 0; }
const char *mef_toml_include(const mef_toml_document *document, size_t index)
{ return document->includes.u.arr.elem[index].u.str.ptr; }
size_t mef_toml_override_count(const mef_toml_document *document)
{ return document->overrides.type == TOML_ARRAY ? (size_t)document->overrides.u.arr.size : 0; }
const char *mef_toml_override(const mef_toml_document *document, size_t index)
{ return document->version == 3 ? document->override_native[index] : document->overrides.u.arr.elem[index].u.str.ptr; }

size_t mef_toml_count(const mef_toml_document *document)
{
    return document->version == 3 ? document->count : (size_t)document->native.u.tab.size;
}

mef_status mef_toml_get(const mef_toml_document *document, const char *key,
    mef_toml_value *out)
{
    domain_entry *entry = document->version == 3 ? domain_find(document, key) : NULL;
    toml_datum_t value = document->version == 3 ? (entry ? entry->value : (toml_datum_t){0}) : toml_get(document->native, key);
    if (value.type == TOML_STRING) {
        out->kind = MEF_TOML_TEXT; out->text = value.u.str.ptr;
    } else if (value.type == TOML_INT64 && value.u.int64 >= INT_MIN && value.u.int64 <= INT_MAX) {
        out->kind = MEF_TOML_INTEGER; out->integer = (int)value.u.int64;
    } else if (value.type == TOML_FP64 && isfinite(value.u.fp64)) {
        out->kind = MEF_TOML_REAL; out->real = value.u.fp64;
    } else return MEF_ERR_CONFIG;
    return MEF_OK;
}

const char *mef_toml_source_key(const mef_toml_document *document, const char *key)
{
    domain_entry *entry = document->version == 3 ? domain_find(document, key) : NULL;
    return entry ? entry->path : key;
}
int mef_toml_source_line(const mef_toml_document *document, const char *key)
{
    domain_entry *entry = document->version == 3 ? domain_find(document, key) : NULL;
    return entry ? entry->value.lineno : toml_get(document->native, key).lineno;
}
