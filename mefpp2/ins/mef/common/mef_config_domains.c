#include "mef_config_domains.h"
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
typedef struct { const char *native, *path, *storage, *unit, *role; } field;
static const field fields[] = {
#define MEF_DOMAIN(key, path, storage, unit, role) {key, path, storage, unit, role},
#include "mef_config_domains.def"
#undef MEF_DOMAIN
};
/* Match a single positive canonical decimal CHIP ordinal, not an asset ID. */
static int match(const char *text, const char *pattern, int *chip)
{
    int number, digit;
    *chip = 0;
    while (*pattern) {
        if (*pattern != '%') { if (*text++ != *pattern++) return 0; continue; }
        pattern += 2; number = 0;
        if (*text < '1' || *text > '9') return 0;
        while (*text >= '0' && *text <= '9') {
            digit = *text++ - '0';
            if (number > (INT_MAX - digit) / 10) return 0;
            number = 10 * number + digit;
        }
        *chip = number;
    }
    return *text == '\0';
}
static int lookup(const char *text, int native, mef_domain_field *out)
{
    size_t i;
    int chip;
    const field *f;
    if (text == NULL || out == NULL) return 0;
    for (i = 0; i < sizeof(fields) / sizeof(fields[0]); ++i) {
        f = fields + i;
        if (!match(text, native ? f->native : f->path, &chip)) continue;
        /* All format strings are the fixed reviewed catalog, not caller text. */
        if (chip) { sprintf(out->native_key, f->native, chip); sprintf(out->path, f->path, chip); }
        else { strcpy(out->native_key, f->native); strcpy(out->path, f->path); }
        out->storage = f->storage; out->unit = f->unit; out->role = f->role;
        return 1;
    }
    return 0;
}
int mef_domain_from_native(const char *key, mef_domain_field *out) { return lookup(key, 1, out); }
int mef_domain_from_path(const char *path, mef_domain_field *out) { return lookup(path, 0, out); }
int mef_domain_container(const char *path)
{
    char candidate[192];
    mef_domain_field field;
    if (!strcmp(path, "instrument") || !strcmp(path, "processing") || !strcmp(path, "product") ||
        !strcmp(path, "product.header") || !strcmp(path, "product.naming") ||
        !strcmp(path, "instrument.detectors")) return 1;
    if (strlen(path) + 6 >= sizeof(candidate) || strncmp(path, "instrument.detectors.", 21)) return 0;
    strcpy(candidate, path); strcat(candidate, ".gain");
    return mef_domain_from_path(candidate, &field);
}
int mef_domain_catalog_dump(FILE *stream)
{
    size_t i;
    const field *f;
    if (stream == NULL) return 0;
    fputs("{\"domain_schema_version\":1,\"fields\":[\n", stream);
    for (i = 0; i < sizeof(fields) / sizeof(fields[0]); ++i) {
        f = fields + i;
        if (i) fputs(",\n", stream);
        fprintf(stream, "{\"native_pattern\":\"%s\",\"path_pattern\":\"%s\",\"storage\":\"%s\",\"unit\":\"%s\",\"role\":\"%s\"}",
            f->native, f->path, f->storage, f->unit, f->role);
    }
    fputs("\n]}\n", stream); return !ferror(stream);
}
