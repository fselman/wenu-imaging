/* BPM/linearity coordinator. Read these phases in execution order.
 * Supporting modules expose the mechanics; the typed services own the science.
 * Guide: docs/developer/linearity-preparation-guide-v1.pdf#nameddest=native-recipe
 * Source: docs/developer/linearity-preparation-guide-v1.tex, Native recipe.
 */

#include "mef_bpm_linearity_recipe.h"

int main(int argc, char **argv)
{
    mef_recipe_run run;
    mef_bpm_linearity_recipe recipe;
    size_t detector_index;
    int succeeded = 0;

    mef_recipe_run_initialize(&run, "cal.bpm-linearity", "BPM_LINEARITY",
        "bpm-linearity", "BPM/linearity", MEFPP_CANDIDATE_REVISION);
    mef_bpm_linearity_recipe_initialize(&recipe, &run);

    /* [BPM-LINEARITY-ADMISSION]
     * Sample the start once. Admit the project roots, explicit detector bindings
     * and frozen dependencies before opening products or running a service.
     */

    if (!mef_recipe_run_start(&run) ||
        !mef_bpm_linearity_recipe_prepare(&recipe, argc, argv) ||
        !mef_bpm_linearity_recipe_admit(&recipe) ||
        !mef_bpm_linearity_recipe_begin(&recipe)) {
        goto finish;
    }

    /* [BPM-LINEARITY-DETECTOR-LOOP]
     * Prepare measurements, then characterize the candidate with the same
     * admitted master and prior mask. Never feed the candidate back as a prior.
     */

    for (detector_index = 0; detector_index < recipe.detector_count; ++detector_index) {
        if (!mef_bpm_linearity_recipe_process(&recipe, detector_index)) {
            goto finish;
        }
    }

    /* [BPM-LINEARITY-PUBLICATION]
     * Join complete detector products without changing pixels or measurements.
     * Input preservation is required before a successful completion receipt.
     */

    if (!mef_bpm_linearity_recipe_verify(&recipe) ||
        !mef_bpm_linearity_recipe_publish(&recipe) ||
        !mef_recipe_run_complete(&run)) {
        goto finish;
    }
    succeeded = 1;

finish:

    /* Report while diagnostics are alive, then release in-memory owners.
     * Failed products and private work remain available as evidence.
     */

    if (recipe.show_usage) {
        mef_bpm_linearity_recipe_usage();
    }
    mef_recipe_run_finish(&run, succeeded, NULL, recipe.diagnostic);
    mef_bpm_linearity_recipe_destroy(&recipe);
    return succeeded ? EXIT_SUCCESS : EXIT_FAILURE;
}
