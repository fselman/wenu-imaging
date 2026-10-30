/* I/O adaptation only: no cwd changes, list staging or scientific defaults. */
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <errno.h>
#include "mefp_lib.h"
#include "mef_paths.h"

struct mef_paths {
    char invocation[FILENAMESZ];
    char output[FILENAMESZ];
    char work[FILENAMESZ];
    char member_base[FILENAMESZ];
    char log[FILENAMESZ];
    char **outputs;
    size_t output_count;
};

static char *resolve(const char *base, const char *name)
{
    char joined[PATH_MAX], canonical[PATH_MAX];
    if (name == NULL || *name == '\0') return NULL;
    if (strlen(name) + (base ? strlen(base) : 0) + 2 >= sizeof(joined)) return NULL;
    if (name[0] == '/') strcpy(joined, name);
    else {
        if (base == NULL || base[0] != '/') {
            e_error("relative input has no explicit --list-base: %s", name);
            return NULL;
        }
        sprintf(joined, "%s/%s", base, name);
    }
    if (realpath(joined, canonical) == NULL || strlen(canonical) >= FILENAMESZ - 40) {
        e_error("cannot resolve input or path exceeds supported length: %s", joined);
        return NULL;
    }
    return strdup(canonical);
}

static int directory(char *target, const char *base, const char *name)
{
    char *resolved;
    struct stat st;
    resolved = resolve(base, name);
    if (resolved == NULL) return -1;
    if (stat(resolved, &st) != 0 || !S_ISDIR(st.st_mode) ||
        (st.st_mode & 0222) == 0 || access(resolved, W_OK | X_OK) != 0) {
        e_error("expected an existing writable directory: %s", resolved);
        free(resolved); return -1;
    }
    strcpy(target, resolved); free(resolved); return 0;
}

static int record(const mef_paths *paths, const char *role, const char *path)
{
    FILE *stream;
    int failed;
    if (paths == NULL) return 0;
    stream = fopen(paths->log, "a");
    if (stream == NULL) return -1;
    failed = fprintf(stream, "PATH %s %s\n", role, path) < 0;
    if (fclose(stream) != 0) failed = 1;
    return failed ? -1 : 0;
}

mef_paths *mef_paths_new(const char *output, const char *work,
    const char *members, const char *log)
{
    mef_paths *paths;
    char *resolved;
    struct stat st;
    int fd;
    paths = calloc(1, sizeof(*paths));
    if (paths == NULL) return NULL;
    if (getcwd(paths->invocation, sizeof(paths->invocation)) == NULL ||
        directory(paths->output, paths->invocation, output) != 0 ||
        directory(paths->work, paths->invocation, work) != 0) goto fail;
    if (members != NULL) {
        resolved = resolve(paths->invocation, members);
        if (resolved == NULL) goto fail;
        if (stat(resolved, &st) != 0 || !S_ISDIR(st.st_mode)) {
            free(resolved); goto fail;
        }
        strcpy(paths->member_base, resolved); free(resolved);
    }
    /* A fresh log is explicit evidence; never overwrite a prior attempt. */
    if (log != NULL) {
        if (log[0] == '/') {
            if (strlen(log) >= sizeof(paths->log)) goto fail;
            strcpy(paths->log, log);
        } else {
            if (strlen(paths->invocation) + strlen(log) + 2 >= sizeof(paths->log)) goto fail;
            if (snprintf(paths->log, sizeof(paths->log), "%s/%s", paths->invocation, log) >= (int)sizeof(paths->log)) goto fail;
        }
    } else if (snprintf(paths->log, sizeof(paths->log), "%s/mefpp.log", paths->work) >= (int)sizeof(paths->log)) goto fail;
    fd = open(paths->log, O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) { e_error("cannot create fresh explicit log: %s", paths->log); goto fail; }
    if (close(fd) != 0) goto fail;
    if (record(paths, "invocation", paths->invocation) != 0 ||
        record(paths, "output", paths->output) != 0 ||
        record(paths, "work", paths->work) != 0) goto fail;
    if (*paths->member_base && record(paths, "list-base", paths->member_base) != 0) goto fail;
    set_logfilename(paths->log); set_logfile(1);
    return paths;
fail:
    free(paths); return NULL;
}

void mef_paths_del(mef_paths *paths)
{
    size_t i;
    if (paths == NULL) return;
    for (i = 0; i < paths->output_count; ++i) free(paths->outputs[i]);
    free(paths->outputs); free(paths);
}
const char *mef_paths_work(const mef_paths *paths) { return paths->work; }

static int readable(const char *path)
{
    struct stat st;
    return stat(path, &st) == 0 && S_ISREG(st.st_mode) && access(path, R_OK) == 0;
}

framelist *mef_paths_frames(const mef_paths *paths, char *name)
{
    framelist *frames;
    charmatrix *table;
    const char *type;
    FILE *stream;
    char *resolved;
    size_t length, bytes;
    int ch, i;
    if (paths == NULL) return framelist_load(name);
    if (name == NULL || !readable(name) || is_fits_file(name)) return NULL;
    stream = fopen(name, "rb");
    if (stream == NULL) return NULL;
    length = bytes = 0;
    while ((ch = fgetc(stream)) != EOF) {
        if (++bytes > 16 * 1024 * 1024 || ch == 0 || ch == '\r' || (ch != '\n' && ++length >= 1023)) {
            fclose(stream); e_error("unsupported legacy list line: %s", name); return NULL;
        }
        if (ch == '\n') length = 0;
    }
    if (ferror(stream)) { fclose(stream); return NULL; }
    if (fclose(stream) != 0) return NULL;
    /* framelist_load validates member existence against cwd before returning.
     * Reuse its authoritative tokenizer, then resolve before that validation. */
    table = charmatrix_read(name);
    if (table == NULL) return NULL;
    if (table->ly > 100000) { charmatrix_del(table); return NULL; }
    frames = framelist_new(table->ly);
    if (frames == NULL) { charmatrix_del(table); return NULL; }
    frames->filename = strdup(name);
    if (frames->filename == NULL) { charmatrix_del(table); framelist_del(frames); return NULL; }
    if (table->lx < 2) {
        free(frames->type); frames->type = NULL;
    }
    for (i = 0; i < frames->n; ++i) {
        resolved = resolve(*paths->member_base ? paths->member_base : NULL,
                           charmatrix_elem(table, 0, i));
        if (resolved == NULL || !readable(resolved)) {
            free(resolved); charmatrix_del(table); framelist_del(frames); return NULL;
        }
        frames->name[i] = resolved;
        if (frames->type != NULL) {
            type = charmatrix_elem(table, 1, i);
            if (type != NULL) {
                frames->type[i] = strdup(strlwc((char *)type));
                if (frames->type[i] == NULL) { charmatrix_del(table); framelist_del(frames); return NULL; }
            }
        }
        if (record(paths, "member", resolved) != 0) {
            charmatrix_del(table); framelist_del(frames); return NULL;
        }
    }
    charmatrix_del(table);
    return frames;
}

char *mef_paths_first(const mef_paths *paths, char *name)
{
    framelist *frames;
    char *first;
    if (name == NULL) return NULL;
    if (is_fits_file(name)) return strdup(name);
    frames = mef_paths_frames(paths, name);
    if (frames == NULL || frames->n < 1) { framelist_del(frames); return NULL; }
    first = is_fits_file(frames->name[0]) ? strdup(frames->name[0]) : NULL;
    framelist_del(frames); return first;
}

int mef_paths_bind(struct _mef_bb_ *bb)
{
    char **slots[8], *resolved;
    framelist *frames;
    int i;
    slots[0] = &bb->name_paf; slots[1] = &bb->name_bias; slots[2] = &bb->name_bpm;
    slots[3] = &bb->name_dome; slots[4] = &bb->name_sky; slots[5] = &bb->name_mf;
    slots[6] = &bb->science_name_i; slots[7] = &bb->name_split;
    for (i = 0; i < 8; ++i) {
        if (*slots[i] == NULL) continue;
        resolved = resolve(bb->paths->invocation, *slots[i]);
        if (resolved == NULL || !readable(resolved)) { free(resolved); return -1; }
        free(*slots[i]); *slots[i] = resolved;
        if (record(bb->paths, "argument", resolved) != 0) return -1;
        if (i != 0 && !is_fits_file(resolved)) {
            frames = mef_paths_frames(bb->paths, resolved);
            if (frames == NULL) return -1;
            framelist_del(frames);
        }
    }
    return 0;
}

char *mef_paths_output(const mef_paths *paths, const char *leaf)
{
    char *result;
    size_t n;
    if (paths == NULL) return strdup(leaf);
    if (leaf == NULL || *leaf == '\0' || strchr(leaf, '/') != NULL || !strcmp(leaf, ".") || !strcmp(leaf, "..")) {
        e_error("explicit output names must be local names under --output-dir"); return NULL;
    }
    n = strlen(paths->output) + strlen(leaf) + 2;
    if (n >= FILENAMESZ - 40) { e_error("output path too long"); return NULL; }
    result = malloc(n);
    if (result != NULL) sprintf(result, "%s/%s", paths->output, leaf);
    return result;
}

static int reserve(mef_paths *paths, const char *path)
{
    struct stat st;
    char **grown;
    size_t i;
    if (path == NULL) return -1;
    for (i = 0; i < paths->output_count; ++i) if (!strcmp(paths->outputs[i], path)) {
        e_error("duplicate output destination: %s", path); return -1;
    }
    if (lstat(path, &st) == 0 || errno != ENOENT) {
        e_error("refusing existing or inaccessible output: %s", path); return -1;
    }
    grown = realloc(paths->outputs, (paths->output_count + 1) * sizeof(*grown));
    if (grown == NULL) return -1;
    paths->outputs = grown;
    grown[paths->output_count] = strdup(path);
    if (grown[paths->output_count] == NULL) return -1;
    ++paths->output_count;
    return record(paths, "planned-output", path);
}

int mef_paths_split_preflight(struct _mef_bb_ *bb, framelist *frames)
{
    int i, k, n;
    char leaf[FILENAMESZ], *path;
    if (bb->paths == NULL) return 0;
    for (i = 0; i < frames->n; ++i) {
        n = qfits_query_n_ext(frames->name[i]);
        if (n < 1) return -1;
        for (k = 1; k <= n; ++k) {
            if (strlen(get_basename(frames->name[i])) + 20 >= sizeof(leaf)) return -1;
            sprintf(leaf, "%s_%02d.fits", get_rootname(get_basename(frames->name[i])), k);
            path = mef_paths_output(bb->paths, leaf);
            if (reserve(bb->paths, path) != 0) { free(path); return -1; }
            free(path);
        }
    }
    return 0;
}

static int calibration_geometry(struct _mef_bb_ *bb)
{
    const char *names[5];
    qfits_header *header;
    int i, xt, first, last, width, height;
    names[0] = bb->name_bias; names[1] = bb->name_bpm; names[2] = bb->name_mf;
    names[3] = bb->name_dome; names[4] = bb->name_sky;
    first = bb->xtnum > 0 ? bb->xtnum : 1;
    last = bb->xtnum > 0 ? bb->xtnum : bb->nchips;
    if (first < 1 || last > bb->nchips) return -1;
    for (i = 0; i < 5; ++i) {
        if (names[i] == NULL || !is_fits_file((char *)names[i])) continue;
        for (xt = first; xt <= last; ++xt) {
            header = qfits_header_readext(names[i], xt);
            if (header == NULL) return -1;
            width = bb->ccd[xt - 1].trimreg[1] - bb->ccd[xt - 1].trimreg[0] + 1;
            height = bb->ccd[xt - 1].trimreg[3] - bb->ccd[xt - 1].trimreg[2] + 1;
            if (qfits_header_getint(header, "NAXIS1", -1) != width ||
                qfits_header_getint(header, "NAXIS2", -1) != height) {
                qfits_header_destroy(header);
                e_error("calibration geometry differs from configured crop: %s HDU %d", names[i], xt);
                return -1;
            }
            qfits_header_destroy(header);
        }
    }
    return 0;
}

int mef_paths_finish(const mef_paths *paths)
{
    char current[FILENAMESZ];
    if (paths == NULL) return 0;
    if (getcwd(current, sizeof(current)) == NULL || strcmp(current, paths->invocation)) {
        e_error("processing changed the invocation directory"); return -1;
    }
    return record(paths, "final-cwd", current);
}

int mef_paths_preflight(struct _mef_bb_ *bb)
{
    const char *roles[] = {"bias", "dome", "sky", "combined", "bpm"};
    int selected[5], i;
    char leaf[FILENAMESZ], *path;
    framelist *frames;
    if (bb->paths == NULL) return 0;
    if (calibration_geometry(bb) != 0) return -1;
    selected[0] = bb->bias_save; selected[1] = bb->dome_save;
    selected[2] = bb->sky_save; selected[3] = bb->name_mf_o != NULL && bb->name_sky != NULL;
    selected[4] = bb->name_bpm != NULL && !is_fits_file(bb->name_bpm);
    for (i = 0; i < 5; ++i) if (selected[i]) {
        path = mef_get_output_filename(bb, (char *)roles[i]);
        if (reserve(bb->paths, path) != 0) { free(path); return -1; }
        free(path);
    }
    if (bb->science_name_i == NULL) return 0;
    frames = mef_paths_frames(bb->paths, bb->science_name_i);
    if (frames == NULL) {
        if (!is_fits_file(bb->science_name_i)) return -1;
        frames = framelist_new(1);
        if (frames == NULL) return -1;
        frames->name[0] = strdup(bb->science_name_i);
        if (frames->name[0] == NULL) { framelist_del(frames); return -1; }
    }
    for (i = 0; i < frames->n; ++i) {
        if (strlen(get_basename(frames->name[i])) + 20 >= sizeof(leaf)) { framelist_del(frames); return -1; }
        sprintf(leaf, "%s_pre.fits", get_rootname(get_basename(frames->name[i])));
        path = mef_paths_output(bb->paths, leaf);
        if (reserve(bb->paths, path) != 0) { free(path); framelist_del(frames); return -1; }
        free(path);
    }
    framelist_del(frames); return 0;
}
