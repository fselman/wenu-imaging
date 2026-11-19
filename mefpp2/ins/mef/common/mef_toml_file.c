/* Read a typed TOML document without applying a configuration schema. */
#define _POSIX_C_SOURCE 200809L

#include "mef_toml_file.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

mef_toml_file mef_toml_file_read(const char *path, size_t max_bytes)
{
    mef_toml_file file = {0};
    struct stat info;
    const char *error = "Missing TOML path";

    if (!path) {
        goto done;
    }
    if (!max_bytes) {
        max_bytes = (size_t)1 << 30;
    }

    error = "Cannot open TOML document";
    file.path = strdup(path);
    FILE *stream = file.path ? fopen(file.path, "rb") : NULL;
    if (!stream) {
        goto done;
    }

    error = "Invalid TOML file size or type";
    if (!fstat(fileno(stream), &info) && S_ISREG(info.st_mode) &&
        info.st_size >= 0 && info.st_size <= INT_MAX &&
        (size_t)info.st_size <= max_bytes) {
        file.length = (size_t)info.st_size;
        file.source = malloc(file.length + 1);
        error = "Cannot read TOML document";
        if (file.source &&
            fread(file.source, 1, file.length, stream) == file.length &&
            fgetc(stream) == EOF && !ferror(stream)) {
            file.source[file.length] = '\0';
            error = memchr(file.source, '\0', file.length)
                ? "NUL byte in TOML document" : NULL;
        }
    }
    if (fclose(stream)) {
        error = "Cannot close TOML document";
    }

done:
    if (error) {
        snprintf(file.parsed.errmsg, sizeof(file.parsed.errmsg), "%s", error);
    } else {
        file.parsed = toml_parse_named(file.source, (int)file.length, file.path);
    }
    return file;
}

void mef_toml_file_destroy(mef_toml_file *file)
{
    toml_free(file->parsed);
    free(file->source);
    free(file->path);
    *file = (mef_toml_file){0};
}
