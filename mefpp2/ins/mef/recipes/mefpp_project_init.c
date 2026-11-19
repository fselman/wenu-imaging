/* Create the project roots used by the native recipe readers. */
#include "mef_recipe_help.h"
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

enum { path_capacity = 4096 };

static int directory(const char *path)
{
    struct stat info;
    return path && !stat(path, &info) && S_ISDIR(info.st_mode);
}

static int join(char *out, const char *parent, const char *leaf)
{
    int length = snprintf(out, path_capacity, "%s%s%s", parent,
        !strcmp(parent, "/") ? "" : "/", leaf);
    return length > 0 && length < path_capacity;
}

/* Resolve the parent of a new destination so aliases cannot hide overlap. */
static int destination(const char *argument, char *out)
{
    char path[path_capacity];
    size_t length = strlen(argument);
    if (!length || length >= sizeof(path)) {
        return 0;
    }
    memcpy(path, argument, length + 1);
    while (length > 1 && path[length - 1] == '/') {
        path[--length] = '\0';
    }
    char *slash = strrchr(path, '/');
    const char *leaf = slash ? slash + 1 : path;
    if (!*leaf || !strcmp(leaf, ".") || !strcmp(leaf, "..")) {
        return 0;
    }
    const char *parent = ".";
    if (slash == path) {
        parent = "/";
    } else if (slash) {
        *slash = '\0';
        parent = path;
    }
    char *resolved = realpath(parent, NULL);
    int okay = directory(resolved) && join(out, resolved, leaf);
    free(resolved);
    return okay;
}

static int contains(const char *parent, const char *path)
{
    size_t length = strlen(parent);
    return !strcmp(parent, "/") ||
        (!strncmp(parent, path, length) && (!path[length] || path[length] == '/'));
}

static int overlap(const char *first, const char *second)
{
    return contains(first, second) || contains(second, first);
}

/* Reject control characters and escape the TOML basic-string delimiters. */
static int clean_text(const char *text)
{
    if (!*text) {
        return 0;
    }
    for (const unsigned char *p = (const unsigned char *)text; *p; ++p) {
        if (*p < 32 || *p == 127) {
            return 0;
        }
    }
    return 1;
}

static void string_field(FILE *out, const char *key, const char *value)
{
    fprintf(out, "%s = \"", key);
    for (const char *p = value; *p; ++p) {
        if (*p == '\\' || *p == '"') {
            fputc('\\', out);
        }
        fputc(*p, out);
    }
    fputs("\"\n", out);
}

int mef_project_init_command(int argc, char **argv)
{
    static const char *const options[] = {"--name", "--orchestration", "--raw", "--reduced"};
    const char *values[4] = {0};
    if (argc != 11) {
        mef_recipe_operation_help(stderr, "project", "init");
        return EXIT_FAILURE;
    }
    for (int arg = 3; arg < argc; arg += 2) {
        size_t option;
        for (option = 0; option < sizeof(options) / sizeof(*options); ++option) {
            if (!strcmp(argv[arg], options[option])) {
                break;
            }
        }
        if (option == sizeof(options) / sizeof(*options) || values[option] ||
            !clean_text(argv[arg + 1])) {
            fprintf(stderr, "Invalid or repeated project option: %s\n", argv[arg]);
            return EXIT_FAILURE;
        }
        values[option] = argv[arg + 1];
    }

    char orchestration[path_capacity], reduced[path_capacity], project[path_capacity];
    char roots[3][path_capacity];
    char *raw = realpath(values[2], NULL);
    int valid = directory(raw) && strlen(raw) < path_capacity && clean_text(raw) &&
        destination(values[1], orchestration) && destination(values[3], reduced) &&
        clean_text(orchestration) && clean_text(reduced) &&
        !overlap(raw, orchestration) && !overlap(raw, reduced) &&
        !overlap(orchestration, reduced) &&
        join(project, orchestration, "project.toml") &&
        join(roots[0], reduced, "cal") && join(roots[1], reduced, "work") &&
        join(roots[2], reduced, "logs");
    if (!valid) {
        fputs("Project roots must be disjoint directories with existing destination parents.\n",
            stderr);
        free(raw);
        return EXIT_FAILURE;
    }

    /* Claim both destinations exclusively. Only remove entries created here. */
    const char *directories[] = {orchestration, reduced, roots[0], roots[1], roots[2]};
    size_t created = 0;
    int wrote_project = 0;
    const char *target = NULL;
    for (; created < sizeof(directories) / sizeof(*directories); ++created) {
        target = directories[created];
        if (mkdir(target, 0755)) {
            goto failed;
        }
    }
    target = project;
    FILE *out = fopen(project, "wx");
    if (!out) {
        goto failed;
    }
    wrote_project = 1;
    fputs("project_schema_version = 2\n\n[project]\nschema_version = 1\n", out);
    string_field(out, "id", values[0]);
    string_field(out, "name", values[0]);
    fputs("\n[project.roots]\n", out);
    string_field(out, "raw", raw);
    string_field(out, "calibration", roots[0]);
    string_field(out, "output", reduced);
    string_field(out, "work", roots[1]);
    string_field(out, "logs", roots[2]);
    int write_failed = ferror(out);
    if (fclose(out) || write_failed) {
        errno = EIO;
        goto failed;
    }
    printf("PROJECT %s\nORCHESTRATION %s\nREDUCED %s\n", project, orchestration, reduced);
    free(raw);
    return EXIT_SUCCESS;

failed:
    fprintf(stderr, "Cannot initialize project at %s: %s\n", target, strerror(errno));
    if (wrote_project) {
        unlink(project);
    }
    while (created) {
        rmdir(directories[--created]);
    }
    free(raw);
    return EXIT_FAILURE;
}
