/* Native project composition: disjoint or identical domains, no replacements.
 * Relative roots and native references belong to the file declaring the domain.
 */
#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_project.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    toml_result_t documents[256];
    char *names[256];
    size_t count;
    const char *active[17];

    struct {
        const char *key;
        toml_datum_t value;
        size_t source;
    } domains[32];

    size_t domain_count, project_source;
    int (*freeze)(void *, const char *);
    void *user;
} project_composition;

static char *relative(const char *source, const char *name)
{
    char base[4096], result[4096];
    const char *slash = strrchr(source, '/');
    int n = slash ? (int)(slash - source) : 0;
    if (!name ||
        snprintf(base, sizeof(base), "%.*s%s%s", name[0] == '/' ? 0 : n, source,
            name[0] == '/' ? "" : "/", name) >= (int)sizeof(base) ||
        !realpath(base, result)) {
        return NULL;
    }
    return strdup(result);
}

static int equal(toml_datum_t a, toml_datum_t b, const char *pa, const char *pb, int paths)
{
    if (a.type != b.type) {
        return 0;
    }
    switch (a.type) {
    case TOML_UNKNOWN:
        return 1;
    case TOML_STRING:
        if (paths) {
            char *x = relative(pa, a.u.s), *y = relative(pb, b.u.s);
            int okay = x && y && !strcmp(x, y);
            free(x);
            free(y);
            return okay;
        }
        return a.u.str.len == b.u.str.len && !memcmp(a.u.s, b.u.s, (size_t)a.u.str.len);
    case TOML_INT64:
        return a.u.int64 == b.u.int64;
    case TOML_FP64:
        return a.u.fp64 == b.u.fp64;
    case TOML_BOOLEAN:
        return a.u.boolean == b.u.boolean;
    case TOML_ARRAY:
        if (a.u.arr.size != b.u.arr.size) {
            return 0;
        }
        for (int i = 0; i < a.u.arr.size; ++i) {
            if (!equal(a.u.arr.elem[i], b.u.arr.elem[i], pa, pb, paths)) {
                return 0;
            }
        }
        return 1;
    case TOML_TABLE:
        if (a.u.tab.size != b.u.tab.size) {
            return 0;
        }
        for (int i = 0; i < a.u.tab.size; ++i) {
            const char *key = a.u.tab.key[i];
            if (!equal(a.u.tab.value[i], toml_get(b, key), pa, pb,
                    paths || !strcmp(key, "roots") || !strcmp(key, "native_configuration"))) {
                return 0;
            }
        }
        return 1;
    default:
        return 0;
    }
}

static int visit(project_composition *c, const char *name, int depth)
{
    size_t index;
    if (depth > 16) {
        return 0;
    }
    for (int i = 0; i < depth; ++i) {
        if (!strcmp(c->active[i], name)) {
            return 0;
        }
    }
    for (index = 0; index < c->count; ++index) {
        if (!strcmp(c->names[index], name)) {
            return 1;
        }
    }
    if (c->count == 256 || (c->freeze && !c->freeze(c->user, name))) {
        return 0;
    }
    index = c->count++;
    c->names[index] = strdup(name);
    c->documents[index] = toml_parse_file_ex(name);
    if (!c->names[index] || !c->documents[index].ok) {
        return 0;
    }
    toml_datum_t root = c->documents[index].toptab,
                 version = toml_get(root, "project_schema_version"),
                 includes = toml_get(root, "include");
    if (version.type != TOML_INT64 || (version.u.int64 != 1 && version.u.int64 != 2) ||
        (depth && version.u.int64 != 2) ||
        (version.u.int64 == 1 && includes.type != TOML_UNKNOWN) ||
        (includes.type != TOML_UNKNOWN && includes.type != TOML_ARRAY) ||
        (includes.type == TOML_ARRAY && includes.u.arr.size > 64)) {
        return 0;
    }
    c->active[depth] = name;
    if (includes.type == TOML_ARRAY) {
        for (int i = 0; i < includes.u.arr.size; ++i) {
            toml_datum_t item = includes.u.arr.elem[i];
            if (item.type != TOML_STRING) {
                return 0;
            }
            for (int j = 0; j < i; ++j) {
                if (!strcmp(item.u.s, includes.u.arr.elem[j].u.s)) {
                    return 0;
                }
            }
            char *child = relative(name, item.u.s);
            int okay = child && visit(c, child, depth + 1);
            free(child);
            if (!okay) {
                return 0;
            }
        }
    }
    for (int i = 0; i < root.u.tab.size; ++i) {
        const char *key = root.u.tab.key[i];
        if (!strcmp(key, "include") || !strcmp(key, "project_schema_version")) {
            continue;
        }
        const char *known = "|project|association|reduction_profile|recipe|execution|quality|"
                            "product_profile|processing|readout|";
        char token[96];
        if (snprintf(token, sizeof(token), "|%s|", key) >= (int)sizeof(token) ||
            !strstr(known, token)) {
            return 0;
        }
        size_t found;
        for (found = 0; found < c->domain_count; ++found) {
            if (!strcmp(c->domains[found].key, key)) {
                break;
            }
        }
        if (found < c->domain_count) {
            if (!equal(c->domains[found].value, root.u.tab.value[i],
                    c->names[c->domains[found].source], name, 0)) {
                return 0;
            }
        } else {
            if (c->domain_count == 32) {
                return 0;
            }
            c->domains[found].key = key;
            c->domains[found].value = root.u.tab.value[i];
            c->domains[found].source = index;
            if (!strcmp(key, "project")) {
                c->project_source = index;
            }
            ++c->domain_count;
        }
    }
    return 1;
}

int mef_project_read(const char *path, toml_result_t *out, char **origin,
    int (*freeze)(void *, const char *), void *user)
{
    project_composition *c = calloc(1, sizeof(*c));
    int okay = 0;
    if (!c) {
        return 0;
    }
    c->project_source = 256;
    c->freeze = freeze;
    c->user = user;
    if (!visit(c, path, 0) || c->project_source == 256) {
        goto done;
    }
    *origin = strdup(c->names[c->project_source]);
    if (!*origin) {
        goto done;
    }
    *out = c->documents[c->project_source];
    memset(c->documents + c->project_source, 0, sizeof(*out));
    okay = 1;
done:
    for (size_t i = 0; i < c->count; ++i) {
        toml_free(c->documents[i]);
        free(c->names[i]);
    }
    free(c);
    return okay;
}
