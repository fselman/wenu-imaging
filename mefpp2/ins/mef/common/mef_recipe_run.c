#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_recipe_run.h"
#include "mefp_lib.h"
#include <fcntl.h>
#include <unistd.h>

void mef_recipe_run_initialize(mef_recipe_run *run, const char *operation, const char *progress_tag,
    const char *workspace_tag, const char *display_name, const char *revision)
{
    memset(run, 0, sizeof(*run));
    run->log_descriptor = -1;
    run->has_final_mef = 1;
    run->operation = operation;
    run->progress_tag = progress_tag;
    run->workspace_tag = workspace_tag;
    run->display_name = display_name;
    run->revision = revision;
}

int mef_recipe_run_start(mef_recipe_run *run)
{
    return !mef_recipe_start_time(
               run->recipe_start, sizeof(run->recipe_start), run->message, sizeof(run->message)) &&
           getcwd(run->invocation_directory, sizeof(run->invocation_directory)) != NULL;
}

int mef_recipe_run_paths(
    mef_recipe_run *run, const char *directory, const char *output, const char *product_class)
{
    size_t i;
    if (mef_product_paths_resolve(run->invocation_directory, directory, output, product_class,
            run->recipe_start, 1, &run->paths, run->message, sizeof(run->message))) {
        return 0;
    }
    {
        const char *name = strrchr(run->paths.fits, '/') + 1;
        if (strlen(name) > 68 || strchr(name, '\'')) {
            strcpy(
                run->message, "Final basename exceeds the existing single-card ORIGFILE contract");
            return 0;
        }
        for (i = 0; name[i]; ++i) {
            if ((unsigned char)name[i] < 32 || (unsigned char)name[i] > 126) {
                strcpy(run->message, "Final FITS basename must use printable ASCII");
                return 0;
            }
        }
    }
    return 1;
}

int mef_recipe_run_begin(mef_recipe_run *run, const char *config_path, const char *listing_path,
    const char *const *raw_paths, size_t frame_count)
{
    size_t i;
    run->log_descriptor = open(run->paths.log, O_WRONLY | O_CREAT | O_EXCL | O_APPEND, 0600);
    if (run->log_descriptor < 0) {
        return 0;
    }
    run->log = fdopen(run->log_descriptor, "a");
    if (run->log == NULL) {
        return 0;
    }
    run->log_descriptor = -1;
    run->has_final_mef = 1;
    fprintf(run->log,
        "RECIPE %s\nSTART %s\nSOURCE %s\nINVOCATION %s\nCONFIG %s\nINPUT_LIST %s\nFITS "
        "%s\nASDF %s\n",
        run->operation, run->recipe_start, run->revision, run->invocation_directory, config_path,
        listing_path, run->paths.fits, run->paths.asdf);
    for (i = 0; i < frame_count; ++i) {
        fprintf(run->log, "INPUT %lu %s\n", (unsigned long)i, raw_paths[i]);
    }
    if (snprintf(run->private_work_directory, sizeof(run->private_work_directory),
            "%s/.mefpp-%s-XXXXXX", run->paths.directory,
            run->workspace_tag) >= (int)sizeof(run->private_work_directory) ||
        mkdtemp(run->private_work_directory) == NULL) {
        run->private_work_directory[0] = '\0';
        return 0;
    }
    fprintf(run->log, "PRIVATE_WORK %s\n", run->private_work_directory);
    if (fflush(run->log)) {
        return 0;
    }
    set_logfilename(run->paths.log);
    set_logfile(1);
    return 1;
}

void mef_recipe_run_discard_temporary(mef_recipe_run *run, const char *path)
{
    if (unlink(path)) {
        fprintf(run->log, "RETAINED_TEMPORARY %s\n", path);
    }
}

int mef_recipe_run_complete(mef_recipe_run *run)
{
    if (rmdir(run->private_work_directory)) {
        fprintf(run->log, "RETAINED_PRIVATE_WORK %s\n", run->private_work_directory);
    }
    fprintf(run->log, "OUTPUTS_WRITTEN; final success requires zero command exit\n");
    if (ferror(run->log)) {
        return 0;
    }
    if (fclose(run->log)) {
        run->log = NULL;
        return 0;
    }
    run->log = NULL;
    printf("%s_RECIPE_COMPLETE\n",run->progress_tag);
    if(run->has_final_mef) printf("FITS %s\nASDF %s\n",run->paths.fits,run->paths.asdf);
    printf("LOG %s\n",run->paths.log);
    return 1;
}

void mef_recipe_run_finish(
    mef_recipe_run *run, int succeeded, const mef_error *error, const char *diagnostic)
{
    set_logfile(0);
    if (!succeeded) {
        if (*run->message) {
            fprintf(stderr, "%s\n", run->message);
        }
        if (error) {
            fprintf(stderr, "%s\n", mef_error_message(error));
        }
        if (diagnostic) {
            fprintf(stderr, "%s\n", diagnostic);
        }
        if (run->log) {
            fprintf(run->log, "FAILED; retain existing outputs and private work %s\n",
                run->private_work_directory);
            fclose(run->log);
            run->log = NULL;
        }
        if (*run->private_work_directory) {
            fprintf(stderr, "Retained private work: %s\n", run->private_work_directory);
        }
        fprintf(stderr, "%s recipe incomplete; no overall success reported.\n", run->display_name);
    }
    if (run->log_descriptor >= 0) {
        close(run->log_descriptor);
    }
}
