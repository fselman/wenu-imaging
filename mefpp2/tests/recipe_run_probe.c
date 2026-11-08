/* Exercise actual shared run services with an empty synthetic input catalogue.
 * Require exclusive logs, unchanged prior files, retained failed work, and clean
 * successful log/workspace finalization. No scientific products are generated.
 */

#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_recipe_run.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static void initialize(mef_recipe_run *run)
{
    mef_recipe_run_initialize(run, "test.run", "TEST", "test", "Test", "synthetic");
    assert(mef_recipe_run_start(run));
}

int main(int argc, char **argv)
{
    mef_recipe_run run, duplicate;
    char output[MEF_PRODUCT_PATH_SIZE], failed_work[MEF_PRODUCT_PATH_SIZE];
    char failed_log[MEF_PRODUCT_PATH_SIZE], line[128];
    FILE *stream;
    struct stat before, after;
    assert(argc == 2);
    assert(snprintf(output, sizeof(output), "%s/complete.fits", argv[1]) < (int)sizeof(output));

    /* Resolve without creating files. Reject filenames incompatible with FITS. */

    initialize(&run);
    assert(!mef_recipe_run_paths(&run, NULL, "bad'quote.fits", "CMDP"));
    assert(mef_recipe_run_paths(&run, NULL, output, "CMDP"));
    assert(access(run.paths.log, F_OK));
    assert(mef_recipe_run_begin(&run, "config", "list", NULL, 0));
    assert(!stat(run.paths.log, &before));
    assert((before.st_mode & 0777) == 0600);
    assert(!access(run.private_work_directory, F_OK));

    /* A competing open must preserve the original log and its contents. */

    initialize(&duplicate);
    duplicate.paths = run.paths;
    assert(!mef_recipe_run_begin(&duplicate, "config", "list", NULL, 0));
    mef_recipe_run_finish(&duplicate, 0, NULL, NULL);
    assert(!stat(run.paths.log, &after));
    assert(before.st_ino == after.st_ino && before.st_size == after.st_size);
    assert(mef_recipe_run_complete(&run));
    assert(run.log == NULL);
    assert(access(run.private_work_directory, F_OK));
    mef_recipe_run_finish(&run, 1, NULL, NULL);
    stream = fopen(run.paths.log, "r");
    assert(stream && fgets(line, sizeof(line), stream));
    assert(!strcmp(line, "RECIPE test.run\n"));
    fclose(stream);
    assert(!unlink(run.paths.log));

    /* Failure reports and retains the private workspace and exclusive log. */

    initialize(&run);
    assert(snprintf(output, sizeof(output), "%s/failed.fits", argv[1]) < (int)sizeof(output));
    assert(mef_recipe_run_paths(&run, NULL, output, "CMDP"));
    assert(mef_recipe_run_begin(&run, "config", "list", NULL, 0));
    strcpy(failed_work, run.private_work_directory);
    strcpy(failed_log, run.paths.log);
    mef_recipe_run_finish(&run, 0, NULL, "synthetic failure");
    assert(run.log == NULL);
    assert(!access(failed_work, F_OK));
    initialize(&duplicate);
    assert(!mef_recipe_run_paths(&duplicate, NULL, output, "CMDP"));
    mef_recipe_run_finish(&duplicate, 1, NULL, NULL);
    assert(!rmdir(failed_work));
    assert(!unlink(failed_log));
    puts("PASS: shared recipe run ownership, exclusive log, no-clobber, failure retention");
    return 0;
}
