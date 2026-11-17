#include "mef_flat_stack.h"
#include "mef_config_toml.h"
#include <stdlib.h>
#include <string.h>

static int flat_command(int argc, char **argv, int sky)
{
    mef_recipe_run run;
    mef_flat_stack flat = {.run = &run, .sky = sky};
    int okay = 0;
    if (argc != 5 || strcmp(argv[3], "--config")) {
        fprintf(stderr, "Usage: mefpp_recipe cal %s --config RECIPE.toml\n",
            sky ? "skyff" : "domeff");
        return EXIT_FAILURE;
    }

    mef_recipe_run_initialize(&run, sky ? "cal.skyff" : "cal.domeff",
        sky ? "SKYFF" : "DOMEFF", sky ? "skyff" : "domeff",
        sky ? "Sky flat" : "Dome flat", MEFPP_CANDIDATE_REVISION);
    mef_config_toml_initialize();
    if (!mef_recipe_run_start(&run) || !mef_flat_stack_admit(&flat, argv[4]) ||
        !mef_recipe_run_paths(&run, flat.output, NULL, "CMDP"))
        goto done;

    if (!mef_recipe_run_begin(&run, flat.recipe.path, flat.list_path, NULL, 0))
        goto done;
    okay = mef_flat_stack_process(&flat) && mef_flat_stack_publish(&flat) &&
        mef_recipe_run_complete(&run);
done:
    mef_recipe_run_finish(&run, okay, flat.error, NULL);
    mef_flat_stack_destroy(&flat);
    return okay ? EXIT_SUCCESS : EXIT_FAILURE;
}

int mef_domeff_command(int argc, char **argv)
{
    return flat_command(argc, argv, 0);
}

int mef_skyff_command(int argc, char **argv)
{
    return flat_command(argc, argv, 1);
}
