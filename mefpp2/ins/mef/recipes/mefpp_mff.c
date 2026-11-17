/* Combine supplied flat masters. The detector loop keeps one pair resident. */
#include "mef_mff.h"
#include "mef_config_toml.h"
#include <stdlib.h>
#include <string.h>

int mef_mff_command(int argc, char **argv)
{
    mef_recipe_run run;
    mef_mff mff = {.run = &run};
    int okay = 0;

    mef_recipe_run_initialize(&run, "cal.mff", "MFF", "mff", "Master flat",
        MEFPP_CANDIDATE_REVISION);
    if (argc != 5 || strcmp(argv[3], "--config")) {
        fputs("Usage: mefpp_recipe cal mff --config RECIPE.toml\n", stderr);
        return EXIT_FAILURE;
    }

    /* [MFF-ADMIT] Every master and detector binding is checked before output. */
    mef_config_toml_initialize();
    if (!mef_recipe_run_start(&run) || !mef_mff_admit(&mff, argv[4]) ||
        !mef_recipe_run_paths(&run, mff.output, NULL, "CMDP"))
        goto done;

    const char *inputs[] = {mff.components[MFF_DOME].path, mff.components[MFF_SKY].path,
        mff.components[MFF_BPM].path};
    if (!mef_recipe_run_begin(&run, mff.recipe.path, "supplied masters",
            inputs, inputs[2] ? 3 : 2))
        goto done;
    for (size_t i = 0; i < mff.detector_count; ++i) {
        if (!mef_mff_process(&mff, i))
            goto done;
    }
    okay = mef_mff_inputs_unchanged(&mff) && mef_mff_publish(&mff) &&
           mef_recipe_run_complete(&run);
done:
    mef_recipe_run_finish(&run, okay, mff.error, NULL);
    mef_mff_destroy(&mff);
    return okay ? EXIT_SUCCESS : EXIT_FAILURE;
}
