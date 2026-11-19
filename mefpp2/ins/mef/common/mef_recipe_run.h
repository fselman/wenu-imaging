/* Shared serial recipe run resources. See GitHub issue #292. */

#ifndef MEF_RECIPE_RUN_H
#define MEF_RECIPE_RUN_H
#include "mef_product_paths.h"
#include "mef_runtime.h"
#include <stdio.h>

/* Identity strings are borrowed. Initialize before any phase; finish once.
 * This owner manages logs and workspace, not scientific results or QC policy. */

typedef struct {
    mef_product_paths paths;
    char recipe_start[MEF_RECIPE_TIME_SIZE];
    char invocation_directory[MEF_PRODUCT_PATH_SIZE];
    char private_work_directory[MEF_PRODUCT_PATH_SIZE];
    char message[512];
    const char *operation, *progress_tag, *workspace_tag, *display_name, *revision;
    FILE *log;
    int log_descriptor, has_final_mef;
} mef_recipe_run;

void mef_recipe_run_initialize(
    mef_recipe_run *, const char *, const char *, const char *, const char *, const char *);
int mef_recipe_run_start(mef_recipe_run *);
int mef_recipe_run_paths(mef_recipe_run *, const char *, const char *, const char *);
int mef_recipe_run_begin(mef_recipe_run *, const char *, const char *, const char *const *, size_t);
void mef_recipe_run_discard_temporary(mef_recipe_run *, const char *);
int mef_recipe_run_complete(mef_recipe_run *);
void mef_recipe_run_finish(mef_recipe_run *, int, const mef_error *, const char *);
#endif
