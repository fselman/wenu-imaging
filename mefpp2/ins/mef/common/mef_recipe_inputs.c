#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_recipe_inputs.h"
#include "qfits.h"
#include <ctype.h>
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

void mef_recipe_inputs_destroy(mef_recipe_inputs *list)
{
    if (!list) {
        return;
    }
    for (size_t i = 0; i < list->count; ++i) {
        free(list->rows[i].path);
        free(list->rows[i].dpr_type);
    }
    free(list->rows);
    memset(list, 0, sizeof(*list));
}

int mef_recipe_inputs_read(const char *name, const char *raw, int legacy, mef_recipe_inputs *list,
    char *error, size_t capacity)
{
    FILE *stream = fopen(name, "rb");
    char *line = NULL;
    size_t length = 0, number = 0;
    int okay = 0;
    const char *requirement = "require path and DPR.TYPE, unique existing files";
    if (!stream || !list || list->rows) {
        goto done;
    }
    ssize_t bytes;
    while ((bytes = getline(&line, &length, stream)) >= 0) {
        if (memchr(line, 0, (size_t)bytes)) {
            goto done;
        }
        ++number;
        char *start = line;
        while (isspace((unsigned char)*start)) {
            ++start;
        }
        if (!*start || *start == '#') {
            continue;
        }
        char *end = start + strlen(start);
        while (end > start && isspace((unsigned char)end[-1])) {
            --end;
        }
        *end = 0;
        char *type = strchr(start, '\t');
        if (!type) {
            type = start;
            while (*type && !isspace((unsigned char)*type)) {
                ++type;
            }
        }
        if (*type) {
            *type++ = 0;
            while (isspace((unsigned char)*type)) {
                ++type;
            }
        }
        if ((!*type && !legacy) || strpbrk(type, "\t\r\n ") || list->count == 100000) {
            goto done;
        }
        if (!legacy && start[0] != '/') {
            requirement = "observation path must be absolute";
            goto done;
        }
        char absolute[4096];
        if (snprintf(absolute, sizeof(absolute), "%s%s%s", start[0] == '/' ? "" : raw,
                start[0] == '/' ? "" : "/", start) >= (int)sizeof(absolute)) {
            goto done;
        }
        char *resolved = realpath(absolute, NULL);
        if (!resolved) {
            goto done;
        }
        /* Explicit DPR.TYPE labels must agree with available primary metadata.
         * Non-ESO inputs may supply classification solely in the list. */
        if (!legacy) {
            char *declared = qfits_query_ext(resolved, "HIERARCH ESO DPR TYPE", 0);
            if (!declared) {
                declared = qfits_query_ext(resolved, "DPR.TYPE", 0);
            }
            if (declared && strcmp(qfits_pretty_string(declared), type)) {
                free(resolved);
                goto done;
            }
        }
        for (size_t i = 0; i < list->count; ++i) {
            if (!strcmp(resolved, list->rows[i].path)) {
                free(resolved);
                goto done;
            }
        }
        mef_recipe_input *next = realloc(list->rows, (list->count + 1) * sizeof(*next));
        if (!next) {
            free(resolved);
            goto done;
        }
        list->rows = next;
        mef_recipe_input *row = list->rows + list->count++;
        *row = (mef_recipe_input){resolved, strdup(*type ? type : "BIAS"), list->count - 1, -1, 0};
        if (!row->dpr_type) {
            goto done;
        }
    }
    okay = !ferror(stream) && list->count > 0;
done:
    if (stream) {
        fclose(stream);
    }
    free(line);
    if (!okay) {
        if (error && capacity) {
            snprintf(error, capacity,
                "Invalid observation list %s at line %zu: %s", name, number, requirement);
        }
        mef_recipe_inputs_destroy(list);
    }
    return okay;
}

int mef_recipe_inputs_pair(mef_recipe_inputs *list, const char *key, int hdu, double tolerance,
    char *error, size_t capacity)
{
    int next_pair = 0;
    if (!list || !key || hdu < 0 || !isfinite(tolerance) || tolerance < 0) {
        return 0;
    }
    for (size_t i = 0; i < list->count; ++i) {
        mef_recipe_input *row = list->rows + i;
        if (strncmp(row->dpr_type, "FLAT", 4) || (row->dpr_type[4] && row->dpr_type[4] != ',')) {
            continue;
        }
        const char *value = qfits_query_ext(row->path, key, hdu);
        char *end;
        errno = 0;
        if (!value) {
            goto failed;
        }
        row->seconds = strtod(value, &end);
        while (isspace((unsigned char)*end)) {
            ++end;
        }
        if (errno || end == value || *end || !isfinite(row->seconds) || row->seconds <= 0) {
            goto failed;
        }
    }
    for (size_t i = 0; i < list->count; ++i) {
        mef_recipe_input *row = list->rows + i;
        if (row->seconds <= 0) {
            continue;
        }
        size_t partner = 0, matches = 0;
        for (size_t j = 0; j < list->count; ++j) {
            if (j != i && list->rows[j].seconds > 0 &&
                !strcmp(row->dpr_type, list->rows[j].dpr_type) &&
                fabs(row->seconds - list->rows[j].seconds) <= tolerance) {
                partner = j;
                ++matches;
            }
        }
        if (matches != 1) {
            goto failed;
        }
        if (row->pair < 0) {
            row->pair = next_pair;
            list->rows[partner].pair = next_pair++;
        }
    }
    return next_pair > 0;
failed:
    if (error && capacity) {
        snprintf(error, capacity,
            "Flat pairing requires exactly two members of each DPR.TYPE/exposure group within "
            "%.17g s; missing, ambiguous or invalid exposure",
            tolerance);
    }
    return 0;
}
